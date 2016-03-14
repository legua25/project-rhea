# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render_to_response, redirect, RequestContext
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from app.rhea.forms import ProgramForm, SubjectForm, DependencyFormSet
from app.rhea.decorators import ajax_required, role_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from app.rhea.models import AcademicProgram, Subject
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import get_user_model
from django.views.generic import View
from django.http import JsonResponse
from django.db.models import Q

User = get_user_model()

class ManagementView(View):

	@method_decorator(login_required)
	@method_decorator(role_required('administrator'))
	def get(self, request):

		# TODO: This is the lamest settings panel in history - add something here!
		site = 'management:main'
		return render_to_response('rhea/management/index.html', context = RequestContext(request, locals()))
main = ManagementView.as_view()


class ProgramListView(View):

	@method_decorator(login_required)
	@method_decorator(role_required('administrator'))
	def get(self, request):

		if request.is_ajax():

			@csrf_protect
			def ajax(request):

				page = request.GET.get('page', 1)
				size = request.GET.get('size', 10)
				query = AcademicProgram.objects.active().order_by('-name')

				# Paginate the data - we will fetch it by parts using AJAX
				paginator = Paginator(query, size)

				try: programs = paginator.page(page)
				except EmptyPage: programs = paginator.page(paginator.num_pages)
				except PageNotAnInteger: programs = paginator.page(1)

				# Serialize the response and send it through
				return JsonResponse({
					'version': '0.1.0',
					'status': 200,
					'programs': {
						'meta': {
							'current': page,
							'prev': programs.previous_page_number() if programs.has_previous() else False,
							'next': programs.next_page_number() if programs.has_next() else False,
							'size': size,
							'total': paginator.num_pages
						},
						'count': query.count(),
						'entries': [ {
							'id': p.id,
							'acronym': p.acronym,
							'name': p.name,
							'description': p.description,
							'subjects': [ { 'id': s.id, 'code': s.code, 'name': s.name } for s in p.subjects ]
						} for p in programs ]
					}
				})
			return ajax(request)

		site = 'management:main'
		return render_to_response('rhea/management/curricula/list.html', context = RequestContext(request, locals()))
program_list = ProgramListView.as_view()

class ProgramCreateView(View):

	@method_decorator(login_required)
	@method_decorator(role_required('administrator'))
	def get(self, request):

		program = ProgramForm()
		dependencies = DependencyFormSet(prefix = 'deps')

		site = 'management:main'
		return render_to_response('rhea/management/curricula/create.html', context = RequestContext(request, locals()))
	@method_decorator(login_required)
	@method_decorator(role_required('administrator'))
	@method_decorator(csrf_protect)
	def post(self, request):

		program = ProgramForm(request.POST)
		dependencies = DependencyFormSet(request.POST, prefix = 'deps')

		if program.is_valid() and dependencies.is_valid():
			pass

		print program
		site = 'management:main'
		return render_to_response('rhea/management/curricula/create.html', context = RequestContext(request, locals()))
program_create = ProgramCreateView.as_view()

class SubjectListView(View):

	@method_decorator(login_required)
	@method_decorator(role_required('administrator'))
	def get(self, request):

		if request.is_ajax():

			@csrf_protect
			def ajax(request, page, size, term):

				query = Subject.objects.active()
				if term is not False:
					query = query.filter(Q(name__icontains = term) | Q(code__icontains = term))

				query = query.order_by('-name', '-code')

				# Paginate the data - we will fetch it by parts using AJAX
				paginator = Paginator(query, size)

				try: subjects = paginator.page(page)
				except EmptyPage: subjects = paginator.page(paginator.num_pages)
				except PageNotAnInteger: subjects = paginator.page(1)

				# Serialize the response and send it through
				return JsonResponse({
					'version': '0.1.0',
					'status': 200,
					'subjects': {
						'meta': {
							'current': page,
							'prev': subjects.previous_page_number() if subjects.has_previous() else False,
							'next': subjects.next_page_number() if subjects.has_next() else False,
							'size': size,
							'total': paginator.num_pages
						},
						'count': query.count(),
						'entries': [ {
							'id': s.id,
							'code': s.code,
							'name': s.name
						} for s in subjects ]
					}
				})
			return ajax(request, request.GET.get('page', 1), request.GET.get('size', 10), request.GET.get('q', False))

		# TODO: Add the actual view here

		site = 'management:main'
subject_list = SubjectListView.as_view()
