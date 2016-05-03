# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from django.utils.timezone import now
from collections import defaultdict
from django.db.models import *
from schedule import DayOfWeek
from _programs import Subject
from _base import (
	InheritanceManager,
	ActiveManager,
	Model,
)

__all__ = [
	'Course',
	'CourseSchedule',
	'AvailabilitySchedule',
	'Availability'
]

class ScheduleManager(InheritanceManager): pass
class Schedule(Model):

	expiry = DateTimeField(
		auto_now_add = False,
		auto_now = False,
		null = False,
		blank = False,
		verbose_name = _('expiration date'),
		help_text = """
			The expiration date for this schedule. Schedules are valid per semester, but since we don't
			really know when is the semester scheduled to begin, we leave this to the staff to decide.
		"""
	)

	@cached_property
	def entries_list(self):

		entries = defaultdict(list)
		subjects = {}

		for entry in self.entries.all():

			if entry.subject_id not in subjects:
				subjects[entry.subject_id] = Subject.objects.get_active(id = entry.subject_id)

			entries[entry.subject_id].append({ 'day': entry.day, 'time': entry.time })

		return [
			{
				'id': id,
				'code': subjects[id].code,
				'name': subjects[id].name,
				'slots': slots
			} for (id, slots) in entries.iteritems()
		]

	class Meta(object):
		abstract = True


class CourseSchedule(Schedule):

	entries = ManyToManyField('rhea.Course',
		related_name = 'schedule',
		related_query_name = 'schedule',
		verbose_name = _('schedule entries'),
		help_text = """
			This indicates a course is to be taken by a student or instructed by an instructor. Since
			this data is collected into the individual course object, we can relax the relationship and
			use courses as the middle-man between students, instructors, subjects, and time slots.
			Programming time is just so much fun!
		"""
	)

	class Meta(object):

		verbose_name = _('course schedule')
		verbose_name_plural = _('course schedules')
		app_label = 'rhea'

class CourseManager(ActiveManager): pass
class Course(Model):

	instructor = ForeignKey('rhea.Instructor',
		related_name = 'courses',
		null = False,
		verbose_name = _('course subject'),
		help_text = """
			The instructor for this course. Every course must have an instructor...
		"""
	)
	subject = ForeignKey('rhea.Subject',
		related_name = '+',
		null = False,
		verbose_name = _('course subject'),
		help_text = """
			The subject of the course. The subject may only be offered once a day. Stacking
			courses together counts only as one course and is thus valid. Stacking courses is
			understood to be vertically grouping two or more immediately consecutive courses into
			a single logical unit.
		"""
	)
	day = PositiveSmallIntegerField(
		choices = [ (value, day.value) for (value, day) in enumerate(DayOfWeek.__members__.values()) ],
		null = False,
		verbose_name = _('day of week'),
		help_text = """
			The day of the week in which the course takes place. Preferably, courses follow the
			following rules regarding placement by day of week:
				- The course is unique per day per student. If a course is immediately preceded by
				another course covering the same subject by the same instructor, it is assumed to
				be an extension to the current course and thus is valid.
				- If a course is given in Monday, giving the same course at Thursday at the same
				hour is preferred over stacking sessions. Likewise, it is preferred to have
				mirroring courses on Tuesday - Friday than stacking them.
				- If a course is given in Wednesday, it is preferred to stack it instead of spreading
				it through the week.
		"""
	)
	time = PositiveSmallIntegerField(
		choices = [
			(0, _('07:00')),
			(1, _('08:30')),
			(2, _('10:00')),
			(3, _('11:30')),
			(4, _('13:00')),
			(5, _('14:30')),
			(6, _('16:00')),
			(7, _('17:30')),
			(8, _('19:00')),
			(9, _('20:30'))
		],
		null = False,
		verbose_name = _('time slot'),
		help_text = """
			The time slot in which the lecture takes place. Time slots measure exactly 1:30 long. All
			courses must conform to this constraint in order to be located efficiently. Courses lasting
			3:00 or any other multiple of such time are considered as separate courses of 1:30 each.
		"""
	)

	class Meta(object):

		verbose_name = _('course')
		verbose_name_plural = _('courses')
		app_label = 'rhea'


class AvailabilitySchedule(Schedule):

	entries = ManyToManyField('rhea.Availability',
		related_name = 'schedule',
		verbose_name = _('schedule entries'),
		help_text = """
			Schedules are sparse matrices of entries. In this case, this is a sparse matrix of
			availability entries. Each availability entry represents a period of time per day
			in which the instructor may be assigned a course.
		"""
	)

	@cached_property
	def entries_list(self):
		return [ { 'day': e.day, 'time': e.time, 'level': e.level } for e in self.entries.all() ]

	class Meta(object):

		db_table = 'rhea_a_schedule'
		verbose_name = _('availability schedule')
		verbose_name_plural = _('availability schedules')
		app_label = 'rhea'
class Availability(Model):

	level = FloatField(
		choices = [
			(0.0, _('Not available')),
			(0.25, _('Mealtime')),
			(0.5, _('If required')),
			(1.0, _('Available'))
		],
		null = False,
		default = 0.0,
		verbose_name = _('availability level'),
		help_text = """
			The level of availability this availability slot represents. 0.0 implies the slot is
			unavailable for selection whereas 1.0 implies the slot is absolutely available for
			selection.
		"""
	)
	day = PositiveSmallIntegerField(
		choices = [ (value, day.value) for (value, day) in enumerate(DayOfWeek.__members__.values()) ],
		null = False,
		verbose_name = _('day of week')
	)
	time = PositiveSmallIntegerField(
		choices = [
			(0, _('07:00')),
			(1, _('08:30')),
			(2, _('10:00')),
			(3, _('11:30')),
			(4, _('13:00')),
			(5, _('14:30')),
			(6, _('16:00')),
			(7, _('17:30')),
			(8, _('19:00')),
			(9, _('20:30'))
		],
		null = False,
		verbose_name = _('time slot')
	)

	class Meta(object):

		db_table = 'rhea_a_entry'
		verbose_name = _('availability entry')
		verbose_name_plural = _('availability entries')
		app_label = 'rhea'
