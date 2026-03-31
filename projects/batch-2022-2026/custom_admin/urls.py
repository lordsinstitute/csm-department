from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('users/', views.user_management, name='user_management'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('monitoring/', views.system_monitoring, name='system_monitoring'),
]