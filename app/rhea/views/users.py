# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render_to_response
from django.contrib.auth import get_user_model
from django.views.generic import View
from django.http import JsonResponse
from django.db.models import Q
from app.rhea.models import *

__all__ = [ 'list' ]

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


class UserCreateView(View):

	@method_decorator(csrf_protect)
	# @method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def post(self, request):

		# user_type = request.GET.get('type', 'user')

		return JsonResponse({
			'version': '0.1.0',
			'status': 501
		}, status = 501)
create = UserCreateView.as_view()


class UserView(View):

	@method_decorator(csrf_protect)
	# @method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def get(self, request, id = ''):

		# Determine the type of user to request
		user_type = request.GET.get('type', 'user')
		if user_type == 'student': UserClass = Student
		elif user_type == 'instructor': UserClass = Instructor
		elif user_type == 'user': UserClass = User
		else:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)

		# Try to locate the subject - return 404 Not Found if code is invalid
		try: user = UserClass.objects.get(user_id = id, active = True)
		except UserClass.DoesNotExist:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
		else:

			# Serialize the user
			user_dict = {
				'id': user.user_id,
				'name': user.full_name,
				'email': user.email_address
			}

			# Add additional data if the user is a student or an instructor
			if user_type == 'student':

				user_dict['program'] = user.program_id
				user_dict['semester'] = user.semester
				user_dict['subjects'] = [ s.dependent.code for s in user.subjects.all() ]
			elif user_type == 'instructor':

				user_dict['subjects'] = [ s.code for s in user.subjects.all() ]

			# Serialize and send back response
			return JsonResponse({
				'version': '0.1.0',
				'status': 200,
				'type': user_type,
				'user': user_dict
			})
	@method_decorator(csrf_protect)
	# @method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def post(self, request, code = ''):

		return JsonResponse({
			'version': '0.1.0',
			'status': 501
		}, status = 501)
	@method_decorator(csrf_protect)
	# @method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def delete(self, request, code = ''):

		return JsonResponse({
			'version': '0.1.0',
			'status': 501
		}, status = 501)
view = UserView.as_view()
