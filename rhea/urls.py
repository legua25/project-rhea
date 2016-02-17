# -*- config: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.conf import settings


def debug_view(request, **kwargs):

	from django.http import HttpResponse
	return HttpResponse('{ "status": 200 }', content_type = 'application/json')


urlpatterns = [

	# Login & dashboard views
	url(r'^$', debug_view, name = 'login'),
	url(r'^dashboard/$', debug_view, name = 'dashboard'),

	# Schedule construction & user profiles
	url(r'^student/', include([

		# AJAX views
		url(r'^$', debug_view, name = 'list'),

		# User views
		url(r'(?P<enroll_id>A[\d]+)/', include([

			url(r'^$', debug_view, name = 'view'),
			url(r'^schedule/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', debug_view, name = 'create')

		]))

	], namespace = 'student', app_name = 'app.rhea')),

	# Instructor profiles
	url(r'^instructor/', include([

		# AJAX views
		url(r'^$', debug_view, name = 'list'),

		# User views
		url(r'(?P<payroll_id>L[\d]+)/', include([

			url(r'^$', debug_view, name = 'view'),
			url(r'^edit/$', debug_view, name = 'edit')

		]))

	], namespace = 'instructor', app_name = 'app.rhea')),

	# Management, reports & settings
	url(r'^manage/', include([

		# User views
		url(r'^settings/$', debug_view, name = 'settings'),
		url(r'^reports/$', debug_view, name = 'reports'),

		# Curricula & subjects
		url(r'^curricula/', include([

			# AJAX views
			url(r'^$', debug_view, name = 'list'),
			url(r'^create/$', debug_view, name = 'create'),

			# User views
			url(r'^(?P<id>[\d]+)/$', debug_view, name = 'manage')

		], namespace = 'curricula', app_name = 'app.rhea')),
		url(r'^subject/', include([

			# AJAX views
			url(r'^$', debug_view, name = 'list'),
			url(r'^create/$', debug_view, name = 'create'),

			# User views
			url(r'^(?P<id>[\d]+)/$', debug_view, name = 'manage')

		], namespace = 'subject', app_name = 'app.rhea')),

		# Instructors & students
		url(r'^instructor/', include([

			# AJAX views
			url(r'^$', debug_view, name = 'list'),
			url(r'^create/$', debug_view, name = 'create'),

			# User views
			url(r'^(?P<payroll_id>L[\d]+)/$', debug_view, name = 'manage')

		], namespace = 'instructor', app_name = 'app.rhea')),
		url(r'^student/', include([

			# AJAX views
			url(r'^$', debug_view, name = 'list'),
			url(r'^create/$', debug_view, name = 'create'),

			# User views
			url(r'^(?P<enroll_id>A[\d]+)/$', debug_view, name = 'manage')

		], namespace = 'student', app_name = 'app.rhea'))

	], namespace = 'management', app_name = 'app.rhea'))

] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)


