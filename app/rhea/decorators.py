# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest

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
			if not user.belongs_to(codename = r):

				if raise_exception: raise PermissionDenied()
				return False

		return True

	return user_passes_test(has_role, login_url = login_url)
def permission_required(perm, login_url = None, raise_exception = False):

	def has_permission(user):

		if not isinstance(perm, (tuple, list)): perms = ( perm, )
		else: perms = perm

		for p in perms:
			if not user.has_permission(codename = p):

				if raise_exception: raise PermissionDenied()
				return False

		return True

	return user_passes_test(has_permission, login_url = login_url)
