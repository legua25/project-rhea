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
from app.rhea.models import *
from time import mktime

__all__ = [ 'subjects' ]


class ScheduleSubjectsView(View):

	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def post(self, request):

		# This view is profiled to measure performance
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
subjects = cache_page(3600)(ScheduleSubjectsView.as_view())
