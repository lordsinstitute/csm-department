from django.urls import path
from . import views

app_name = 'security_controls'

urlpatterns = [
    path('', views.control_list, name='list'),
    path('create/', views.control_create, name='create'),
    path('<int:pk>/', views.control_detail, name='detail'),
    path('<int:pk>/edit/', views.control_edit, name='edit'),
    path('<int:pk>/delete/', views.control_delete, name='delete'),
    path('policies/', views.policy_list, name='policy_list'),
    path('policies/create/', views.policy_create, name='policy_create'),
    path('policies/<int:pk>/edit/', views.policy_edit, name='policy_edit'),
    path('policies/<int:pk>/delete/', views.policy_delete, name='policy_delete'),
]