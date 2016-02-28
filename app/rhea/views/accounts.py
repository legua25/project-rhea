# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import (
	login as login_to_site,
	logout as logout_from_site
)
from django.shortcuts import render_to_response, redirect, RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import update_last_login
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from django.views.generic import View
from app.rhea.forms import LoginForm
import random

class LoginView(View):

	def get(self, request):

		# Get redirect URL
		redirect_url = request.GET.get('next', reverse_lazy('dashboard'))

		# Check if user has been authenticated before - if so, redirect him/her to the main site
		if request.user is not None and request.user.is_authenticated():
			return redirect(redirect_url)

		# Create the login form and render the template
		background = random.randint(1, 2)
		form = LoginForm()
		return render_to_response('rhea/accounts/login.html', context = RequestContext(request, locals()))
	@method_decorator(csrf_protect)
	def post(self, request):

		# Get redirect URL
		redirect_url = request.GET.get('next', reverse_lazy('dashboard'))

		# Check if user has been authenticated before - if so, redirect him/her to the main site
		if request.user is not None and request.user.is_authenticated():
			return redirect(redirect_url)

		form = LoginForm(request.POST)
		if form.is_valid():

			user = form.user
			login_to_site(request, user)
			update_last_login(None, user = user)

			return redirect(redirect_url)

		# Resend the user to the login form to retry
		background = random.randint(1, 2)
		return render_to_response('rhea/accounts/login.html',
			context = RequestContext(request, locals()),
			status = 401
		)

login = LoginView.as_view()

class LogoutView(View):

	@method_decorator(login_required)
	def get(self, request):

		# Proceed to log out the user
		logout_from_site(request)
		return redirect(reverse_lazy('accounts:login'))

logout = LogoutView.as_view()
