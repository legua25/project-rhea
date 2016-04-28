# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.db.models import *
from _base import (
	ActiveManager,
	Model,
)

__all__ = [
	'Role',
	'Permission'
]

class RoleManager(ActiveManager): pass
class Role(Model):

	codename = CharField(
		max_length = 32,
		null = False,
		blank = False,
		unique = True,
		verbose_name = _('role code name'),
		help_text = """
			The code name given to this role. This is used by the permission decorators to determine
			which role or roles should the current user have to be eligible for a certain page or
			action.
		"""
	)
	name = CharField(
		max_length = 64,
		null = False,
		default = '',
		verbose_name = _('role name'),
		help_text = """
			A user-friendly name for this role, to make this selectable from the user administration
			page.
		"""
	)
	base = ForeignKey('self',
	    related_name = 'subroles',
	    null = True,
		verbose_name = _('base role'),
		help_text = """
			If provided, this specifies a base role from which to inherit permissions. This essentially
			creates a permission chain through which we must go to check for permissions. If the current
			role doesn't define the permission but it has a base role, the base role is recursively
			queried until either the permission is found or all possibilities are exhausted.
		"""
	)
	permissions = ManyToManyField('rhea.Permission',
		related_name = 'roles',
		verbose_name = _('role permissions'),
		help_text = """
			A list of all permission tokens this role is entitled to. Roles also inherit permissions
			from their parent roles (if any).
		"""
	)

	objects = RoleManager()

	def is_of_type(self, codename):

		# We use tail recursion here to amortize the cost of traversing the prototype chain
		def has_codename(role, codename):

			if role.codename == codename: return True
			elif role.base is not None: return has_codename(role.base, codename)

			return False

		return has_codename(self, codename)
	def has_permission(self, perm):

		if not isinstance(perm, (tuple, list)): permissions = [ perm ]
		else: permissions = perm

		# We use a function here to traverse recursively using tail recursion to minimize impact
		def has_perm(role, perm):

			if role.permissions.filter(codename__iexact = perm).exists(): return True
			elif role.base is not None: return has_perm(role.base, perm)

			return False

		# All permissions must be granted or it's a fail
		return all([ has_perm(self, perm) for perm in permissions ])
	def all_permissions(self):

		perms = { p for p in self.permissions.all().filter(active = True) }
		if self.base is not None: perms |= self.base.all_permissions()

		return perms

	class Meta(object):

		verbose_name = _('user role')
		verbose_name_plural = _('user roles')
		app_label = 'rhea'


class PermissionManager(ActiveManager): pass
class Permission(Model):

	codename = CharField(
		max_length = 32,
		null = False,
		blank = False,
		unique = True,
		verbose_name = _('permission code name'),
		help_text = """
			The code name given to this permission. This is used by the permission decorators to
			determine which permissions should the current user have to be eligible for a certain
			page or action.
		"""
	)
	name = CharField(
		max_length = 64,
		null = False,
		default = '',
		verbose_name = _('permission name'),
		help_text = """
			A user-friendly name for this permission, to make this selectable from the user
			administration page.
		"""
	)

	objects = PermissionManager()

	class Meta(object):

		verbose_name = _('permission')
		verbose_name_plural = _('permissions')
		app_label = 'rhea'
