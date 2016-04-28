# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import update_last_login
from jsonschema import Draft4Validator, ValidationError
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from app.rhea.tokens import AuthTokenFactory
from django.views.generic import View
from django.http import JsonResponse
from base64 import b64decode
from json import loads

from django.contrib.auth import (
	logout as logout_from_site,
	login as login_to_site,
	authenticate
)

__all__ = [
	'LoginView',
	'LogoutView',
	'TokenValidationView'
]

User = get_user_model()

class LoginView(View):

	schema = Draft4Validator({
		'$schema': 'http://json-schema.org/draft-04/schema#',
		'type': 'object',
		'properties': {
			'id': { 'type': 'string', 'minLength': 1 },
			'password': { 'type': 'string', 'minLength': 1 }
		},
		'required': [ 'id', 'password' ]
	})

	@method_decorator(csrf_exempt)
	def post(self, request):

		data = loads(request.body)
		try:

			# Validate the user's credentials
			LoginView.schema.validate(data)
			user_id, password = data['id'], b64decode(data['password'])

			if user_id and password:

				user = authenticate(user_id = user_id, password = password)
				if user:

					# Log in the user to the service
					login_to_site(request, user)
					update_last_login(None, user = user)

					# Generate a user token
					tokens = AuthTokenFactory()
					token = tokens.make_token(user)

					return JsonResponse({
						'version': '0.1.0',
						'status': 200,
						'token': token,
						'user': {
							'id': user.user_id,
							'name': user.full_name,
							'email': user.email_address,
							'permissions': [ p.codename for p in user.all_permissions() ]
						}
					})

				return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)

		except ValidationError:
			return JsonResponse({ 'version': '0.1.0', 'status': 403 }, status = 403)
login = LoginView.as_view()

class LogoutView(View):

	@method_decorator(csrf_protect)
	@method_decorator(login_required)
	def get(self, request):

		logout_from_site(request)
		return JsonResponse({ 'version': '0.1.0',  'status': 200 })
logout = LogoutView.as_view()


class TokenValidationView(View):

	@method_decorator(csrf_protect)
	def get(self, request, id = '', token = ''):

		try: user = User.objects.select_subclasses().get(user_id = id)
		except User.DoesNotExist:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
		else:

			# Do not provide any details for any user other than ourselves
			tokens = AuthTokenFactory()
			is_valid = tokens.check_token(user, token)
			if request.user and (request.user.user_id == id and is_valid):

				return JsonResponse({
					'version': '0.1.0',
					'status': 200,
					'token': is_valid,
					'user': {
						'id': user.user_id,
						'name': user.full_name,
						'email': user.email_address,
						'permissions': [ p.codename for p in user.all_permissions() ]
					}
				})

			return JsonResponse({ 'version': '0.1.0', 'status': 200, 'token': is_valid })
validate = TokenValidationView.as_view()
