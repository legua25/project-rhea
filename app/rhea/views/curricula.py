# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render_to_response, redirect, RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from app.rhea.decorators import ajax_required
from django.views.generic import View

class CurriculaListView(View):

	# @method_decorator(login_required)
	def get(self, request):


		return render_to_response('rhea/curricula/list.html', context = RequestContext(request, locals()))

	def post(self, request):
		pass

list = CurriculaListView.as_view()
