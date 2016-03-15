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

__all__ = []


