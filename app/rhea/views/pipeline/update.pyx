# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from dateutil.relativedelta import relativedelta as timedelta
from django.contrib.auth.decorators import login_required
from jsonschema import Draft4Validator, ValidationError
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.core.management import call_command
from app.rhea.tokens import AuthTokenFactory
from django.db.transaction import atomic
from StringIO import StringIO as strio
from django.views.generic import View
from django.utils.timezone import now
from django.http import JsonResponse
from operator import or_ as __or__
from django.db.models import Q
from app.rhea.models import *
from time import mktime
from json import loads


__all__ = [ 'update' ]

class ScheduleUpdateView(View):

	schema = Draft4Validator({
		'$schema': 'http://json-schema.org/draft-04/schema#',
		'type': 'object',
		'properties': {
			'subjects': {
				'type': 'array',
				'minItems': 1,
				'items': { 'type': 'string' }
			},
			'schedule': {
				'type': 'array',
				'minItems': 1,
				'items': {
					'type': 'object',
					'properties': {
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
						},
						'level': {
							'type': 'number',
							'maximum': 1.0,
							'minimum': 0.0,
							'exclusiveMaximum': False,
							'exclusiveMinimum': False
						}
					},
					'required': [ 'day', 'time', 'level' ]
				}
			}
		},
		'required': [ 'subjects', 'schedule' ]
	})

	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def get(self, request, token = False):

		tokens = AuthTokenFactory(timeout_days = 5)
		if token is not False:

			# Validate the token first
			if tokens.check_token(request.user, token) is False:
				return JsonResponse({ 'version': '0.1.0', 'status': 407 }, status = 407)

			# Having a token means we're querying the current state
			with atomic():

				start = now()
				instructors = Instructor.objects.active()

				total = instructors.count()
				remaining = instructors.filter(last_confirmation__isnull = True)
				end = now()

				return JsonResponse({
					'version': '0.1.0',
					'status': 200,
					'token': token,
					'execution': {
						'stats': {
							'coverage': (remaining.count() / total),
							'start': mktime(start.utctimetuple()),
							'elapsed': (end - start).microseconds
						},
						'pending': [
							{
								'id': instructor.user_id,
								'name': instructor.full_name,
								'last-login': instructor.last_login
							} for instructor in remaining
						]
					}
				})
		else:

			# Run the command and capture results
			# TODO: Make this self-scheduling later on... for now, we'll leave it as a single swipe
			stdout = strio()
			call_command('runtask', args = [ 'email_instructors' ], stdout = stdout)
			response = loads(stdout.getvalue().strip())

			# Serialize data and return
			return JsonResponse({
				'version': '0.1.0',
				'status': 200,
				'token': tokens.make_token(request.user),
				'execution': response
			})
	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def post(self, request, token = ''):

		data = loads(request.body)
		try:

			# Collect data and validate
			ScheduleUpdateView.schema.validate(data)
			instructor = Instructor.objects.get(id = request.user.id)

			tokens = AuthTokenFactory(timeout_days = 5)
			if not tokens.check_token(instructor, token): raise ValueError('Token is invalid')

			with atomic():

				# Update subjects
				Specialty.objects.active(instructor__id = instructor.id).delete()
				instructor.specialties = [ Specialty.objects.create(instructor = instructor, subject = Subject.objects.get_active(code = subject)) for subject in data['subjects'] ]

				# Update schedule
				if instructor.availability:

					instructor.availability.active = False
					instructor.availability.save()

				schedule = AvailabilitySchedule.objects.create(expiry = now() + timedelta(months = 6))
				for e in data['schedule']:
					schedule.entries.add(Availability.objects.create(level = e['level'], day = e['day'], time = e['time']))

				instructor.availability = schedule

				instructor.last_confirmation = now()
				instructor.save()

				return JsonResponse({
					'version': '0.1.0',
					'status': 201,
					'instructor': {
						'id': instructor.user_id,
						'name': instructor.full_name,
						'email': instructor.email_address,
						'confirmed': mktime(instructor.last_confirmation.utctimetuple()),
						'subjects': [ specialty.subject.code for specialty in instructor.specialties.all().filter(active = True) ],
						'schedule': schedule.entries_list
					}
				}, status = 201)
		except ValueError:
			return JsonResponse({ 'version': '0.1.0', 'status': 407 }, status = 407)
		except Instructor.DoesNotExist:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
		except ValidationError:
			return JsonResponse({ 'version': '0.1.0', 'status': 403 }, status = 403)
update = ScheduleUpdateView.as_view()
