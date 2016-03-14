# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render_to_response, RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from app.rhea.decorators import role_required
from django.views.generic import View

from _programs import *
from _subjects import *

class ManagementView(View):

	@method_decorator(login_required)
	@method_decorator(role_required('administrator'))
	def get(self, request):

		site = 'management:main'
		return render_to_response('rhea/management/index.html', context = RequestContext(request, locals()))
main = ManagementView.as_view()
