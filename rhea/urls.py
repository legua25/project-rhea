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

			url(r'^$', rhea.users.view, name = 'view'),
			url(r'^edit/$', debug_view, name = 'edit')

		]))

	], namespace = 'user', app_name = 'app.rhea')),

] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
