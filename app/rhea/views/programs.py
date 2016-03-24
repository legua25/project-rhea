# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render_to_response
from django.views.generic import View
from django.http import JsonResponse
from app.rhea.models import *

__all__ = [ 'list', 'create', 'view' ]

class ProgramListView(View):

	@method_decorator(csrf_protect)
	# @method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def get(self, request):

		# Page the subjects list
		page, size = request.GET.get('page', 1), request.GET.get('size', 15)
		pages = Paginator(AcademicProgram.objects.active().order_by('acronym'), size)

		try: programs = pages.page(page)
		except PageNotAnInteger: programs = pages.page(1)
		except EmptyPage: programs = pages.page(pages.num_pages)

		# Serialize and send back response
		return JsonResponse({
			'version': '0.1.0',
			'status': 200,
			'pagination': {
				'total': Subject.objects.active().count(),
				'current': page,
				'previous': programs.previous_page_number() if programs.has_previous() else False,
				'next': programs.next_page_number() if programs.has_next() else False,
				'size': size
			},
			'programs': [
				{
					'id': p.id,
					'acronym': p.acronym,
					'name': p.name
				} for p in programs
			]
		})
list = ProgramListView.as_view()


class ProgramCreateView(View):

	@method_decorator(csrf_protect)
	# @method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def post(self, request):

		return JsonResponse({
			'version': '0.1.0',
			'status': 501
		}, status = 501)
create = ProgramCreateView.as_view()


class ProgramView(View):

	@method_decorator(csrf_protect)
	# @method_decorator(login_required)
	# @method_decorator(role_required('administrator'))
	def get(self, request, acronym = ''):

		# Try to locate the subject - return 404 Not Found if code is invalid
		try: program = AcademicProgram.objects.get(acronym = acronym, active = True)
		except Subject.DoesNotExist:
			return JsonResponse({ 'version': '0.1.0', 'status': 404 }, status = 404)
		else:

			# Paginate the program requirements, since these can be quite extensive
			page, size = request.GET.get('page', 1), request.GET.get('size', 15)
			pages = Paginator(program.subjects.order_by('code'), size)

			try: subjects = pages.page(page)
			except PageNotAnInteger: subjects = pages.page(1)
			except EmptyPage: subjects = pages.page(pages.num_pages)

			# Serialize and send back response
			return JsonResponse({
				'version': '0.1.0',
				'status': 200,
				'pagination': {
					'total': program.subjects.count(),
					'current': page,
					'previous': subjects.previous_page_number() if subjects.has_previous() else False,
					'next': subjects.next_page_number() if subjects.has_next() else False,
					'size': size
				},
				'program': {
					'id': program.id,
					'acronym': program.acronym,
					'name': program.name,
					'subjects': [ { 'id': s.id, 'code': s.code } for s in subjects ]
				}
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
view = ProgramView.as_view()
