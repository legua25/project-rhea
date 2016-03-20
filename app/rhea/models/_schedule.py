# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.db.models import *
from _base import (
	ActiveManager,
	Model,
)

__all__ = [
	'Course',
	'Schedule'
]

class CourseManager(ActiveManager): pass
class Course(Model):

	instructor = ForeignKey('rhea.Instructor',
		related_name = 'courses',
		verbose_name = _('instructor'),
		help_text = """
			Courses is a list of all courses, past and present, which the instructor provided.
			This field is provided for historic reasons and is not actually used by the generator
			to calculate the new schedules.
		"""
	)
	students = ManyToManyField('rhea.Student',
		related_name = 'courses',
		verbose_name = _('students'),
		help_text = """
            Courses is a list of all courses, past and present, which the student participated in.
            This field is provided for historic reasons and is not actually used by the generator
            to calculate the new schedules.
        """
	)
	subject = ForeignKey('rhea.Subject',
		related_name = 'courses',
		verbose_name = _('lecture subject'),
		help_text = """
			The subject of the lecture series. This is not connected to specific requirements since
			the subject may be present for more than one academic program and thus would create a
			humongous amount of data duplication which is avoidable.
		"""
	)
	date_started = DateTimeField(
		auto_now_add = False,
		auto_now = False,
		null = True,
		verbose_name = _('date started'),
		help_text = """
			This sets the date in which the course started. Dates are subject to the institution's
			policies regarding academic periods and must be set manually afterwards. Good thing this
			can be a batch operation if we take into account the final schedules.
		"""
	)
	date_ended = DateTimeField(
		auto_now_add = False,
		auto_now = False,
		null = True,
		verbose_name = _('date ended'),
		help_text = """
			This sets the date in which the course officially ended. Dates are subject to the
			institution's policies regarding academic periods and must be set manually afterwards.
			Good thing this can be a batch operation if we take into account the final schedules.
		"""
	)

	objects = CourseManager()

	class Meta(object):

		verbose_name = _('course')
		verbose_name_plural = _('courses')
		app_label = 'rhea'

def _upload_to(instance, filename):

	if instance.type == 0:
		return 'users/%s/schedule-%s.bson' % (instance.student.user_id, instance.date_created.strftime('%b-%d-%Y'))
	elif instance.type == 1:
		return 'users/%s/schedule-%s.bson' % (instance.instructor.user_id, instance.date_created.strftime('%b-%d-%Y'))
	else:
		return 'users/%s/schedule-work-%s.bson' % (instance.user.user_id, instance.date_created.strftime('%b-%d-%Y'))

class ScheduleManager(ActiveManager): pass
class Schedule(Model):

	type = PositiveSmallIntegerField(
		choices = [
			(0, _('Student academic schedule')),
			(1, _('Instructor academic schedule')),
			(2, _('Instructor work preference schedule'))
		],
		null = False,
		blank = False,
		verbose_name = _('schedule type'),
		help_text = """
			The type of schedule we're storing. We use this to determine where should we show the
			schedule, how should we name it and to whom should we relate it to, since students have
			one schedule and instructors have two.
		"""
	)
	data = FileField(
		upload_to = _upload_to,
		verbose_name = _('schedule data file'),
		help_text = """
			The actual schedule, as a *.bson file. We chose this representation because we must store
			a set of sparse data representing time slots, pointers to instructors and pointers to
			courses. Storing in the RDBMS, although it may seem as a nice option, will cause a lot of
			wasted resources per query where we need a free-form approach for data which will tend not
			to mutate further as time goes by. Note that, per scope, we're disregarding dropping out
			of courses as a valid action and we disallow it for simplicity.
		"""
	)
	expiry = DateField(
		auto_now = False,
		auto_now_add = False,
		null = False,
		blank = False,
		verbose_name = _('expiry date'),
		help_text = """
			The date in which this schedule was created. Since we use an expiry system with schedules
			to deallocate them when done being useful, we must record the expiry date to compare it
			with today's date to check if the schedule is still valid.
		"""
	)

	objects = ScheduleManager()

	class Meta(object):

		verbose_name = _('academic schedule')
		verbose_name_plural = _('academic schedules')
		app_label = 'rhea'
