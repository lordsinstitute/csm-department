from django.urls import path
from . import views

app_name = 'monitoring'
urlpatterns = [
    path('', views.monitor_dashboard, name='dashboard'),
    path('api/live/', views.live_data_api, name='live_api'),
    path('network/', views.network_traffic, name='network_traffic'),
]
