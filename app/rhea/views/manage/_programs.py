# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render_to_response, redirect, RequestContext
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from app.rhea.forms import ProgramForm, DependencyFormSet
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from app.rhea.decorators import role_required
from django.http import HttpResponseNotFound
from app.rhea.models import AcademicProgram
from django.views.generic import View
from django.http import JsonResponse

__all__ = [
	'program_list',
	'program_create',
	'program_edit'
]


class ProgramListView(View):

	@method_decorator(login_required)
	@method_decorator(role_required('administrator'))
	def get(self, request):

		if request.is_ajax():

			@csrf_protect
			def ajax(request):

				page = request.GET.get('page', 1)
				size = request.GET.get('size', 10)
				query = AcademicProgram.objects.active().order_by('name')

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
							'url': reverse('management:curricula:edit', kwargs = { 'id': p.id }),
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

		site = 'management:main'
		return render_to_response('rhea/management/curricula/create.html', context = RequestContext(request, locals()))
	@method_decorator(login_required)
	@method_decorator(role_required('administrator'))
	@method_decorator(csrf_protect)
	def post(self, request):

		program = ProgramForm(request.POST)

		# Validate the forms - both of them
		if program.is_valid():

			# Save the program and return the user to the "same" page, except we're now editing the program, not creating it
			program.save()
			instance = program.instance

			return redirect(reverse_lazy('management:curricula:edit', kwargs = { 'id': instance.id }))

		site = 'management:main'
		return render_to_response('rhea/management/curricula/create.html', context = RequestContext(request, locals()))
program_create = ProgramCreateView.as_view()

class ProgramEditView(View):

	@method_decorator(login_required)
	@method_decorator(role_required('administrator'))
	def get(self, request, id = 0):

		try: instance = AcademicProgram.objects.get(id = id)
		except AcademicProgram.DoesNotExist: return HttpResponseNotFound()
		else:

			program = ProgramForm(instance = instance)

		site = 'management:main'
		return render_to_response('rhea/management/curricula/edit.html', context = RequestContext(request, locals()))
	@method_decorator(login_required)
	@method_decorator(role_required('administrator'))
	@method_decorator(csrf_protect)
	def post(self, request, id = 0):

		try: instance = AcademicProgram.objects.get(id = id)
		except AcademicProgram.DoesNotExist: return HttpResponseNotFound()
		else:

			program = ProgramForm(request.POST, instance = instance)

		# Validate the forms - both of them
		if program.is_valid():

			# Save the program changes
			program.save()
			return redirect(reverse_lazy('management:curricula:list'))

		site = 'management:main'
		return render_to_response('rhea/management/curricula/edit.html', context = RequestContext(request, locals()))
program_edit = ProgramEditView.as_view()
