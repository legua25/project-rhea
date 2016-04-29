# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from jsonschema import Draft4Validator, ValidationError
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from app.rhea.mail import TemplateEmailMessage
from django.contrib.auth import get_user_model
from django.shortcuts import RequestContext
from django.db.transaction import atomic
from django.views.generic import View
from django.http import JsonResponse
from app.rhea.models import *
from time import mktime
from json import loads

__all__ = [ 'create', 'view' ]

User = get_user_model()

class StudentCreateView(View):

	schema = Draft4Validator({
		'$schema': 'http://json-schema.org/draft-04/schema#',
		'type': 'object',
		'properties': {
			'id': { 'type': 'string' },
			'general': {
				'type': 'object',
				'properties': {
					'name': { 'type': 'string' },
					'program': { 'type': 'string' },
					'email-address': { 'type': 'string', 'format': 'email' }
				},
				'required': [ 'name', 'program', 'email-address' ]
			},
			'semester': { 'type': 'integer' }
		},
		'required': [ 'id', 'general', 'semester' ]
	})

	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def put(self, request):

		data = loads(request.body)
		try:

			# First, validate the input data through a JSON schema
			StudentCreateView.schema.validate(data)

			# Check if this user is not a duplicate (enroll ID is ab-so-lute)
			if Student.objects.active(user_id = data['id']).exists():
				return JsonResponse({ 'version': '0.1.0', 'status': 409 }, status = 409)
			program = AcademicProgram.objects.get(acronym__iexact = data['general']['program'])

			# Create the student object
			student = Student(
				user_id = data['id'],
				full_name = data['general']['name'],
				email_address = data['general']['email-address'],
				program = program,
				role = Role.objects.get(codename = 'student')
			)
			# Set the base subjects for the student based on the semester
			student.set_at_semester(data['semester'])

			# Create a randomized password for the student for now (we will let them change it later on)
			password = User.objects.make_random_password(12, allowed_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
			student.set_password(password)
			student.save()

			# Send an email to the user with his/her password, as it was randomly-generated
			email = TemplateEmailMessage(
				subject = _('Your password for Project Rhea'),
				from_email = 'noreply@project_rhea.com',
				to = [ student.email_address ],
				context = RequestContext(request, {
					'student': student,
					'password': password
				})
			)
			email.attach_from_template('rhea/email/new-enroll.txt', 'text/plain')
			email.send()

			return JsonResponse({
				'version': '0.1.0',
				'status': 201,
				'email': email.send(fail_silently = True) == 1,
				'student': {
					'id': student.user_id,
					'name': student.full_name,
					'email': student.email_address,
					'created': mktime(student.date_registered.utctimetuple())
				}
			}, status = 201)

		except ValidationError:
			return JsonResponse({ 'version': '0.1.0', 'status': 403 }, status = 403)
		except AcademicProgram.DoesNotExist:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
create = StudentCreateView.as_view()

class StudentView(View):

	schema = Draft4Validator({
		'$schema': 'http://json-schema.org/draft-04/schema#',
		'type': 'object',
		'properties': {
			'name': { 'oneOf': [ { 'type': 'boolean', 'enum': [ False ] },  { 'type': 'string', 'minLength': 1 } ] },
			'email-address': { 'oneOf': [ { 'type': 'boolean', 'enum': [ False ] }, { 'type': 'string', 'format': 'email', 'minLength': 1 } ] },
			'picture': { 'oneOf': [ { 'type': 'boolean', 'enum': [ False ] }, { 'type': 'string', 'minLength': 1 } ] },
			'semester': { 'oneOf': [ { 'type': 'boolean', 'enum': [ False ] }, { 'type': 'integer', 'minimum': 0, 'exclusiveMinimum': False } ] },
			'subjects': {
				'type': 'array',
				'uniqueItems': True,
				'additionalItems': True,
				'items': {
					'type': 'object',
					'properties': {
						'code': { 'type': 'string' },
						'action': {  'type': 'string', 'enum': [ 'add', 'rem' ] }
					},
					'required': [ 'code', 'action' ]
				}
			}
		},
		'required': [ 'name', 'email-address', 'picture', 'semester', 'subjects' ]
	})

	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def get(self, request, id = ''):

		try: student = Student.objects.select_subclasses().get_active(user_id = id)
		except Student.DoesNotExist:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
		else:

			# Serialize the student's full data and send the response
			return JsonResponse({
				'version': '0.1.0',
				'status': 200,
				'student': {
					'id': student.user_id,
					'name': student.full_name,
					'email': student.email_address,
					'picture': student.picture.url,
					'created': mktime(student.date_registered.utctimetuple()),
					'last-login': mktime(student.last_login.utctimetuple()) if student.last_login else False,
					'curriculum': {
						'program': student.program_id,
						'semester': student.semester,
						'current': [
							{
								'id': s.dependent_id,
								'code': s.dependent.code,
								'name': s.dependent.name
							} for s in student.subjects
						],
						'candidate': [
							{
								'id': s.id,
								'code': s.code,
								'name': s.name
							} for s in student.candidate_subjects
						]
					}
				}
			})
	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def post(self, request, id = ''):

		data = loads(request.body)
		try:

			StudentView.schema.validate(data)
			student = Student.objects.select_subclasses().get_active(user_id = id)

			# Apply the changes in a transaction since we may need to perform several updates at once
			with atomic():

				# Apply each update available
				if data['name'] is not False: student.full_name = data['name']
				if data['email-address'] is not False: student.email_address = data['email-address']
				if data['semester'] is not False:

					# Clear the progress - this is a destructive operation, ye have been warned
					student.subjects.clear()
					student.set_at_semester(data['semester'])
				if data['picture'] is not False:

					# In this case, "picture" points to the name of the form element which held the file (for flexibility at frontend)
					if data['picture'] not in request.FILES:
						return JsonResponse({ 'version': '0.1.0', 'status': 409 }, status = 409)

					student.picture = request.FILES[data['picture']]

				try:

					program = student.program_id
					for entry in data['subjects']:

						# The subject works using a standard many-to-many relationship, so this is available
						subject, action = Requirement.objects.get_active(program_id = program, dependent__code__iexact = entry['code']), entry['action']

						if action == 'add': subject.subjects.add(subject)
						elif action == 'rem': subject.subjects.remove(subject)

				except Subject.DoesNotExist:
					return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)

				# Commit the changes now, then serialize the updated student
				student.save()
				return JsonResponse({
					'version': '0.1.0',
					'status': 200,
					'student': {
						'id': student.user_id,
						'name': student.full_name,
						'email': student.email_address,
						'picture': student.picture.url,
						'created': mktime(student.date_registered.utctimetuple()),
						'last-login': mktime(student.last_login.utctimetuple()) if student.last_login else False,
						'curriculum': {
							'program': student.program_id,
							'semester': student.semester,
							'current': [
								{
									'id': s.dependent_id,
									'code': s.dependent.code,
									'name': s.dependent.name
								} for s in student.subjects
							],
							'candidate': [
								{
									'id': s.id,
									'code': s.code,
									'name': s.name
								} for s in student.candidate_subjects
							]
						}
					}
				})

		except Student.DoesNotExist:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
		except ValidationError:
			return JsonResponse({ 'version': '0.1.0', 'status': 403 }, status = 403)
	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def delete(self, request, id = ''):

		try: student = Student.objects.select_subclasses().get_active(user_id = id)
		except Student.DoesNotExist:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
		else:

			# We use soft-delete here, so no need to worry
			student.delete(soft = True)
			return JsonResponse({ 'version': '0.1.0', 'status': 200 })
view = StudentView.as_view()
