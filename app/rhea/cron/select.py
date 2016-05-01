# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from app.rhea.tokens import StudentTokenFactory
from app.rhea.mail import TemplateEmailMessage
from django.utils.timezone import now
from app.rhea.models import Student
from kronos import register
from time import mktime
from json import dumps

__all__ = [ 'email_students' ]


@register('1 * * * *')
def email_students():

	students = Student.objects.active()
	tokens = StudentTokenFactory()

	# Send an email to all missing instructors
	missing = []
	start = now()
	for student in students.filter(last_confirmation__isnull = True):

		# Build the email form a template
		mail = TemplateEmailMessage(
			subject = 'Action required - Select your Courses',
			from_email = 'noreply@project_rhea.com',
			to = [ student.email_address ],
			context = { 'student': student, 'token': tokens.make_token(student) }
		)
		mail.attach_from_template('rhea/email/select-courses.txt', 'text/plain')

		missing.append({
			'student': {
				'id': student.user_id,
				'name': student.full_name,
				'email': student.email_address
			},
			'sent': mail.send(fail_silently = True) > 0
		})
	end = now()

	return dumps({
		'stats': {
			'start': mktime(start.utctimetuple()),
			'elapsed': (end - start).microseconds,
			'coverage': (len(missing) / students.count())
		},
		'pending': missing
	})
