# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from app.rhea.models import AcademicProgram, Subject, Dependency
from django.core.validators import *
from django.forms import *

__all__ = [
	'ProgramForm',
	'SubjectForm'
]

class ProgramForm(Form):

	acronym = CharField(
		max_length = 8,
		min_length = 1,
		strip = True,
		required = True,
		widget = TextInput(attrs = { 'placeholder': _('Program Acronym') })
	)
	name = CharField(
		max_length = 128,
		min_length = 4,
		strip = True,
		required = True,
		widget = TextInput(attrs = { 'placeholder': _('Program Name') })
	)
	description = CharField(
		max_length = 512,
		strip = True,
		initial = '',
		required = False,
		widget = Textarea(attrs = { 'style': 'resize: none', 'placeholder': _('Brief description of the program') })
	)

	_instance = None

	def clean(self):

		data = self.cleaned_data

		# Gather the program instance data
		acronym = data['acronym'].upper()
		name = data['name']
		description = data['description']

		# Create the instance
		self._instance = AcademicProgram(
			acronym = acronym,
			name = name,
			description = description
		)
	def save(self, using = None):

		if self._instance is not None:
			self._instance.save(using = using)

		return self._instance


class SubjectForm(Form):

	code = SlugField(
		max_length = 8,
		min_length = 1,
		allow_unicode = True,
		strip = True,
		required = True,
		widget = TextInput(attrs = { 'placeholder': 'Subject Code' })
	)
	name = CharField(
		max_length = 256,
		min_length = 8,
		required = True,
		widget = TextInput(attrs = { 'placeholder': 'Subject Name' })
	)
