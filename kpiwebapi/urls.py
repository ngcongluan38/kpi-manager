from django.conf import settings
from django.contrib import admin
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from rest_framework_jwt import views
from kpi_manager import views as kpiviews

urlpatterns = [
    # url(r'', kpiviews.HomeIndexView.as_view(), name='home_page'),
    url(r'^home/', login_required(kpiviews.HomeIndexView.as_view()), name='home'),
    url(r'^my-kpi/print/(?P<year_request>[\w-]+)/(?P<month_request>[\w-]+)/$',
        login_required(kpiviews.StatisticTagView.as_view()), name='print'),
    url(r'^kpi/print/(?P<profile_id>[\w-]+)/(?P<year_request>[\w-]+)/(?P<month_request>[\w-]+)/$',
        login_required(kpiviews.MemberStatisticTagView.as_view()), name='member_print'),
    url(r'^kpi_admin/', admin.site.urls),
    url(r'', include('web_api.urls')),
    # url(r'^$', kpiviews.HomeIndexView.as_view(), name='home'),

    # url(r'^web-api/', include('web_api.urls', namespace='web_api')),

    # url(r'^account/', include('registration.urls', namespace='registration')),
    url(r'', include('registration.urls', namespace='registration')),
    url(r'^api-token-verify/', views.verify_jwt_token),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
