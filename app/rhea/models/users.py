# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Permission
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.db.models import *
from _base import Model, ActiveManager

__all__ = [
	'User',
	'Role'
]

class UserManager(ActiveManager, BaseUserManager):

	def _create(self, user_id = None, full_name = None, email_address = None, password = None, **kwargs):

		if email_address is None: raise ValueError('Email address cannot be null')
		if user_id is None: raise ValueError('User ID cannot be null')
		if full_name is None: raise ValueError('Full name cannot be null')

		email = UserManager.normalize_email(email_address)
		user = self.model(
			user_id = user_id,
			email_primary = email,
			full_name = full_name,
			date_registered = now(),
			**kwargs
		)

		user.set_password(password)
		user.save()

		return user

	# TODO: Superusers here have the "Administrator" role - this fixture should be registered beforehand
	def create_user(self, user_id, full_name, email_address, password = None, **extra_fields):
		return self._create(user_id, full_name, email_address, password, **extra_fields)
	def create_superuser(self, user_id, full_name, email_address, password, **extra_fields):
		return self._create(user_id, full_name, email_address, password, **extra_fields)
class User(Model, AbstractBaseUser):

	user_id = CharField(
		max_length = 16,
		null = False,
		blank = False,
		unique = True,
		verbose_name = _('enrollment ID')
	)
	date_registered = DateTimeField(
		auto_now_add = True,
		verbose_name = _('date registered')
	)
	full_name = CharField(
		max_length = 1024,
		null = False,
		blank = False,
		verbose_name = _('full name')
	)
	email_primary = EmailField(
		max_length = 255,
		null = False,
		blank = False,
		unique = True,
		verbose_name = _('primary email address')
	)
	email_secondary = EmailField(
		max_length = 255,
		null = True,
		blank = True,
		verbose_name = _('secondary (backup) email address')
	)
	role = ForeignKey('rhea.Role',
		related_name = 'members',
	    null = True,
	    default = None,
		verbose_name = _('user role')
	)

	objects = UserManager()

	USERNAME_FIELD = 'enroll_id'
	REQUIRED_FIELDS = [ 'full_name' ]

	@property
	def is_active(self): return self.active

	def get_full_name(self): return self.full_name
	def get_short_name(self): return self.full_name
	def belongs_to(self, **kwargs):

		def _belongs(role, target):

			if role is None: return False

			if role.id == target.id: return True
			return _belongs(role.parent, target)

		return _belongs(self.role, Role.objects.get(active = True, **kwargs))

	def __str__(self): return 'User (id: %s, full-name: %s)' % (self.user_id, self.full_name)
	def __repr__(self): return self.__str__()

	class Meta(object):
		verbose_name = _('user')
		verbose_name_plural = _('users')
		app_label = 'rhea'


class RoleManager(ActiveManager): pass
class Role(Model):

	name = CharField(
		max_length = 64,
		null = False,
		blank = False,
		verbose_name = _('role name')
	)
	description = CharField(
		max_length = 512,
		null = False,
		default = '',
		verbose_name = _('role description')
	)
	parent = ForeignKey('self',
	    null = True,
	    blank = True,
		verbose_name = _('parent role')
	)
	_permissions = ManyToManyField(Permission,
		related_name = 'roles',
	    related_query_name = 'role',
		verbose_name = _('permissions')
	)

	objects = RoleManager()

	@cached_property
	def permissions(self):

		query = self._permissions_query()
		return Permission.objects.filter(query)

	def _permissions_query(self, query = None):

		if query is None: query = Q(role__id = self.id)
		if self.parent is not None:
			query = (query | self.parent._permissions_query(query = query))

		return query

	def __str__(self): return 'Role (name: %s, parent: %s)' % (self.name, self.parent if self.parent is not None else 'none')
	def __repr__(self): return self.__str__()

	class Meta(object):
		verbose_name = _('user role')
		verbose_name_plural = _('user roles')
		app_label = 'rhea'
