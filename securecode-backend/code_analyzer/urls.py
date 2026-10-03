from django.urls import path, re_path
from . import views

urlpatterns = [
    path('analyze/', views.analyze_code_api, name='api_analyze'),
    re_path(r'^report/(?P<report_id>[0-9a-fA-F]{32})/$', views.get_report_api, name='api_report'),
    path('health/', views.health_check_api, name='api_health'),
    path('download/cli/', views.download_cli, name='download_cli'),
]
