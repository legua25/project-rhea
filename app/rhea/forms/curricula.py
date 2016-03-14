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

	dependency = ModelChoiceField(
		queryset = Subject.objects.active(),
		required = True,
		widget = HiddenInput()
	)
	dependent = ModelChoiceField(
		queryset = Subject.objects.active(),
		empty_label = None,
		required = False
	)

	def clean(self):

		data = self.cleaned_data
		dependency = data['dependency']
		dependent = data['dependent']

		if dependent is not None:
			if dependency.id == dependent.id:
				raise ValidationError('Dependency cannot refer to itself')

	class Meta(object):

		model = Dependency
		fields = [ 'dependency', 'dependent' ]

DependencyFormSet = formset_factory(DependencyForm, extra = 0)
