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
		required = True,
		widget = TextInput(attrs = { 'placeholder': 'Subject Name' })
	)
	class Meta(object):

		model = Subject
		fields = [ 'code', 'name' ]
class DependencyForm(Form):
	""" Allows the dependencies of an existing subject to be edited """

	subject = ModelChoiceField(
		queryset = Subject.objects.active(),
		empty_label = None,
		required = False,
		widget = HiddenInput()
	)
	dependency = ModelChoiceField(
		queryset = Subject.objects.active(),
		empty_label = None,
		required = False,
		widget = HiddenInput()
	)
	program = ModelChoiceField(
		queryset = AcademicProgram.objects.active(),
		empty_label = None,
		required = True
	)

	instance = {}

	def clean(self):

		data = self.cleaned_data

		subject = data['subject']
		dependency = data['dependency']
		program = data['program']

		if subject is not None:
			if dependency.id == subject.id: raise ValidationError('Dependencies cannot be recursive')

		self.instance['subject'] = subject
		self.instance['dependency'] = dependency
		self.instance['program'] = program
	def save(self, subject = None):

		if self.instance['subject'] is None:

			if subject is None: raise ValueError('Cannot save form because there is no dependent subject')
			self.instance['subject'] = subject

		subject = self.instance['subject']
		dependency = self.instance['dependency']
		program = self.instance['program']

		# Save the individual instances, then save the dependency
		subject.save()
		dependency.save()

		# Check if the dependency exists - if so, skip it
		dependency_exists = Dependency.objects.filter(dependent_id = subject, dependency_id = dependency, program_id = program).exists()
		if not dependency_exists:
			return Dependency.objects.create(
				dependent = self.instance['subject'],
				dependency = self.instance['dependency'],
				program = self.instance['program']
			)


DependencyFormSet = formset_factory(DependencyForm, extra = 0)
