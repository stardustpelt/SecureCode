from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze_code_api, name='api_analyze'),
    path('report/<str:filename>/', views.get_report_api, name='api_report'),
    path('health/', views.health_check_api, name='api_health'),
]
