# -*- config: utf-8 -*-
from __future__ import unicode_literals
from django.core.urlresolvers import reverse_lazy as reverse
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.conf import settings


redirect = RedirectView.as_view
def debug(request, **kwargs):

	from django.http import JsonResponse
	return JsonResponse({
		'version': '0.1.0',
		'status': 501
	}, status = 501)


from app.rhea import views as rhea
urlpatterns = [

	url(r'^$', redirect(url = reverse('accounts:login')), name = 'index'),
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

		# Users management
		url(r'^users/', include([

			url(r'^$', rhea.users.list, name = 'list'),
			url(r'^students/', include([

				url(r'^create/$', rhea.users.students.create, name = 'create'),
				url(r'^(?P<id>[aA][\d]+)/', include([

					url(r'^$', rhea.users.students.view, name = 'view'),
					url(r'^schedule/', include([

						url(r'^$', debug, name = 'schedule'),
						url(r'^(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', debug, name = 'select')

					]))

				]))

			], namespace = 'students')),
			url(r'^instructors/', include([

				url(r'^create/$', rhea.users.instructors.create, name = 'create'),
				url(r'^(?P<id>[lL][\d]+)/', include([

					url(r'^$', rhea.users.instructors.view, name = 'view'),
					url(r'^schedule/$', debug, name = 'schedule')

				]))

			], namespace = 'instructors'))

		], namespace = 'users', app_name = 'rhea'))

	], namespace = 'manage', app_name = 'rhea')),

] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)


