# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from dateutil.relativedelta import relativedelta as timedelta
from django.contrib.auth.decorators import login_required
from jsonschema import Draft4Validator, ValidationError
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.core.management import call_command
from app.rhea.tokens import StudentTokenFactory
from django.db.transaction import atomic
from StringIO import StringIO as strio
from django.views.generic import View
from django.utils.timezone import now
from django.http import JsonResponse
from collections import defaultdict
from django.db.models import Count
from app.rhea.models import *
from time import mktime
from json import loads


__all__ = [ 'select', 'predict' ]

class ScheduleSelectView(View):

	schema = Draft4Validator({
		'$schema': 'http://json-schema.org/draft-04/schema#',
		'type': 'object',
		'properties': {
			'courses': {
				'type': 'array',
				'minItems': 1,
				'uniqueItems': True,
				'items': {
					'type': 'object',
					'properties': {
						'code': { 'type': 'string', 'minLength': 1 },
						'instructor': { 'type': 'string', 'minLength': 1 },
						'day': {
							'type': 'integer',
							'multipleOf': 1,
							'maximum': 4,
							'minimum': 0,
							'exclusiveMaximum': False,
							'exclusiveMinimum': False
						},
						'time': {
							'type': 'integer',
							'multipleOf': 1,
							'maximum': 9,
							'minimum': 0,
							'exclusiveMaximum': False,
							'exclusiveMinimum': False
						}
					},
					'required': [ 'code', 'instructor', 'day', 'time' ]
				}
			}
		},
		'required': [ 'courses' ]
	})

	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def get(self, request, token = False):

		tokens = StudentTokenFactory(timeout_days = 5)
		try:

			student = Student.objects.get(id = request.user.id)

			if token is not False:

				# Validate the token first
				if tokens.check_token(student, token) is False:
					return JsonResponse({ 'version': '0.1.0', 'status': 409 }, status = 409)

				# Having a token means we're querying the current state
				with atomic():

					start = now()
					students = Student.objects.active()

					total = students.count()
					remaining = students.filter(last_confirmation__isnull = True)
					end = now()

					return JsonResponse({
						'version': '0.1.0',
						'status': 200,
						'token': token,
						'execution': {
							'stats': {
								'coverage': (remaining.count() / total),
								'start': mktime(start.utctimetuple()),
								'elapsed': (end - start).total_seconds() * 1000000
							},
							'pending': [
								{
									'id': student.user_id,
									'name': student.full_name,
									'last-login': student.last_login
								} for student in remaining
							]
						}
					})
			else:

				# Run the command and capture results
				# TODO: Make this self-scheduling later on... for now, we'll leave it as a single swipe
				stdout = strio()
				call_command('runtask', args = [ 'email_students' ], stdout = stdout)
				response = loads(stdout.getvalue().strip())

				# Serialize data and return
				return JsonResponse({
					'version': '0.1.0',
					'status': 200,
					'token': tokens.make_token(student),
					'execution': response
				})

		except Student.DoesNotExist:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def post(self, request, token = ''):

		data = loads(request.body)
		tokens = StudentTokenFactory(timeout_days = 5)
		try:

			# Validate inputs before inserting data
			ScheduleSelectView.schema.validate(data)
			student = Student.objects.get(id = request.user.id)

			if tokens.check_token(student, token) is False:
				return JsonResponse({ 'version': '0.1.0', 'status': 409 }, status = 409)

			# All-or-nothing
			with atomic():

				if student.schedule is not None:

					student.schedule.entries.all().update(active = False)
					student.schedule.delete(soft = True)

				# Create the new schedule
				schedule = CourseSchedule.objects.create(expiry = now() + timedelta(months = 6))
				for entry in data['courses']:

					schedule.entries.add(Course.objects.get_active(
						subject__code__iexact = entry['code'],
						instructor__user_id__iexact = entry['instructor'],
						day = entry['day'],
						time = entry['time']
					))
				schedule.save()

				# Set the schedule to the user
				student.schedule = schedule
				student.last_confirmation = now()
				student.semester += 1
				student.save()

				return JsonResponse({
					'version': '0.1.0',
					'status': 201,
					'student': {
						'id': student.user_id,
						'name': student.full_name,
						'email': student.email_address,
						'confirmed': mktime(student.last_confirmation.utctimetuple()),
						'semester': student.semester,
						'schedule': schedule.entries_list
					}
				})

		except Course.DoesNotExist:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
		except User.DoesNotExist:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
		except ValidationError:
			return JsonResponse({ 'version': '0.1.0', 'status': 403 }, status = 403)
select = ScheduleSelectView.as_view()

class SchedulePredictView(View):

	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def get(self, request, token = ''):

		tokens = StudentTokenFactory(timeout_days = 5)
		try:

			student = Student.objects.get(id = request.user.id)

			# Validate the token first
			if tokens.check_token(student, token) is False:
				return JsonResponse({ 'version': '0.1.0', 'status': 409 }, status = 409)

			# List all courses for this user grouped by subject, then instructor
			courses = defaultdict(lambda: defaultdict(list))
			instructors = {}
			course_list = []

			for subject in student.candidate_subjects:

				candidate_courses = Course.objects.active(subject_id = subject.id).annotate(count = Count('schedule__student'))
				if candidate_courses.count() > 0:

					instructors.clear()
					for course in candidate_courses:

						if course.count < 28:

							instructors[course.instructor_id] = course.instructor
							courses[subject.id][course.instructor_id].append({ 'day': course.day, 'time': course.time })

					course_list.append({
						'id': subject.id,
						'code': subject.code,
						'name': subject.name,
						'instructors': [
							{
								'id': instructor.user_id,
								'name': instructor.full_name,
								'email': instructor.email_address,
								'title': instructor.title or '',
								'slots': courses[subject.id][instructor.id]
							} for instructor in instructors.itervalues()
						]
					})

			# Serialize and return response
			return JsonResponse({
				'version': '0.1.0',
				'status': 200,
				'subjects': course_list
			})

		except User.DoesNotExist:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
predict = SchedulePredictView.as_view()
