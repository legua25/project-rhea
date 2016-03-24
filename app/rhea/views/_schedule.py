# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render_to_response
from django.views.generic import View
from django.http import JsonResponse
from collections import defaultdict
from operator import add as __add__
from app.rhea.models import *

class SchedulePrebuildView(View):

	def get(self, request):

		# Disable existing courses first
		Course.objects.all().update(active = False)

		# Get the course populations (steps 1-2)
		students = Student.objects.active()
		instructors = Instructor.objects.active()
		available_subjects = set(Instructor.objects.available_subjects().values_list('id', flat = True))

		# For each student, match available subjects to candidate subjects and create course templates (step 3)
		courses = defaultdict(list)
		for student in students:

			# Get actual subjects the student may take
			candidates = set(student.candidate_subjects.values_list('id', flat = True))
			subjects = candidates.intersection(available_subjects)

			# For each subject, find all instructors able to offer it, then create a course for each
			for subject in subjects:

				available_instructors = instructors.filter(subjects__id = subject).values_list('id', flat = True)
				for instructor in available_instructors:

					courses[subject].append({
						'student': student.id,
						'subject': subject,
						'instructor': instructor
					})

		# TODO: Remove this
		# Flatten the list and showcase the results
		return JsonResponse({
			'version': '0.1.0',
			'status': 200,
			'courses': reduce(__add__, courses.itervalues(), [])
		})
