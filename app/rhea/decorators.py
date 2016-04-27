# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from base64 import b64decode

def ajax_required(view):
	""" AJAX request required decorator
		From <"https://djangosnippets.org/snippets/771/">

	@ajax_required
	def my_view(request):
	....

	"""

	def wrap(request, *args, **kwargs):

		if not request.is_ajax(): return HttpResponseBadRequest()
		return view(request, *args, **kwargs)

	wrap.__doc__ = view.__doc__
	wrap.__name__ = view.__name__

	return wrap
def role_required(role, login_url = None, raise_exception = False):

	def has_role(user):

		if not isinstance(role, (list, tuple)): roles = ( role, )
		else: roles = role

		for r in roles:

			if not user.belongs_to(name = r):

				if raise_exception: raise PermissionDenied()
				return False

		return True

	return user_passes_test(has_role, login_url = login_url)
def token_required(view):

	def wrap(request, *args, **kwargs):

		basic_auth = request.META.get('HTTP_AUTHORIZATION')
		if basic_auth:

			method, payload = basic_auth.split(' ', 1)

			if method.lower() == 'basic':

				auth_str = b64decode(payload.strip())
				id, token = auth_str.decode().split(':', 1)

				if id and token:

					user = authenticate(id = id, token = token)
					if user:

						request.user = user
						request.token = token

						return view(request, *args, **kwargs)
				return HttpResponseForbidden('Must include the "id" and "token" parameters with request')
		return HttpResponseForbidden()

	wrap.__doc__ = view.__doc__
	wrap.__name__ = view.__name__

	return wrap
