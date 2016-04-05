# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from jsonschema import Draft4Validator, ValidationError
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.http import JsonResponse
from app.rhea.models import *

__all__ = [ 'list', 'create', 'view' ]

class SubjectListView(View):

	@method_decorator(csrf_protect)
	# @method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def get(self, request):

		# Page the subjects list
		page, size = request.GET.get('page', 1), request.GET.get('size', 15)
		pages = Paginator(Subject.objects.active().order_by('code'), size)

		try: subjects = pages.page(page)
		except PageNotAnInteger: subjects = pages.page(1)
		except EmptyPage: subjects = pages.page(pages.num_pages)

		# Serialize and send back response
		return JsonResponse({
			'version': '0.1.0',
			'status': 200,
			'pagination': {
				'total': Subject.objects.active().count(),
				'current': page,
				'previous': subjects.previous_page_number() if subjects.has_previous() else False,
				'next': subjects.next_page_number() if subjects.has_next() else False,
				'size': size
			},
			'subjects': [
				{
					'id': s.id,
					'code': s.code,
					'name': s.name,
					'hours': s.hours
				} for s in subjects
			]
		})
list = SubjectListView.as_view()

class SubjectCreateView(View):

	@method_decorator(csrf_protect)
	# @method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def put(self, request):

		return JsonResponse({
			'version': '0.1.0',
			'status': 501
		}, status = 501)
create = SubjectCreateView.as_view()

class SubjectView(View):

	@method_decorator(csrf_protect)
	# @method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def get(self, request, code = ''):

		# Try to locate the subject - return 404 Not Found if code is invalid
		try: subject = Subject.objects.get_active(code = code)
		except Subject.DoesNotExist:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
		else:

			response = {
				'version': '0.1.0',
				'status': 200,
				'subject': {
					'id': subject.id,
					'code': subject.code,
					'name': subject.name,
					'hours': subject.hours
				}
			}

			# If we were given the optional "program" parameter, we should list dependencies and dependents instead of programs
			if 'program' in request.GET:

				try: program = AcademicProgram.objects.get(acronym = request.GET['program'])
				except AcademicProgram.DoesNotExist:
					return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
				else:

					response['subject']['program'] = {
						'acronym': program.acronym,
						'dependencies': [ { 'id': s.id, 'code': s.code } for s in subject.dependencies(program) ],
						'dependents': [ { 'id': s.id, 'code': s.code } for s in subject.dependents(program) ]
					}
			else:

				# Get all programs in which this subject is a requirement and list their IDs
				programs = set(Requirement.objects.active(dependent_id = subject.id).values_list('program__acronym', flat = True))
				response['subject']['programs'] = [ program for program in programs ]

			# Serialize and send back response
			return JsonResponse(response)
	@method_decorator(csrf_protect)
	# @method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def post(self, request, code = ''):

		return JsonResponse({
			'version': '0.1.0',
			'status': 501
		}, status = 501)
	@method_decorator(csrf_protect)
	# @method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def delete(self, request, code = ''):

		return JsonResponse({
			'version': '0.1.0',
			'status': 501
		}, status = 501)
view = SubjectView.as_view()
