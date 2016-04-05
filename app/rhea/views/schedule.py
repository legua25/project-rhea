# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from jsonschema import Draft4Validator, ValidationError
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.db.transaction import atomic
from django.views.generic import View
from django.utils.timezone import now
from django.http import JsonResponse
from django.db.models import Count
from app.rhea.models import *
from time import mktime
from json import loads

__all__ = [ 'subjects' ]

class ScheduleSubjectsView(View):

	schema = Draft4Validator({
		'$schema': 'http://json-schema.org/draft-04/schema#',
		'type': 'object',
		'properties': {
			'minimum': { 'oneOf': [ { 'type': 'integer', 'minimum': 0, 'exclusiveMinimum': False }, { 'type': 'boolean', 'enum': [ False ] } ] }
		},
		'required': [ 'minimum' ]
	})

	@method_decorator(csrf_protect)
	# @method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def post(self, request):

		data = loads(request.body)

		try:

			# First, validate the input data through a JSON schema
			ScheduleSubjectsView.schema.validate(data)
			minimum = data['minimum']

			# This view is profiled to measure performance and support/refute hypothesis
			start = now()
			with atomic():

				demand = Student.objects.demanded_subjects()
				offer = Instructor.objects.available_subjects()

				subjects = []
				for subject in demand:

					count = Student.objects.active(subjects__id__in = [ subject.id ]).count()
					available = offer.filter(id = subject.id).exists() and count >= minimum
					subjects.append((subject, count, available))

			end = now()

			# Serialize the result and send it back
			return JsonResponse({
				'version': '0.1.0',
				'status': 200,
				'profiler': { 'elapsed': (end - start).microseconds, 'start': mktime(start.utctimetuple()) },
				'subjects': [
					{
						'id': s.id,
						'code': s.code,
						'name': s.name,
						'population': count,
						'available': available
					} for (s, count, available) in subjects
				]
			})

		except ValidationError:
			return JsonResponse({ 'version': '0.1.0', 'status': 403 }, status = 403)
subjects = ScheduleSubjectsView.as_view()
