# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from imagekit.models.fields import ProcessedImageField
from django.utils.functional import cached_property
from django.core.validators import RegexValidator
from pilkit.processors import SmartCrop
from django.utils.timezone import now
from django.db.models import *
from _base import (
	InheritanceManager,
	Model,
)

__all__ = [
	'User',
	'Student',
	'Instructor'
]

def _upload_to(instance, filename): return 'users/%s/picture.png' % instance.user_id

class UserManager(InheritanceManager, BaseUserManager):

	def create(self, password = None, **kwargs):

		kwargs.setdefault('date_registered', now())

		user = self.model(**kwargs)
		user.set_password(password)
		user.save(using = self._db)

		return user
	def create_user(self, user_id, password = None, **kwargs):
		return self.create(password = password, user_id = user_id, **kwargs)
	def create_superuser(self, user_id, password, **kwargs):
		return self.create(password = password, user_id = user_id, **kwargs)
class User(Model, AbstractBaseUser):

	user_id = CharField(
		max_length = 16,
		null = False,
		blank = False,
		unique = True,
		db_index = True,
		validators = [ RegexValidator(regex = r'^[LA][\d]+$') ],
		verbose_name = _('user ID'),
	    help_text = """
            The user ID, which can be either an enrollment ID in the case of a student or a
            payroll ID in the case of any other person (instructor or staff member). The
            user ID is protected by a regular expression validator - only valid IDs as specified
            by the institution's policies is a valid ID.
        """
	)
	date_registered = DateTimeField(
		auto_now_add = True,
		null = False,
		editable = False,
		verbose_name = _('date registered'),
	    help_text = """
            The date in which this user registered. This is kept for historic reasons and is not
            required by the generator in any way.
        """
	)
	full_name = CharField(
		max_length = 1024,
		null = False,
		blank = False,
		verbose_name = _('full name'),
	    help_text = """
            The user's full name. Enough space is given to take into account distinct configurations
            and most foreign names according to the W3C suggestions on the topic of internationalization
            and name storage.
        """
	)
	picture = ProcessedImageField(
		processors = [ SmartCrop(128, 128) ],
		upload_to = _upload_to,
		format = 'PNG',
		default = 'users/default/picture.png',
		verbose_name = _('user picture'),
	    help_text = """
            A picture of the user used for profile only. This is not required by the generator in
            any way.
        """
	)
	email_address = EmailField(
		max_length = 255,
		null = False,
		blank = False,
		verbose_name = _('email address'),
	    help_text = """
            The institutional email address. This is expected to exist and should be provided by
            the institution through their own internal processes. This serves as the official means
            for the system to communicate new schedule selection sessions and to notify any mismatch
            or results.
        """
	)
	role = ForeignKey('rhea.Role',
		related_name = 'users',
		verbose_name = _('user role'),
	    help_text = """
            The role, permission-wise, this user has on the system. The role of the user is independent
            of their user type in order to allow for flexible scenarios, such as instructors belonging
            to staff as well or students who work on the platform for any given reason.
        """
	)
	permissions = ManyToManyField('rhea.Permission',
		related_name = '+',
		verbose_name = _('user-specific permissions'),
	    help_text = """
            User-wise permissions which can be added or revoked individually. This does not affect the
            structure of the role's permissions and is only provided for fine-tuning permissions for
            specific users, such as superusers or specific staff members who require additional
            privileges with respect to their role.
        """
	)

	objects = UserManager()

	USERNAME_FIELD = 'user_id'
	REQUIRED_FIELDS = [ 'full_name', 'email_address', 'role' ]

	def get_full_name(self): return self.full_name
	def get_short_name(self): return self.full_name

	class Meta(object):

		verbose_name = _('user')
		verbose_name_plural = _('users')
		swappable = 'AUTH_USER_MODEL'
		app_label = 'rhea'


class Student(User):

	program = ForeignKey('rhea.AcademicProgram',
		related_name = 'students',
		verbose_name = _('academic program'),
	    help_text = """
            The current academic program for this student. Note that changes in the academic
            program are not considered for this development, but should imply a revalidation
            analysis on undertaken subjects to correctly position the new subject pointers to
            their adequate positions prior to making this instance usable again.
        """
	)
	subjects = ManyToManyField('rhea.Requirement',
		related_name = '+',
		verbose_name = _('currently-coursing subjects'),
	    help_text = """
            This is a list of pointers to subjects in the academic program's requirements tree,
            or course plan. The list points to current subjects only - candidates are calculated
            on demand by the schedule generator.
        """
	)
	course_schedule = OneToOneField('rhea.Schedule',
		related_name = 'student',
		verbose_name = _('current course schedule'),
	    help_text = """
            This schedule is the current academic period's schedule for the instructor. This
            specifies the courses the student should take and when should these be taken.
            Since it is tied to the current academic period, this schedule has an expiry date.
        """
	)

	@cached_property
	def candidate_subjects(self):

		candidates = []

		# List the current subjects and the program


		return candidates

	class Meta(object):

		verbose_name = _('student')
		verbose_name_plural = _('students')
		app_label = 'rhea'
class Instructor(User):

	subjects = ManyToManyField('rhea.Subject',
		related_name = 'instructors',
		through = 'rhea.Specialty',
		through_fields = [ 'instructor', 'subject' ],
		symmetrical = False,
		verbose_name = _('subjects that can be instructed'),
	    help_text = """
            This is a list of pointers to subjects which the instructor can teach. These are
            considered the instructor's "specialty subjects" and are ranked according to
            confidence: a number from 0.0 to 1.0 inclusive which allows instructors to rank
            subjects based on their particular specialties. Ties may exist - this is only a
            hint on which subjects to consider first.
        """
	)
	work_schedule = OneToOneField('rhea.Schedule',
		related_name = 'user',
		verbose_name = _('work schedule'),
	    help_text = """
            This schedule serves as a "probability matrix" which gets merged with the course's
            in order to determine possible slots in which the course could be fitted into.
        """
	)
	course_schedule = OneToOneField('rhea.Schedule',
		related_name = 'instructor',
		verbose_name = _('current course schedule'),
	    help_text = """
            This schedule is the current academic period's schedule for the instructor. This
            specifies the courses the instructor should provide and when should these be given.
            Since it is tied to the current academic period, this schedule has an expiry date.
        """
	)

	class Meta(object):

		verbose_name = _('class instructor')
		verbose_name_plural = _('class instructors')
		app_label = 'rhea'
