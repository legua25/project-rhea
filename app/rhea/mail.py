# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

__all__ = [ 'TemplateEmailMessage' ]

class TemplateEmailMessage(EmailMultiAlternatives):

	def __init__(self, context, *args, **kwargs):

		EmailMultiAlternatives.__init__(self, *args, **kwargs)
		self.context = context

	def attach_from_template(self, template, mimetype):

		content = render_to_string(template, self.context)
		self.attach_alternative(content, mimetype)
