# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.template import Library

register = Library()

@register.filter
def has_role(user, role_name):
	return user.belongs_to(codename = role_name)

@register.filter
def has_permission(user, permission_name):
	return user.has_permission(codename = permission_name)
