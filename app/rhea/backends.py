# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from app.rhea.tokens import AuthTokenFactory
from django.conf import settings

User = get_user_model()

class ModelTokenBackend(object):

	TOKEN_FACTORY = AuthTokenFactory()

	def authenticate(self, id, token):

		try: user = User.objects.select_subclasses().filter(user_id = id)
		except User.DoesNotExist: return None
		else:

			if user.active and ModelTokenBackend.TOKEN_FACTORY.check_token(user, token):
				return user

			return None
