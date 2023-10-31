import user_agents
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.views import LoginView, LogoutView

from django.views.decorators.cache import never_cache
from django.views.generic import FormView
from django.views.generic.base import TemplateResponseMixin, ContextMixin, TemplateView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from . import forms
# Create your views here.


class DeviceAutoSelectMixin(TemplateResponseMixin, ContextMixin):
    mobile_template_name = ''
    desktop_template_name = ''
    mobile_form_class = None
    desktop_form_class = None
    extra_context = {}

    def is_desktop(self):
        user_agent = user_agents.parse(self.request.META.get('HTTP_USER_AGENT'))
        return user_agent.is_pc

    def get_template_names(self):
        # if self.request.user.is_authenticated:
        #     if self.request.user.profile.force_mobile:
        #         return [self.mobile_template_name]
        if self.is_desktop():
            return [self.desktop_template_name]
        return [self.mobile_template_name]

    def get_form_class(self):
        if self.is_desktop():
            return self.desktop_form_class
        return self.mobile_form_class

    def get_context_data(self, **kwargs):
        context = super(DeviceAutoSelectMixin, self).get_context_data(**kwargs)
        if self.extra_context:
            context.update(self.extra_context)
        return context


class SiteLoginView(DeviceAutoSelectMixin, LoginView):
    mobile_template_name = 'registration/mobile/login.html'
    desktop_template_name = 'registration/login.html'
    mobile_form_class = forms.MobileLoginForm
    desktop_form_class = forms.DesktopLoginForm
    extra_context = {'nav': 'login'}


class LogoutThenLoginView(LogoutView):
    """
    Thoát xong nhảy tới trang login.
    """
    next_page = settings.LOGIN_URL
    template_name = 'registration/logged_out.html'

    # @method_decorator(never_cache)
    # def dispatch(self, request, *args, **kwargs):
    #     # delete online status
    #     return super(LogoutThenLoginView, self).dispatch(request, *args, **kwargs)


class GuestLogin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method == 'POST'
        )


@api_view(['POST'])
@permission_classes((GuestLogin,))
def login_api_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if username and password:
        auth_user = authenticate(request, username=username, password=password)
        if auth_user:
            auth_login(request, auth_user)
            return Response({'ok': True})
    return Response({'ok': False})
