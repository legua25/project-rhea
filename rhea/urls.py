# -*- config: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.conf import settings


def redirect(url): return RedirectView.as_view(url = reverse_lazy(url))
def debug_view(request, **kwargs):

	from django.http import HttpResponse
	return HttpResponse('{ "status": 200 }', content_type = 'application/json')


from app.rhea import views as rhea

urlpatterns = [

	# Login & dashboard views
	url(r'^$', redirect('accounts:login'), name = 'index'),

	url(r'accounts/', include([

		url(r'^login/$', rhea.accounts.login, name = 'login'),
		url(r'^logout/$', rhea.accounts.logout, name = 'logout')

	], namespace = 'accounts', app_name = 'rhea')),

	# Instructor profiles
	url(r'^users/', include([

		# AJAX views
		url(r'^$', debug_view, name = 'list'),

		# User views
		url(r'(?P<user_id>[AaLl][\d]+)/', include([

			url(r'^$', debug_view, name = 'view'),
			url(r'^edit/$', debug_view, name = 'edit')

		]))

	], namespace = 'user', app_name = 'app.rhea')),

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
		url(r'^users/', include([

			# AJAX views
			url(r'^$', debug_view, name = 'list'),
			url(r'^create/$', debug_view, name = 'create'),

			# User views
			url(r'^(?P<user_id>[AaLl][\d]+)/$', debug_view, name = 'manage')

		], namespace = 'user', app_name = 'app.rhea'))

	], namespace = 'management', app_name = 'app.rhea'))

] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
