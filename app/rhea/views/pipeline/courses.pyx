# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from django.contrib.auth.decorators import login_required
from jsonschema import Draft4Validator, ValidationError
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.db.transaction import atomic
from django.views.generic import View
from django.utils.timezone import now
from django.http import JsonResponse
from collections import defaultdict
from app.rhea.models import *
from time import mktime
from json import loads


__all__ = [ 'courses' ]

class ScheduleCourseView(View):

	schema = Draft4Validator({
		'$schema': 'http://json-schema.org/draft-04/schema#',
		'type': 'object',
		'properties': {
			'subjects': {
				'type': 'array',
				'uniqueItems': True,
				'additionalItems': True,
				'items': [
					{
						'type': 'integer',
						'multipleOf': 1,
						'minimum': 1,
						'exclusiveMinimum': False
					}
				]
			}
		},
		'required': [ 'subjects' ]
	})

	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def post(self, request):

		data = loads(request.body)
		try:

			# First, validate the input data through a JSON schema
			ScheduleCourseView.schema.validate(data)
			subjects = set(data['subjects'][:40])

			# For each instructor, get the available courses and calculate a schedule
			start = now()
			with atomic():

				courses = []
				slots = defaultdict(list)
				for instructor in Instructor.objects.active():

					# Availability and the like is computed automatically by the schedule builder
					builder = ScheduleBuilder(instructor, subjects)
					builder.save(CourseSchedule, Course)

					# Collect all time slots for the same course
					slots.clear()
					for (slot, subject) in builder.entries.iteritems():
						slots[subject].append(slot)

					# Roll the information out into the final form
					for (id, slot) in slots.iteritems():

						subject = Subject.objects.get_active(id = id)
						courses.append({
							'instructor': { 'id': instructor.user_id, 'name': instructor.full_name },
							'subject': { 'code': subject.code, 'name': subject.name },
							'slots': [ { 'day': day, 'time': time } for (day, time) in slot ]
						})
			end = now()

			return JsonResponse({
				'version': '0.1.0',
				'status': 200,
				'stats': {
					'elapsed': (end - start).total_seconds() * 1000000,
					'start': mktime(start.utctimetuple())
				},
				'courses': courses
			})

		except ValidationError:
			return JsonResponse({ 'version': '0.1.0', 'status': 403 }, status = 403)
courses = cache_page(3600)(ScheduleCourseView.as_view())
