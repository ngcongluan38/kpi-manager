import user_agents
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.utils import timezone

from django.views.decorators.cache import never_cache
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.views.generic.base import TemplateResponseMixin, ContextMixin, TemplateView
from django.views.generic.list import ListView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from kpi_manager.models import Tag

# from . import forms
# Create your views here.


class TagDetailView(ListView):

    model = Tag
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


