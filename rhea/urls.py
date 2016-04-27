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
	from django.middleware.csrf import get_token

	return JsonResponse({
		'version': '0.1.0',
		'status': 501,
		'csrf': get_token(request)
	}, status = 501)


from app.rhea import views as rhea
urlpatterns = [

	url(r'^test/$', debug, name = 'test'),
	url(r'^$', redirect(url = reverse('accounts:login')), name = 'index'),
	url(r'^accounts/', include([

		url(r'^login/$', rhea.auth.login, name = 'login'),
		url(r'^logout/$', rhea.auth.logout, name = 'logout'),
		url(r'^(?P<id>[aAlL][\d]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', rhea.auth.validate, name = 'validate')

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

		], namespace = 'users', app_name = 'rhea')),

		# Scheduling process management
		url(r'^schedule/', include([

			url(r'^update/', include([

				url(r'^$', debug, name = 'start'),
				url(r'^progress/$', debug, name = 'progress'),
				url(r'^(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', debug, name = 'process')

			], namespace = 'update', app_name = 'rhea')),
			url(r'^subjects/$', rhea.schedule.subjects, name = 'subjects'),
			url(r'^courses/$', rhea.schedule.courses, name = 'courses'),
			url(r'^schedule/', include([

				url(r'^$', debug, name = 'start'),
				url(r'^progress/$', debug, name = 'progress'),
				url(r'^(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', debug, name = 'process')

			], namespace = 'schedule', app_name = 'rhea')),
			url(r'^gathering/$', debug, name = 'gathering')

		], namespace = 'schedule', app_name = 'rhea'))

	], namespace = 'manage', app_name = 'rhea')),

] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)


