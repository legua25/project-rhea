# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import students, instructors

__all__ = [ 'list', 'students', 'instructors' ]

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.views.generic import View
from django.http import JsonResponse
from django.db.models import Q
from app.rhea.models import *

User = get_user_model()


class UserListView(View):

	@method_decorator(csrf_protect)
	# @method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def get(self, request):

		# Determine the type of users to retrieve - no results implies all
		user_type = request.GET.get('type', 'user')
		page, size = request.GET.get('page', 1), request.GET.get('size', 15)

		# Generic serialization function - converts a user query into a JSON response
		def serialize(query, make_user_dict):

			# Page the user query
			paginator = Paginator(query.order_by('user_id'), size)

			try: users = paginator.page(page)
			except PageNotAnInteger: users = paginator.page(1)
			except EmptyPage: users = paginator.page(paginator.num_pages)

			# Run serialization on all results, then return
			return {
				'version': '0.1.0',
				'status': 200,
				'type': user_type,
				'pagination': {
					'total': query.count(),
					'current': page,
					'previous': users.previous_page_number() if users.has_previous() else False,
					'next': users.next_page_number() if users.has_next() else False,
					'size': size
				},
				'users': [ make_user_dict(u) for u in users ]
			}

		if user_type == 'student':

			# Serialize the students - provide all available data
			return JsonResponse(serialize(Student.objects.active(), lambda u: {
				'id': u.user_id,
				'name': u.full_name,
				'email': u.email_address,
				'program': u.program_id,
				'semester': u.semester
			}))
		elif user_type == 'instructor':

			# Serialize the instructors - provide all available data
			return JsonResponse(serialize(Instructor.objects.active(), lambda u: {
				'id': u.user_id,
				'name': u.full_name,
				'email': u.email_address,
				'subjects': [ s.code for s in u.subjects.all().filter(active = True) ]
			}))
		elif user_type == 'staff':

			# Serialize the staff members (all non-students and non-instructors or anyone with the adequate permissions) - provide all available data
			query = Q(student__isnull = True, instructor__isnull = True) | Q(role__codename = 'administrator')
			return JsonResponse(serialize(User.objects.active(query), lambda u: {
				'id': u.user_id,
				'name': u.full_name,
				'email': u.email_address
			}))
		elif user_type == 'user':

			# Serialize the students - provide all available data
			return JsonResponse(serialize(User.objects.active(), lambda u: {
				'id': u.user_id,
				'name': u.full_name,
				'email': u.email_address
			}))
		else:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
list = UserListView.as_view()
