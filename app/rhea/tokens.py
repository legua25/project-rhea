# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36
from app.rhea.models import Instructor, Student
from django.utils import six
from datetime import date

__all__ = [
	'AuthTokenFactory',
	'InstructorTokenFactory',
	'StudentTokenFactory'
]

def _days_in(dt): return (dt - date(2001, 1, 1)).days

class AbstractTokenFactory(object):
	""" Burrowed from Django's PasswordResetTokenGenerator """

	salt = None
	timeout_days = None
	token_split = '-'

	def __init__(self, salt = None, timeout_days = None):

		self.salt = salt or self.__class__.salt
		self.timeout_days = timeout_days or self.__class__.timeout_days

	def make_token(self, user):
		return self._make_token(user, _days_in(date.today()) + self.timeout_days)
	def check_token(self, user, token):

		try:

			timestamp_b36, hash = token.split(self.token_split)
			timestamp = base36_to_int(timestamp_b36)

		except ValueError: return False
		else:

			if not constant_time_compare(self._make_token(user, timestamp), token):
				return False

			if ((_days_in(date.today()) + self.timeout_days) - timestamp) > 0:
				return False

			return True

	def _make_token(self, user, timestamp):

		timestamp_b36 = int_to_base36(timestamp)

		hash = salted_hmac(self.salt, self._make_user_hash(user, timestamp)).hexdigest()[::2]
		return '%s%s%s' % (timestamp_b36, self.token_split, hash)
	def _make_user_hash(self, user, timestamp): raise NotImplementedError()

class AuthTokenFactory(AbstractTokenFactory):

	salt = 'app.rhea.tokens.AuthTokenFactory'
	timeout_days = 1

	def _make_user_hash(self, user, timestamp):

		last_login = '' if user.last_login is None else user.last_login.replace(microsecond = 0, tzinfo = None)
		return (user.user_id + user.password + six.text_type(last_login) + six.text_type(timestamp))
class InstructorTokenFactory(AbstractTokenFactory):

	salt = 'app.rhea.tokens.InstructorTokenFactory'
	timeout_days = 1

	def _make_user_hash(self, user, timestamp):

		assert isinstance(user, Instructor)

		last_confirmed = '' if user.last_confirmation is None else user.last_confirmation.replace(microsecond = 0, tzinfo = None)
		return (user.user_id + user.password + six.text_type(last_confirmed) + six.text_type(timestamp))
class StudentTokenFactory(AbstractTokenFactory):

	salt = 'app.rhea.tokens.StudentTokenFactory'
	timeout_days = 1

	def _make_user_hash(self, user, timestamp):

		assert isinstance(user, Student)

		last_confirmed = '' if user.last_confirmation is None else user.last_confirmation.replace(microsecond = 0, tzinfo = None)
		return (user.user_id + user.password + six.text_type(last_confirmed) + six.text_type(timestamp))
