# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render_to_response, redirect, RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import get_user_model
from app.rhea.decorators import ajax_required
from django.views.generic import View
from django.http import JsonResponse
from time import mktime as timestamp

User = get_user_model()

class UserView(View):

	@method_decorator(login_required)
	def get(self, request, user_id = None):

		# Retrieve the user to prepare the response - in either format, we need it
		try: account = User.objects.get(user_id = user_id, active = True)
		except User.DoesNotExist: account = False

		# The AJAX block must be CSRF protected just in case, so a special route is devised
		if request.is_ajax():

			@csrf_protect
			def ajax(request, user, user_id):

				if user is not False:
					return JsonResponse({
						'version': '0.1.0',
						'status': 302,
						'user': {
							'id': user.user_id,
							'name': user.full_name,
							'registered': timestamp(user.date_registered.utctimetuple()),
							'last_login': timestamp(user.last_login.utctimetuple()),
							'email': {
								'primary': user.email_primary,
								'secondary': user.email_secondary or None
							},
							'role': user.role.name if user.role else None,
							'schedule': None
						}
					}, status = 302)

				return JsonResponse({
					'version': '0.1.0',
					'status': 404,
					'reason': 'User with ID %s does not exist or is invalid' % user_id
				}, status = 404)
			return ajax(request, account, user_id)

		# TODO: Add the user's current schedule (or none if there isn't one)
		site = 'user:view'

		return render_to_response('rhea/users/view.html', context = RequestContext(request, locals()))
view = UserView.as_view()
