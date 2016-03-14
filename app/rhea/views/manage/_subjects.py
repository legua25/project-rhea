# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render_to_response, redirect, RequestContext
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from app.rhea.decorators import ajax_required, role_required
from django.http import JsonResponse, HttpResponseNotFound
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from app.rhea.forms import SubjectForm, DependencyFormSet
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from app.rhea.models import Dependency
from django.views.generic import View
from app.rhea.models import Subject
from django.db.models import Q
import json

__all__ = [
	'subject_list',
	'subject_create',
	'subject_edit'
]


User = get_user_model()

class SubjectListView(View):

	@method_decorator(login_required)
	@method_decorator(role_required('administrator'))
	@method_decorator(ajax_required)
	@method_decorator(csrf_protect)
	def get(self, request):

		page = request.GET.get('page', 1)
		size = request.GET.get('size', 10)
		term = request.GET.get('q', False)

		# Apply search term to the mix if any
		query = Subject.objects.active()
		if term is not False:
			query = query.filter(Q(name__icontains = term) | Q(code__icontains = term))

		query = query.order_by('name', 'code')

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
					'url': reverse('management:subjects:edit', kwargs = { 'id': s.id }),
					'code': s.code,
					'name': s.name
				} for s in subjects ]
			}
		})
subject_list = SubjectListView.as_view()

class SubjectCreateView(View):

	@method_decorator(login_required)
	@method_decorator(role_required('administrator'))
	def get(self, request):

		subject = SubjectForm()
		dependencies = DependencyFormSet(queryset = Subject.objects.active(), prefix = 'deps')

		site = 'management:main'
		return render_to_response('rhea/management/subjects/create.html', context = RequestContext(request, locals()))
	@method_decorator(login_required)
	@method_decorator(role_required('administrator'))
	@method_decorator(csrf_protect)
	def post(self, request):

		subject = SubjectForm(request.POST)
		dependencies = DependencyFormSet(request.POST, queryset = Subject.objects.active(), prefix = 'deps')

		if subject.is_valid() and dependencies.is_valid():

			# Save the subject first to generate the ID
			subject.save()
			subj = subject.instance

			# For each dependency, iterate to set the real value, then go on saving
			for dependency in dependencies:

				dependency.save()
				dep = dependency.instance

				Dependency.objects.create(
					dependency = dep,
					dependent = subj,
					program = dependency.cleaned_data['program']
				)

			return redirect(reverse_lazy('management:curricula:list'))

		site = 'management:main'
		return render_to_response('rhea/management/subjects/create.html', context = RequestContext(request, locals()))
subject_create = SubjectCreateView.as_view()

class SubjectEditView(View):

	@method_decorator(login_required)
	@method_decorator(role_required('administrator'))
	def get(self, request, id = 0):

		try: instance = Subject.objects.get(id = id)
		except Subject.DoesNotExist: return HttpResponseNotFound()
		else:

			# Get dependencies list
			dependency_list = Subject.objects.active(id__in = instance.dependencies.all().values_list('id', flat = True))

			# Create forms
			subject = SubjectForm(instance = instance)
			dependencies = DependencyFormSet(queryset = dependency_list, prefix = 'deps')

			# Create the rastered list
			deps = Dependency.objects.all().select_related('program')
			deps = json.dumps([ {
				'id': dep.id,
				'code': dep.code,
				'name': dep.name,
				'program': deps.get(dependency = dep, dependent = instance).program_id
			} for dep in dependency_list ])

			site = 'management:main'
			return render_to_response('rhea/management/subjects/create.html', context = RequestContext(request, locals()))
	@method_decorator(login_required)
	@method_decorator(role_required('administrator'))
	@method_decorator(csrf_protect)
	def post(self, request, id = 0):

		subject = SubjectForm(request.POST)
		dependencies = DependencyFormSet(request.POST, queryset = Subject.objects.active(), prefix = 'deps')

		if subject.is_valid() and dependencies.is_valid():

			# Save the subject first to generate the ID
			subject.save()
			subj = subject.instance

			# For each dependency, iterate to set the real value, then go on saving
			for dependency in dependencies:

				dependency.save()
				dep = dependency.instance

				Dependency.objects.create(
					dependency = dep,
					dependent = subj,
					program = dependency.cleaned_data['program']
				)

			return redirect(reverse_lazy('management:curricula:list'))

		site = 'management:main'
		return render_to_response('rhea/management/subjects/create.html', context = RequestContext(request, locals()))
subject_edit = SubjectEditView.as_view()
