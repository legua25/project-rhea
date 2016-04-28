# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
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

__all__ = [ 'subjects' ]

class ScheduleSubjectsView(View):

	@method_decorator(csrf_protect)
	# @method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def post(self, request):

		try:

			# This view is profiled to measure performance and support/refute hypothesis
			start = now()
			with atomic():

				# TODO: This number is hardcoded where it should be editable without getting into code
				minimum = min(Student.objects.active().count(), 15)

				# Calculate academic demand and offer
				demand = Student.objects.demanded_subjects(minimum).count()
				subjects = Instructor.objects.available_subjects(minimum)

				# Coverage is a measure of how much of the demand can the institution cover with their current resources
				coverage = subjects.count() / demand
			end = now()

			# Serialize the result and send it back
			# As much as we'd like to, we should not calculate the population again - we're dealing with future values,
			# not current ones, so this cannot be done without taxing performance
			return JsonResponse({
				'version': '0.1.0',
				'status': 200,
				'stats': {
					'elapsed': (end - start).microseconds,
					'start': mktime(start.utctimetuple()),
					'coverage': coverage
				},
				'subjects': [
					{
						'id': s.id,
						'code': s.code,
						'name': s.name
					} for s in subjects
				]
			})

		except ValidationError:
			return JsonResponse({ 'version': '0.1.0', 'status': 403 }, status = 403)
subjects = cache_page(3600)(ScheduleSubjectsView.as_view())


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
	# @method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def post(self, request):

		data = loads(request.body)
		try:

			# First, validate the input data through a JSON schema
			ScheduleCourseView.schema.validate(data)
			subjects = set(data['subjects'])

			# For each instructor, get the available courses and calculate a schedule
			start = now()
			with atomic():

				courses = []
				slots = defaultdict(list)
				for instructor in Instructor.objects.active():

					# Availability and the like is computed automatically by the schedule builder
					builder = ScheduleBuilder(instructor, subjects)

					# Collect all time slots for the same course
					slots.clear()
					for (slot, subject) in builder.entries.iteritems():
						slots[subject].append(slot)

					# Roll the information out into the final form
					for (subject, slots) in slots.iteritems():
						courses.append({
							'instructor': instructor.user_id,
							'subject': Subject.objects.get_active(id = subject).code,
							'slots': [ { 'day': day, 'time': time } for (day, time) in slots ]
						})
			end = now()

			return JsonResponse({
				'version': '0.1.0',
				'status': 200,
				'stats': {
					'elapsed': (end - start).microseconds,
					'start': mktime(start.utctimetuple())
				},
				'courses': courses
			})

		except ValidationError:
			return JsonResponse({ 'version': '0.1.0', 'status': 403 }, status = 403)
courses = cache_page(3600)(ScheduleCourseView.as_view())
