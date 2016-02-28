# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
from app.rhea.models import AnonymousUser
from django.core.validators import *
from django.forms import *

__all__ = [ 'LoginForm' ]

class LoginForm(Form):

	USER_ID_PATTERN = r'^[AaLl][\d]+'

	user_id = CharField(
		max_length = 16,
		strip = True,
		validators = [ RegexValidator(USER_ID_PATTERN, message = _('Provided ID is invalid')) ],
		widget = TextInput(attrs = { 'placeholder': _('Enroll or payroll ID') })
	)
	password = CharField(
		max_length = 128,
		strip = True,
		widget = PasswordInput(attrs = { 'placeholder': _('Password') })
	)
	user = AnonymousUser()

	def clean(self):

		user_id, password = self.cleaned_data['user_id'], self.cleaned_data['password']
		user = authenticate(user_id = user_id, password = password)

		if user is not None:

			if user.is_active: self.user = user
			else: raise ValidationError(_('User was not found or is invalid'))

		else: raise ValidationError(_('Invalid user ID or password'))
