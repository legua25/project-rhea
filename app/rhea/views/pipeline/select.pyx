# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
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
from collections import defaultdict
from app.rhea.models import *
from time import mktime
from json import loads


__all__ = [ 'select' ]

class ScheduleSelectView(View):

	schema = Draft4Validator({})

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
							'elapsed': (end - start).microseconds
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
				'token': tokens.make_token(request.user),
				'execution': response
			})
	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def post(self, request, token = ''):
		return JsonResponse({ 'version': '0.1.0', 'status': 403 }, status = 403)
select = ScheduleSelectView.as_view()
