# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from enum import Enum as enum

class DayOfWeek(enum):

	MONDAY = _('Monday')
	TUESDAY = _('Tuesday')
	WEDNESDAY = _('Wednesday')
	THURSDAY = _('Thursday')
	FRIDAY = _('Friday')
