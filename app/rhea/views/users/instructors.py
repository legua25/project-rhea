# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from dateutil.relativedelta import relativedelta as timedelta
from django.contrib.auth.decorators import login_required
from jsonschema import Draft4Validator, ValidationError
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from app.rhea.mail import TemplateEmailMessage
from django.contrib.auth import get_user_model
from django.shortcuts import RequestContext
from django.db.transaction import atomic
from django.utils.timezone import now
from django.views.generic import View
from django.http import JsonResponse
from app.rhea.models import *
from time import mktime
from json import loads

__all__ = [ 'create', 'view' ]

User = get_user_model()

class InstructorCreateView(View):

	schema = Draft4Validator({
		'$schema': 'http://json-schema.org/draft-04/schema#',
		'type': 'object',
		'properties': {
			'id': { 'type': 'string' },
			'general': {
				'type': 'object',
				'properties': {
					'name': { 'type': 'string' },
					'email-address': { 'type': 'string', 'format': 'email' },
					'title': { 'type': 'string' }
				},
				'required': [ 'name', 'email-address' ]
			},
			'subjects': {
				'type': 'array',
				'uniqueItems': True,
				'minItems': 1,
				'items': { 'type': 'string' }
			}
		},
		'required': [ 'id', 'general', 'subjects' ]
	})

	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def put(self, request):

		data = loads(request.body)
		try:

			# First, validate the input data through a JSON schema
			InstructorCreateView.schema.validate(data)

			# Check if this user is not a duplicate (enroll ID is ab-so-lute)
			if Instructor.objects.active(user_id = data['id']).exists():
				return JsonResponse({ 'version': '0.1.0', 'status': 409 }, status = 409)

			# We need to process many queries and related stuff, so we wrap everything in a transaction
			with atomic():

				# Create the student object
				instructor = Instructor(
					user_id = data['id'],
					full_name = data['general']['name'],
					email_address = data['general']['email-address'],
					availability = Availability.objects.create(expiry = now() + timedelta(days = 15)),
					role = Role.objects.get(codename = 'instructor')
				)

				# Create a randomized password for the instructor for now (we will let them change it later on)
				password = User.objects.make_random_password(12, allowed_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
				instructor.set_password(password)
				instructor.save()

				# Connect with each specialty subject - assign full confidence as default value
				for code in data['subjects']:

					Specialty.objects.create(
						subject = Subject.objects.get(code__iexact = code),
						instructor = instructor,
						confidence = 1.0
					)

				# Send an email to the user with his/her password, as it was randomly-generated
				email = TemplateEmailMessage(
					subject = _('Your password for Project Rhea'),
					from_email = 'noreply@project_rhea.com',
					to = [ instructor.email_address ],
					context = RequestContext(request, {
						'instructor': instructor,
						'password': password
					})
				)
				email.attach_from_template('rhea/email/new-instructor.txt', 'text/plain')
				email.send()

				return JsonResponse({
					'version': '0.1.0',
					'status': 201,
					'email': email.send(fail_silently = True) == 1,
					'instructor': {
						'id': instructor.user_id,
						'name': instructor.full_name,
						'email': instructor.email_address,
						'created': mktime(instructor.date_registered.utctimetuple())
					}
				}, status = 201)

		except ValidationError:
			return JsonResponse({ 'version': '0.1.0', 'status': 403 }, status = 403)
create = InstructorCreateView.as_view()

class InstructorView(View):

	schema = Draft4Validator({
		'$schema': 'http://json-schema.org/draft-04/schema#',
		'type': 'object',
		'properties': {
			'name': { 'oneOf': [ { 'type': 'boolean', 'enum': [ False ] },  { 'type': 'string', 'minLength': 1 } ] },
			'email-address': { 'oneOf': [ { 'type': 'boolean', 'enum': [ False ] }, { 'type': 'string', 'format': 'email', 'minLength': 1 } ] },
			'picture': { 'oneOf': [ { 'type': 'boolean', 'enum': [ False ] }, { 'type': 'string', 'minLength': 1 } ] },
			'subjects': {
				'type': 'array',
				'uniqueItems': True,
				'additionalItems': True,
				'items': {
					'type': 'object',
					'properties': {
						'code': { 'type': 'string' },
						'action': {  'type': 'string', 'enum': [ 'add', 'rem', 'chg' ] },
						'confidence': { 'type': 'number', 'minimum': 0.0, 'maximum': 1.0, 'exclusiveMinimum': False, 'exclusiveMaximum': False }
					},
					'required': [ 'code', 'action' ]
				}
			}
		},
		'required': [ 'name', 'email-address', 'picture', 'subjects' ]
	})

	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def get(self, request, id = ''):

		try: instructor = Instructor.objects.select_subclasses().get_active(user_id = id)
		except Instructor.DoesNotExist:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
		else:

			# Serialize the instructor's full data and send the response
			return JsonResponse({
				'version': '0.1.0',
				'status': 200,
				'instructor': {
					'id': instructor.user_id,
					'name': instructor.full_name,
					'email': instructor.email_address,
					'picture': instructor.picture.url,
					'created': mktime(instructor.date_registered.utctimetuple()),
					'last-login': mktime(instructor.last_login.utctimetuple()) if instructor.last_login else False,
					'specialties': [
						{
							'id': s.subject.id,
							'code': s.subject.code,
							'name': s.subject.name,
							'confidence': s.confidence
						} for s in instructor.specialties.all().filter(active = True)
					]
				}
			})
	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def post(self, request, id = ''):

		data = loads(request.body)
		try:

			InstructorView.schema.validate(data)
			instructor = Instructor.objects.select_subclasses().get_active(user_id = id)

			# Apply the changes in a transaction since we may need to perform several updates at once
			with atomic():

				# Apply each update available
				if data['name'] is not False: instructor.full_name = data['name']
				if data['email-address'] is not False: instructor.email_address = data['email-address']
				if data['picture'] is not False:

					# In this case, "picture" points to the name of the form element which held the file (for flexibility at frontend)
					if data['picture'] not in request.FILES:
						return JsonResponse({ 'version': '0.1.0', 'status': 409 }, status = 409)

					instructor.picture = request.FILES[data['picture']]

				try:

					for entry in data['subjects']:

						# Specialties are not as straightforward, so we update manually - these can be edited as well
						subject, action = Subject.objects.get_active(code__iexact = entry['code']).id, entry['action']

						if action == 'add':

							Specialty.objects.create(
								subject_id = subject,
								instructor_id = instructor.id,
								confidence = entry.get('confidence', 1.0)
							)
						elif action == 'chg': Specialty.objects.active(subject_id = subject, instructor_id = instructor.id).update(confidence = entry.get('confidence', 1.0))
						elif action == 'rem': Specialty.objects.get_active(subject_id = subject, instructor_id = instructor.id).delete(soft = True)

				except Specialty.DoesNotExist, Subject.DoesNotExist:
					return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)

				# Commit the changes now, then serialize the updated student
				instructor.save()
				return JsonResponse({
					'version': '0.1.0',
					'status': 200,
					'instructor': {
						'id': instructor.user_id,
						'name': instructor.full_name,
						'email': instructor.email_address,
						'picture': instructor.picture.url,
						'created': mktime(instructor.date_registered.utctimetuple()),
						'last-login': mktime(instructor.last_login.utctimetuple()) if instructor.last_login else False,
						'specialties': [
							{
								'id': s.subject.id,
								'code': s.subject.code,
								'name': s.subject.name,
								'confidence': s.confidence
							} for s in Specialty.objects.active(instructor_id = instructor.id)
						]
					}
				})

		except Instructor.DoesNotExist:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
		except ValidationError:
			return JsonResponse({ 'version': '0.1.0', 'status': 403 }, status = 403)
	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def delete(self, request, id = ''):

		try: instructor = Instructor.objects.select_subclasses().get_active(user_id = id)
		except Student.DoesNotExist:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
		else:

			# We use soft-delete here, so no need to worry
			instructor.delete(soft = True)
			return JsonResponse({ 'version': '0.1.0', 'status': 200 })
view = InstructorView.as_view()
