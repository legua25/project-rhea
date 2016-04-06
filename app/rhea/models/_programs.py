# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from operator import add as __add__
from django.db.models import *
from _base import (
	ActiveManager,
	Model,
)

__all__ = [
	'AcademicProgram',
	'Subject',
	'Requirement',
	'Specialty'
]

def _upload_to(instance, filename): return 'institution/%s/profile.html' % instance.acronym.lower()

class ProgramManager(ActiveManager): pass
class AcademicProgram(Model):

	acronym = CharField(
		max_length = 8,
		null = False,
		blank = False,
		unique = True,
		db_index = True,
		verbose_name = _('acronym'),
		help_text = """
			An acronym given to the academic program for identification purposes. Since text searches
			are not gracefully handled by the database, we cannot use this as the primary key, although
			it acts like such.
		"""
	)
	name = CharField(
		max_length = 256,
		null = False,
		blank = False,
		verbose_name = _('program full name'),
		help_text = """
			The academic program's user-friendly name, as provided by the institution's program
			portfolio. The name is purely aesthetic and is not used by the generator in any way.
		"""
	)
	graduate_profile = FileField(
		upload_to = _upload_to,
		null = True,
		verbose_name = _('graduate profile'),
		help_text = """
			This is an *.html file which contains the graduate profile for the program's profile to
			showcase. If provided, the contents of this file will be processed and rendered along with
			the program's profile information.
		"""
	)

	objects = ProgramManager()

	@cached_property
	def subjects(self):

		query = self.requirements.all().filter(active = True).values_list('dependent_id', flat = True)
		return Subject.objects.active(id__in = query)

	class Meta(object):

		verbose_name = _('academic program')
		verbose_name_plural = _('academic programs')
		app_label = 'rhea'

class SubjectManager(ActiveManager):

	def by_instructor(self, instructor):
		return self.active(id__in = Specialty.objects.by_confidence(instructor.id))
	def ancestors(self, subjects, program):

		query = reduce(__add__, [ list(subject.ancestors(program).values_list('id', flat = True)) for subject in subjects ])
		return self.active(id__in = query)
	def descendants(self, subjects, program):

		query = reduce(__add__, [ list(subject.descendants(program).values_list('id', flat = True)) for subject in subjects ])
		return self.active(id__in = query)
	def candidates_for(self, program, semester, subjects):

		# Determine what subject have we coursed already (including the current ones) and the list of what's missing
		coursed = (list(self.ancestors(subjects, program)) + [ s.id for s in subjects ])
		pending = list(self.descendants(subjects, program))
		candidates = []

		# For each subject in pending...
		for subject in pending:

			# Get dependencies for the current subject
			dependencies = Requirement.objects.dependencies_for(program.id, subject)

			# If it has no dependencies, it's a candidate
			if dependencies.count() == 0: candidates.append(subject)
			# If all dependencies are included in the coursed set, it's also a candidate
			elif all(dependency in coursed for dependency in dependencies): candidates.append(subject)

		query = (Q(dependent_id__in = candidates) | (Q(semester__range = [ 1, semester + 1 ]) & ~Q(dependent_id__in = candidates + coursed)))
		query = Requirement.objects.active(query).values_list('dependent_id', flat = True)
		return Subject.objects.active(id__in = query)
class Subject(Model):

	code = CharField(
		max_length = 16,
		null = False,
		blank = False,
		unique = True,
		verbose_name = _('subject code'),
		help_text = """
			A subject code provided by the institution to uniquely identify a subject. This is used
			primarily to query for dependencies or followup candidates, if any. As per the project's
			scope, we are not considering "variants" nor equivalencies in this design.
		"""
	)
	name = CharField(
		max_length = 256,
		null = False,
		blank = False,
		verbose_name = _('subject name'),
		help_text = """
			This is the user-friendly version of this subject, used only by the program's profile to
			showcase the composing subjects and their dependencies.
		"""
	)
	hours = PositiveSmallIntegerField(
		default = 1,
		verbose_name = _('hours per week'),
		help_text = """
			This is a measurement of the expected time, in hours per week, a course for this subject
			should use. The provided value is divided by 1.5 (since our blocks are assumed to be of
			1.5 hours length). This is used to determine the most probable arrangement for the course
			by the generator.
		"""
	)

	objects = SubjectManager()

	def dependencies(self, program):

		# Requirements operate on IDs, so we must convert the result to subject instances
		subjects = Requirement.objects.dependencies_for(program.id, self.id)
		return Subject.objects.active(id__in = subjects)
	def dependents(self, program):

		# Requirements operate on IDs, so we must convert the result to subject instances
		subjects = Requirement.objects.dependents_for(program.id, self.id)
		return Subject.objects.active(id__in = subjects)
	def ancestors(self, program):

		# Requirements operate on IDs, so we must convert the result to subject instances
		subjects = Requirement.objects.ancestors_for(program.id, self.id)
		return Subject.objects.active(id__in = subjects)
	def descendants(self, program):

		# Requirements operate on IDs, so we must convert the result to subject instances
		subjects = Requirement.objects.descendants_for(program.id, self.id)
		return Subject.objects.active(id__in = subjects)

	class Meta(object):

		verbose_name = _('subject')
		verbose_name_plural = _('subjects')
		app_label = 'rhea'


