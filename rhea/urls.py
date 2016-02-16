# -*- config: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.conf import settings


# TODO: Replace with proper callbacks, then delete this
def debug_view(request):

	from django.http import HttpResponse
	return HttpResponse('{ "status": 200 }', content_type = 'application/json')
# TODO: Replace with proper callbacks, then delete this

urlpatterns = [] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
