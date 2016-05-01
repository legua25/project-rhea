# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from app.rhea.tokens import InstructorTokenFactory
from app.rhea.mail import TemplateEmailMessage
from app.rhea.models import Instructor
from django.utils.timezone import now
from kronos import register
from time import mktime
from json import dumps

__all__ = [ 'email_instructors' ]


@register('1 * * * *')
def email_instructors():

	instructors = Instructor.objects.active()
	tokens = InstructorTokenFactory()

	# Send an email to all missing instructors
	missing = []
	start = now()
	for instructor in instructors.filter(last_confirmation__isnull = True):

		# Build the email form a template
		mail = TemplateEmailMessage(
			subject = 'Action required - Update your subjects',
			from_email = 'noreply@project_rhea.com',
			to = [ instructor.email_address ],
			context = { 'instructor': instructor, 'token': tokens.make_token(instructor) }
		)
		mail.attach_from_template('rhea/email/update-status.txt', 'text/plain')

		missing.append({
			'instructor': {
				'id': instructor.user_id,
				'name': instructor.full_name,
				'email': instructor.email_address
			},
			'sent': mail.send(fail_silently = True) > 0
		})
	end = now()

	return dumps({
		'stats': {
			'start': mktime(start.utctimetuple()),
			'elapsed': (end - start).microseconds,
			'coverage': (len(missing) / instructors.count())
		},
		'pending': missing
	})
