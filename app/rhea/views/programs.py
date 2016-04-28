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

class ProgramListView(View):

	@method_decorator(csrf_protect)
	@method_decorator(login_required)
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
		'required': [ 'acronym', 'name', 'profile', 'subjects' ]
	})

	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def put(self, request):

		data = loads(request.body)
		try:

			# Validate input data for integrity, then check for collisions
			ProgramCreateView.schema.validate(data)
			acronym = data['acronym']

			if AcademicProgram.objects.active(acronym__iexact = acronym).exists():
				raise ValueError('Program with acronym "%s" already exists' % acronym.upper())

			# Extract data and create the initial item
			name = data['name']
			profile = request.FILES.get(data['profile'], None) if data['profile'] is not False else None
			program = AcademicProgram.objects.create(
				name = name,
				acronym = acronym.upper(),
				graduate_profile = profile
			)

			# Process the subjects
			requirements = {}
			for entry in data['subjects']:

				subject = Subject.objects.get_active(code__iexact = entry['code'])
				semester = entry['semester']
				dependencies = [ Subject.objects.get_active(code__iexact = code) for code in entry['dependencies'] ]

				# Create the dependency chain and register each
				requirements[subject] = [
					Requirement.objects.create(
						dependent = subject,
						dependency = dependency,
						semester = semester,
						program = program
					) for dependency in dependencies
				]

			return JsonResponse({
				'version': '0.1.0',
				'status': 201,
				'program': {
					'id': program.id,
					'acronym': program.acronym,
					'name': program.name,
					'profile': program.graduate_profile.url if program.graduate_profile else False,
					'subjects': [
						{
							'id': subject.id,
							'code': subject.code,
							'name': subject.name,
							'dependencies': [ r.dependency_id for r in dependencies ]
						} for subject, dependencies in requirements
					]
				}
			}, status = 201)

		except ValueError:
			return JsonResponse({ 'version': '0.1.0', 'status': 407 }, status = 407)
		except ValidationError:
			return JsonResponse({ 'version': '0.1.0', 'status': 403 }, status = 403)
create = ProgramCreateView.as_view()

class ProgramView(View):

	schema = Draft4Validator({
		'$schema': 'http://json-schema.org/draft-04/schema#',
		'type': 'object',
		'properties': {
			'acronym': { 'oneOf': [ { 'type': 'boolean', 'enum': [ False ] }, { 'type': 'string', 'minLength': 1 } ] },
			'name': { 'oneOf': [ { 'type': 'boolean', 'enum': [ False ] }, { 'type': 'string', 'minLength': 1 } ] },
			'profile': { 'oneOf': [ { 'type': 'boolean', 'enum': [ False ] }, { 'type': 'string', 'minLength': 1 } ] }
		},
		'required': [ 'acronym', 'name', 'profile' ]
	})

	@method_decorator(csrf_protect)
	@method_decorator(login_required)
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
					'profile': program.graduate_profile.url if program.graduate_profile else False,
					'subjects': [
						{
							'id': s.id,
							'code': s.code,
							'name': s.name,
							'dependencies': [ subject for subject in Requirement.objects.dependencies_for(program.id, s.id) ]
						} for s in subjects
					]
				}
			})
	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def post(self, request, acronym = ''):

		data = loads(request.body)
		try:

			# Validate the data and retrieve the program
			ProgramView.schema.validate(data)
			program = AcademicProgram.objects.get_active(acronym = acronym)

			if data['name'] is not False: program.name = data['name']
			if data['acronym'] is not False: program.acronym = data['acronym']
			if data['profile'] is not False:

				profile = data['profile']
				if profile not in request.FILES: raise ValueError()

				program.graduate_profile = request.FILES[profile]

			program.save()

			return JsonResponse({
				'version': '0.1.0',
				'status': 200,
				'program': {
					'id': program.id,
					'acronym': program.acronym,
					'name': program.name,
					'profile': program.graduate_profile.url if program.graduate_profile else False
				}
			})

		except ValueError:
			return JsonResponse({ 'version': '0.1.0', 'status': 407 }, status = 407)
		except Subject.DoesNotExist:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
		except ValidationError:
			return JsonResponse({ 'version': '0.1.0', 'status': 403 }, status = 403)
	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def delete(self, request, acronym = ''):

		try: program = AcademicProgram.objects.get_active(acronym = acronym)
		except AcademicProgram.DoesNotExist:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
		else:

			program.delete(soft = True)
			return JsonResponse({ 'version': '0.1.0', 'status': 200 })
view = ProgramView.as_view()
