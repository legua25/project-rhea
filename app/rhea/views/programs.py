# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from jsonschema import Draft4Validator, ValidationError
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.http import JsonResponse
from app.rhea.models import *
from json import loads

__all__ = [ 'list', 'create', 'view' ]

class ProgramListView(View):

	@method_decorator(csrf_protect)
	# @method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def get(self, request):

		# Page the programs list
		page, size = request.GET.get('page', 1), request.GET.get('size', 15)
		pages = Paginator(AcademicProgram.objects.active().order_by('acronym'), size)

		try: programs = pages.page(page)
		except PageNotAnInteger: programs = pages.page(1)
		except EmptyPage: programs = pages.page(pages.num_pages)

		# Serialize and send back response
		return JsonResponse({
			'version': '0.1.0',
			'status': 200,
			'pagination': {
				'total': AcademicProgram.objects.active().count(),
				'current': page,
				'previous': programs.previous_page_number() if programs.has_previous() else False,
				'next': programs.next_page_number() if programs.has_next() else False,
				'size': size
			},
			'programs': [
				{
					'id': p.id,
					'acronym': p.acronym,
					'name': p.name
				} for p in programs
			]
		})
list = ProgramListView.as_view()

class ProgramCreateView(View):

	schema = Draft4Validator({
		'$schema': 'http://json-schema.org/draft-04/schema#',
		'type': 'object',
		'properties': {
			'acronym': { 'type': 'string', 'minLength': 1 },
			'name': { 'type': 'string', 'minLength': 1 },
			'profile': { 'oneOf': [ { 'type': 'boolean', 'enum': [ False ] }, { 'type': 'string', 'minLength': 1 } ] },
			'subjects': {
				'type': 'array',
				'minItems': 1,
				'uniqueItems': True,
				'items': {
					'type': 'object',
					'properties': {
						'code': { 'type': 'string', 'minLength': 1 },
						'semester': { 'type': 'integer', 'minimum': 0, 'exclusiveMinimum': False },
						'dependencies': {
							'type': 'array',
							'uniqueItems': True,
							'additionalItems': True,
							'items': { 'type': 'string', 'minLength': 1 }
						}
					}
				}
			}
		},
		'required': [ 'acronym', 'name', 'description', 'profile', 'subjects' ]
	})

	@method_decorator(csrf_protect)
	# @method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def put(self, request):

		data = loads(request.body)
		try:

			# First, validate the input data through a JSON schema
			ProgramCreateView.schema.validate(data)

			# Check the program data is not a duplicate
			if AcademicProgram.objects.get_active(acronym__iexact = data['acronym']):
				return JsonResponse({ 'version': '0.1.0', 'status': 409 }, status = 409)

			# Get all subjects with dependencies first
			items = []
			try:

				for subject in data['subjects']:

					dependent = Subject.objects.get_active(code__iexact = subject['code'])
					dependencies = map(lambda s: Subject.objects.get_active(code__iexact = s), subject.dependencies)
					semester = subject['semester']

					if bool(dependencies) is not False: items.extend([ (dependent, s, semester) for s in dependencies ])
					else: items.append((dependent, None, semester))

			except Subject.DoesNotExist:
				return JsonResponse({ 'version': '0.1.0', 'status': 409 }, status = 409)

			# Create the academic program - the graduate profile file must be added if available
			program = AcademicProgram(
				acronym = data['acronym'].upper(),
				name = data['name']
			)

			# In this case, "profile" points to the name of the form element which held the file (for flexibility at frontend)
			if data['profile'] is not False: program.graduate_profile = request.FILES[data['profile']]
			program.save()

			# Map requirements to program - use tuple unpacking to make things easier
			requirements = map(lambda (dependent, dependency, semester): Requirement.objects.create(
				dependent = dependent,
				dependency = dependency,
				semester = semester,
				program = program
			), items)

			return JsonResponse({
				'version': '0.1.0',
				'status': 201,
				'program': {
					'id': program.id,
					'acronym': program.acronym,
					'name': program.name,
					'profile': program.graduate_profile.url if program.graduate_profile else False,
					'subjects': [
						{ 'id': r.dependent_id, 'code': r.dependent.code } for r in requirements
					]
				}
			}, status = 201)

		except ValidationError:
			return JsonResponse({ 'version': '0.1.0', 'status': 403 }, status = 403)
create = ProgramCreateView.as_view()

class ProgramView(View):

	@method_decorator(csrf_protect)
	# @method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def get(self, request, acronym = ''):

		# Try to locate the subject - return 404 Not Found if code is invalid
		try: program = AcademicProgram.objects.get_active(acronym = acronym)
		except Subject.DoesNotExist:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
		else:

			# Paginate the program requirements, since these can be quite extensive
			page, size = request.GET.get('page', 1), request.GET.get('size', 15)
			pages = Paginator(program.subjects.order_by('code'), size)

			try: subjects = pages.page(page)
			except PageNotAnInteger: subjects = pages.page(1)
			except EmptyPage: subjects = pages.page(pages.num_pages)

			# Serialize and send back response
			return JsonResponse({
				'version': '0.1.0',
				'status': 200,
				'pagination': {
					'total': program.subjects.count(),
					'current': page,
					'previous': subjects.previous_page_number() if subjects.has_previous() else False,
					'next': subjects.next_page_number() if subjects.has_next() else False,
					'size': size
				},
				'program': {
					'id': program.id,
					'acronym': program.acronym,
					'name': program.name,
					'subjects': [ { 'id': s.id, 'code': s.code } for s in subjects ]
				}
			})
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
view = ProgramView.as_view()
