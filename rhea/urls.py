# -*- config: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.conf import settings


def debug(request, **kwargs):

	from django.http import JsonResponse
	return JsonResponse({
		'version': '0.1.0',
		'status': 501
	}, status = 501)
def redirect(url, **kwargs):
	return RedirectView.as_view(url = url, **kwargs)


from app.rhea import views as rhea
urlpatterns = [

	url(r'^accounts/', include([

		url(r'^login/$', debug, name = 'login'),
		url(r'^logout/$', debug, name = 'logout'),
		url(r'^recover/', include([

			url(r'^$', debug, name = 'request'),
			url(r'^(?P<id>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', debug, name = 'reset')

		], namespace = 'recover', app_name = 'rhea'))

	], namespace = 'accounts', app_name = 'rhea')),

	url(r'^manage/', include([

		# Curricula management
		url(r'^curricula/', include([

			url(r'^$', debug, name = 'list'),
			url(r'^programs/', include([

				url(r'^$', rhea.programs.list, name = 'list'),
				url(r'^create/$', rhea.programs.create, name = 'create'),
				url(r'^(?P<acronym>[A-Z]+)/$', rhea.programs.view, name = 'view')

			], namespace = 'programs', app_name = 'rhea')),
			url(r'^subjects/', include([

				url(r'^$', rhea.subjects.list, name = 'list'),
				url(r'^create/$', rhea.subjects.create, name = 'create'),
				url(r'^(?P<code>[A-Z0-9]+)/$', rhea.subjects.view, name = 'view')

			], namespace = 'subjects', app_name = 'rhea'))

		], namespace = 'curricula', app_name = 'rhea')),
		# Users, roles & permissions management
		url(r'^users/', include([

			url(r'^$', debug, name = 'list'),
			url(r'^create/$', debug, name = 'create'),
			url(r'^(?P<id>[LA][\d]+)/', include([

				url(r'^$', debug, name = 'view'),
				url(r'^schedule/$', debug, name = 'query')

			]))

		], namespace = 'users', app_name = 'rhea'))

	], namespace = 'manage', app_name = 'rhea')),

] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)


