# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.db.transaction import atomic
from django.views.generic import View
from django.utils.timezone import now
from django.http import JsonResponse
from collections import defaultdict
from django.db.models import Count
from app.rhea.models import *
from random import choice
from time import mktime
from json import loads


__all__ = ['gathering']

cdef class CourseGroup:

	cdef public object subject
	cdef public object instructor
	cdef list _courses
	cdef list _students

	def __cinit__(CourseGroup self, object subject, object instructor):

		self.subject = subject
		self.instructor = instructor
		self._courses = [ course for course in instructor.schedule.entries.all().filter(subject_id = subject.id).annotate(count = Count('schedule__student')) ]
		self._students = list({ student for student in Student.objects.active(schedule__entries__subject_id = subject.id, schedule__entries__instructor_id = instructor.id) })

	property population:
		def __get__(CourseGroup self): return len(self._students)
	property days:
		def __get__(CourseGroup self):
			return [ course.day for course in self._courses ]
	property time:
		def __get__(CourseGroup self):

			cdef int time = 0
			for course in self._courses:
				if time != course.time:
					time = course.time

			return time

	cdef clear(CourseGroup self):

		for student in self._students:
			student.schedule.entries.remove(*self._courses)

		for course in self._courses:
			course.delete(soft = True)
	cdef void add(CourseGroup self, object student):

		if student not in self._students:

			student.schedule.entries.add(*self._courses)
			self._students.append(student)
	cdef object evict(CourseGroup self):

		cdef object student = self._students.pop(0)
		student.schedule.entries.remove(*self._courses)

		return student

	def __repr__(CourseGroup self): return '<%s @ %s, pop: %s>' % (self.days, self.time, self.population)

cdef tuple cleanse(object subjects):

	cdef list output = [], days = None
	cdef CourseGroup group = None
	cdef Py_ssize_t time = 0, count = 0

	# Exclude all courses without students by destroying them
	for groups in subjects.itervalues():
		for group in groups:

			if group.population == 0: group.clear()
			else:

				days = group.days
				time = group.time
				count += 1

				output.append({
					'instructor': { 'id': group.instructor.user_id, 'name': group.instructor.full_name },
					'subject': { 'code': group.subject.code, 'name': group.subject.name },
					'slots': [ { 'day': day, 'time': time } for day in days ]
				})

	return output, count
cdef object redistribute(object subjects):

	cdef CourseGroup group = None, other = None
	cdef Py_ssize_t count = 0, population = 0

	with atomic():

		for (subject, groups) in subjects.iteritems():
			for group in groups:

				# If less than the limit, we should redistribute the students
				population = group.population
				if population < 15:

					# Only perform if this is a possibility - if the remaining slots in other groups are enough
					count = sum([ 36 - g.population for g in groups if g is not group ])
					if population <= count:
						while population > 0:

							other = choice(groups)
							if other is group or other.population + 1 >= 36:

								other.add(group.evict())
								population -= 1

	return subjects
cdef object group_courses():

	cdef object subjects = defaultdict(list)
	for instructor in Instructor.objects.active():

		for subject in instructor.subjects.all().annotate(count = Count('courses')).filter(count__gt = 0):
			subjects[subject.id].append(CourseGroup(subject, instructor))

	return subjects

class ScheduleGatheringView(View):

	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def post(self, request):

		start = now()
		with atomic():

			# Run the process iterations - which are in C - sequentially
			total = Course.objects.active().count()
			courses, count = cleanse(redistribute(group_courses()))
			remaining = Course.objects.active().count()

			# Serialize information & return data
			end = now()
			return JsonResponse({
				'version': '0.1.0',
				'status': 200,
				'stats': {
					'total': count,
					'coverage': remaining / total,
					'elapsed': (end - start).microseconds,
					'start': mktime(start.utctimetuple())
				},
				'courses': courses
			})
gathering = cache_page(3600)(ScheduleGatheringView.as_view())
