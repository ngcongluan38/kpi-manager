from django.conf.urls import url
# from django.contrib.auth import views as auth_views
# from django.views.generic import TemplateView
from rest_framework_jwt.views import ObtainJSONWebToken

# from kpiwebapi.views import register_api
from registration.serializers import CustomJWTSerializer
from . import views


urlpatterns = [
    url(r'^api/login/', ObtainJSONWebToken.as_view(serializer_class=CustomJWTSerializer)),
    url(r'^login/$', views.SiteLoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutThenLoginView.as_view(), name='logout'),
    # url(r'^register/', register_api),
    # url(r'^signup/$', views.RegisterView.as_view(), name='register'),

    # url(r'^password/reset/$', auth_views.password_reset,
    #     {'post_reset_redirect': 'registration:forgot_password_sent',
    #      'template_name': 'registration/forgot_password.html',  'password_reset_form': forms.ForgotPasswordForm},
    #     name='forgot_password'),

    # url(r'^password/reset/ok/$', TemplateView.as_view(template_name='registration/forgot_password_sent.html'),
    #     name='forgot_password_sent'),

    # url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     views.SitePasswordResetConfirmView.as_view(), name='forgot_password_confirm'),
    # url(r'^password/reset/complete/$',
    #     TemplateView.as_view(template_name='registration/forgot_password_complete.html'),
    #     name='password_reset_complete'),
]