class RequirementManager(ActiveManager):

	def dependencies_for(self, program, subject):

		# We must convert the requirement to a list of subject IDs so the subject may convert them back
		query = self.select_related('dependent', 'dependency').filter(dependent_id = subject, program_id = program, active = True)
		return query.values_list('dependency_id', flat = True)
	def dependents_for(self, program, subject):

		# We must convert the requirement to a list of subject IDs so the subject may convert them back
		query = self.select_related('dependent', 'dependency').filter(dependency_id = subject, program_id = program, active = True)
		return query.values_list('dependent_id', flat = True)
	def ancestors_for(self, program, subject):

		# Ancestry traversal is a recursive operation - from each dependency to the leaves
		def traverse_ancestry(query, output, current, group):

			# Add the current element to the ancestors set
			output.add(current)

			# For each dependency to this one, recursively add them to the ancestors set
			_dependencies = query.dependencies_for(program, current)
			for _dep in _dependencies:
				traverse_ancestry(query, output, _dep, group)

		# The ancestors set is initially empty - it must skip the current element, as we're only querying for the ancestors, not the current elemnt
		ancestors = set()
		dependencies = self.dependencies_for(program, subject)

		for dependency in dependencies:
			traverse_ancestry(self, ancestors, dependency, program)

		return ancestors
	def descendants_for(self, program, subject):

		# Ancestry traversal is a recursive operation - from each dependency to the leaves
		def traverse_descentants(query, output, current, group):

			# Add the current element to the ancestors set
			output.add(current)

			# For each dependency to this one, recursively add them to the ancestors set
			_dependents = query.dependents_for(program, current)
			for _dep in _dependents:
				traverse_descentants(query, output, _dep, group)

		# The ancestors set is initially empty - it must skip the current element, as we're only querying for the ancestors, not the current elemnt
		descendants = set()
		dependencies = self.dependents_for(program, subject)

		for dependency in dependencies:
			traverse_descentants(self, descendants, dependency, program)

		return descendants
class Requirement(Model):

	dependency = ForeignKey('rhea.Subject',
		related_name = '+',
		null = True,
	    verbose_name = _('dependency'),
	    help_text = """
	        A pointer to a subject that is required by the dependent - this stands for the backwards
	        side of the relationship and allows for ancestral navigation in the graph.
	    """
	)
	dependent = ForeignKey('rhea.Subject',
		related_name = '+',
		related_query_name = 'requirements',
		null = True,
	    verbose_name = _('dependent'),
	    help_text = """
	        A pointer to a subject that requires the dependency - this stands for the forward side of
	        the relationship and allows for candidate estimation and progress tracking given a starting
	        set.
	    """
	)
	program = ForeignKey('rhea.AcademicProgram',
		related_name = 'requirements',
		verbose_name = _('academic program'),
		help_text = """
			The academic program this requirement belongs to. Requirements act as graph edges for the
			study plan's graph - they connect subjects with subjects through a "is required" relationship.
			Keeping the relationship separate from the subjects allows recycling subjects for different
			academic programs.
		"""
	)
	semester = PositiveSmallIntegerField(
		verbose_name = _('minimum semester'),
		help_text = """
			The minimum semester in which this course should be taken. Courses that deviate from the
			current semester for a specific student by more than 1 unit upwards are note eligible as
			candidates for next semester topics.
		"""
	)

	objects = RequirementManager()

	class Meta(object):

		verbose_name = _('subject requirement')
		verbose_name_plural = _('subject requirements')
		app_label = 'rhea'

class SpecialtyManager(ActiveManager):

	def by_confidence(self, instructor):

		query =  self.select_related('subject').active(instructor_id = instructor)
		return query.order_by('-confidence').values_list('subject_id', flat = True)
class Specialty(Model):

	subject = ForeignKey('rhea.Subject',
		related_name = '+',
		verbose_name = _('specialty subject'),
		help_text = """
			A pointer to the subject to which the instructor has a specialty on.
		"""
	)
	instructor = ForeignKey('rhea.Instructor',
		related_name = 'specialties',
		verbose_name = _('instructor'),
		help_text = """
			The instructor who features a specialty in the given subject. Specialties are specified
			and ranked by the instructor
		"""
	)
	confidence = FloatField(
		null = False,
		default = 0.5,
		verbose_name = _('confidence factor'),
		help_text = """
			The confidence factor is a number from 0.0 to 1.0 inclusive which allows instructors
			to rank subjects based on their particular specialties. Confidence factors are personal
			and involve elements such as experience in the particular subject, personal preference
			for the given subject and availability. 0.0 implies "would not instruct", whereas 1.0
			implies "will definitely instruct".
		"""
	)

	objects = SpecialtyManager()

	class Meta(object):

		verbose_name = _('specialty subject')
		verbose_name_plural = _('specialty subjects')
		app_label = 'rhea'
