# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from jsonschema import Draft4Validator, ValidationError
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.http import JsonResponse
from app.rhea.models import *
from json import loads

__all__ = [ 'list', 'create', 'view' ]

class SubjectListView(View):

	@method_decorator(csrf_protect)
	@method_decorator(login_required)
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

	schema = Draft4Validator({
		'$schema': 'http://json-schema.org/draft-04/schema#',
		'definitions': {
			'subject': {
				'type': 'object',
				'properties': {
					'code': { 'type': 'string', 'minLength': 1, 'maxLength': 8 },
					'name': { 'type': 'string', 'minLength': 1 },
					'hours': {
						'type': 'integer',
						'multipleOf': 1,
						'maximum': 10,
						'minimum': 1,
						'exclusiveMaximum': True,
						'exclusiveMinimum': False
					}
				},
				'required': [ 'code', 'name', 'hours' ]
			}
		},
		'oneOf': [
			{
				'type': 'array',
				'items': { '$ref': '#/definitions/subject' }
			},
			{ '$ref': '#/definitions/subject' }
		]
	})

	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def put(self, request):

		data = loads(request.body)
		try:

			# Validate and normalize input for linear iteration
			SubjectCreateView.schema.validate(data)
			entries = [ data ] if isinstance(data, dict) else data

			# Iterate over each entry, creating a new subject for each
			subjects = []
			for e in entries:

				code, name, hours = e['code'], e['name'], e['hours']

				if Subject.objects.active(code__iexact = code).exists():
					raise ValueError('Subject with code "%s" already exists' % code.upper())

				subjects.append(Subject.objects.create(
					code = code.upper(),
					name = name,
					hours = hours
				))

			# Serialize and return response
			return JsonResponse({
				'version': '0.1.0',
				'status': 201,
				'subjects': [
					{
						'id': s.id,
						'code': s.code,
						'name': s.name,
						'hours': s.hours
					} for s in subjects
				]
			}, status = 201)

		except ValueError:
			return JsonResponse({ 'version': '0.1.0', 'status': 407 }, status = 407)
		except ValidationError:
			return JsonResponse({ 'version': '0.1.0', 'status': 403 }, status = 403)
create = SubjectCreateView.as_view()

class SubjectView(View):

	schema = Draft4Validator({
		'$schema': 'http://json-schema.org/draft-04/schema#',
		'type': 'object',
		'properties': {
			'code': { 'oneOf': [ { 'type': 'boolean', 'enum': [ False ] }, { 'type': 'string', 'minLength': 1, 'maxLength': 8 } ] },
			'name': { 'oneOf': [ { 'type': 'boolean', 'enum': [ False ] }, { 'type': 'string', 'minLength': 1 } ] },
			'hours': {
				'oneOf': [
					{ 'type': 'boolean', 'enum': [ False ] },
					{
						'type': 'integer',
						'multipleOf': 1,
						'maximum': 72,
						'minimum': 1,
						'exclusiveMaximum': True,
						'exclusiveMinimum': False
					}
				]
			}
		},
		'required': [ 'code', 'name', 'hours' ]
	})

	@method_decorator(csrf_protect)
	@method_decorator(login_required)
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

		data = loads(request.body)
		try:

			# Validate and normalize input for linear iteration
			SubjectView.schema.validate(data)

			# Locate and update the appointed subject
			new_code, name, hours = data['code'], data['name'], data['hours']
			subject = Subject.objects.get_active(code__iexact = code)

			if new_code is not False: subject.code = code.upper()
			if name is not False: subject.name = name
			if hours is not False: subject.hours = hours

			subject.save()

			# Serialize and return response
			return JsonResponse({
				'version': '0.1.0',
				'status': 200,
				'subject': {
					'id': subject.id,
					'code': subject.code,
					'name': subject.name,
					'hours': subject.hours
				}
			})

		except ValidationError:
			return JsonResponse({ 'version': '0.1.0', 'status': 403 }, status = 403)
		except Subject.DoesNotExist:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
	@method_decorator(csrf_protect)
	# @method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def delete(self, request, code = ''):

		try: subject = Subject.objects.get_active(code__iexact = code)
		except Subject.DoesNotExist:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
		else:

			subject.delete(soft = True)
			return JsonResponse({ 'version': '0.1.0', 'status': 200 })
view = SubjectView.as_view()
