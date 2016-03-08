# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render_to_response, redirect, RequestContext
from app.rhea.decorators import ajax_required, role_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import get_user_model
from django.views.generic import View
from django.http import JsonResponse
from time import mktime as timestamp

User = get_user_model()

class ManagementView(View):

	@method_decorator(login_required)
	@method_decorator(role_required('administrator'))
	def get(self, request):

		site = 'management:main'

		return render_to_response('rhea/management/index.html', context = RequestContext(request, locals()))

main = ManagementView.as_view()
