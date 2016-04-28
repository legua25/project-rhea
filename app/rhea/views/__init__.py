# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import RequestContext, render_to_response
from django.views.generic import View

class InterfaceView(View):

	def get(self, request, template = 'index'):

		# Select a template from the requested URL parameter
		return render_to_response('rhea/app/%s.html' % template, context = RequestContext(request, locals()))
view = InterfaceView.as_view()

import subjects, users, programs, auth, pipeline
