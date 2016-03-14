# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from app.rhea.models import AcademicProgram, Subject, Dependency
from django.core.urlresolvers import reverse
from django.core.validators import *
from django.forms import *

__all__ = [
	'ProgramForm',
	'SubjectForm',
	'DependencyForm',
	'DependencyFormSet'
]

class ProgramForm(ModelForm):
	""" Allows a single academic program to be created or edited """

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

	class Meta(object):

		model = AcademicProgram
		fields = [ 'acronym', 'name', 'description' ]

class SubjectForm(ModelForm):
	""" Allows a single subject to be created """

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
	class Meta(object):

		model = Subject
		fields = [ 'code', 'name' ]
class DependencyForm(ModelForm):
	""" Allows the dependencies of an existing subject to be edited """

	dependencies = ModelMultipleChoiceField(
		queryset = Subject.objects.active(),
		required = False,
		widget = CheckboxSelectMultiple()
	)
	program = ModelChoiceField(
		queryset = AcademicProgram.objects.active(),
		required = True
	)

	class Meta(object):

		model = Subject
		fields = [ 'dependencies' ]

DependencyFormSet = modelformset_factory(Subject, form = DependencyForm, extra = 0)
