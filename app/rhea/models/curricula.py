# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from django.db.models import *
from _base import Model, ActiveManager

__all__ = [
	'AcademicProgram',
	'Subject',
	'Dependency'
]

class AcademicProgramManager(ActiveManager): pass
class AcademicProgram(Model):

	acronym = CharField(
		max_length = 8,
		null = False,
		blank = False,
		unique = True,
		verbose_name = _('program acronym')
	)
	name = CharField(
		max_length = 128,
		null = False,
		blank = False,
		verbose_name = _('program name')
	)
	description = CharField(
		max_length = 512,
		null = False,
		default = '',
		verbose_name = _('program description')
	)

	@cached_property
	def subjects(self): return Subject.objects.active(id__in = self.subject_graph.values_list('id', flat = True))

	objects = AcademicProgramManager()

	def __str__(self): return ('(%s) %s' % (self.acronym, self.name)).encode('utf-8')

	class Meta(object):
		db_table = 'rhea_programs'
		verbose_name = _('academic program')
		verbose_name_plural = _('academic programs')
		app_label = 'rhea'


class SubjectManager(ActiveManager): pass
class Subject(Model):

	code = SlugField(
		max_length = 8,
		allow_unicode = False,
		db_index = True,
		unique = True,
		verbose_name = _('subject code')
	)
	name = CharField(
		max_length = 256,
		null = False,
		blank = False,
		verbose_name = _('subject name')
	)
	dependencies = ManyToManyField('self',
	    related_name = 'dependents',
		through = 'rhea.Dependency',
	    through_fields = [ 'dependent', 'dependency' ],
		symmetrical = False,
		verbose_name = _('dependencies')
	)

	objects = SubjectManager()

	def depends_on(self, dependency):

		# A simple assertion to check we're getting the right type here
		assert isinstance(dependency, Subject)

		# Linear dependency is the simplest - if it is a direct dependency, it's a match
		if dependency.id in self.dependencies.all().values_list('id', flat = True): return True
		else:

			# Indirect dependency is a little bit harder...
			# For each dependency, check if the dependency is a dependency - if it is, then it's a match
			for dep in self.dependencies.all():
				if dep.depends_on(dependency): return True

			# We fall through without coincidences - this is a fail
			else: return False
	def dependency_of(self, dependent): return dependent.depends_on(self)

	def __str__(self): return ('(%s) %s' % (self.code, self.name)).encode('utf-8')

	class Meta(object):
		verbose_name = _('subject')
		verbose_name_plural = _('subjects')
		app_label = 'rhea'

class DependencyManager(ActiveManager): pass
class Dependency(Model):

	dependency = ForeignKey('rhea.Subject',
		related_name = '+',
		verbose_name = _('dependency')
	)
	dependent = ForeignKey('rhea.Subject',
		related_name = '+',
		verbose_name = _('dependent')
	)
	program = ForeignKey('rhea.AcademicProgram',
        related_name = 'subject_graph',
        related_query_name = 'graph',
        null = True,
        verbose_name = _('academic program')
    )

	objects = DependencyManager()

	class Meta(object):
		verbose_name = _('dependency')
		verbose_name_plural = _('dependencies')
		app_label = 'rhea'
