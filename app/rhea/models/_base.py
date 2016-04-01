# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from model_utils.managers import InheritanceManager as BaseInheritanceManager
from django.utils.translation import ugettext_lazy as _
from django.db.models import Model as BaseModel
from django.db.models import *

__all__ = [
	'Model',
	'ActiveManager',
	'InheritanceManager'
]

class ActiveManager(Manager):
	""" A utility class which adds support for filtering by active/inactive state. This class is provided
		to enforce the "soft-deleting" schema, required for proper report generation.
	"""

	def inactive(self, *args, **kwargs): return self.filter(active = False, *args, **kwargs)
	def active(self, *args, **kwargs): return self.filter(active = True, *args, **kwargs)
	def get_active(self, *args, **kwargs): return self.get(active = True, *args, **kwargs)
	def get_inactive(self, *args, **kwargs): return self.get(active = False, *args, **kwargs)
class InheritanceManager(ActiveManager, BaseInheritanceManager):
	""" A utility class which adds inheritance resolution support to an active manager.	"""

	pass

class Model(BaseModel):
	""" An adapted Model subclass which implements "soft-deleting". Soft-deleted models are not destroyed
		and removed from the database, but rather hidden from public. This allows historic reports to be
		generated without inconsistency issues.
	"""

	active = BooleanField(
		default = True,
		verbose_name = _('is active')
	)

	objects = ActiveManager()

	def delete(self, soft = True, **kwargs):
		""" Implements a soft-deletion schema in which a model may be deleted from the database or "soft-deleted",
			hidden from public.
			:param soft: a Boolean determining if the model should be soft-deleted or not
			:param using: the alias of the database in which to store this model
		"""

		if soft is True:

			self.active = False
			self.save(**kwargs)
		else: Model.delete(self, **kwargs)

	class Meta(object):
		abstract = True
