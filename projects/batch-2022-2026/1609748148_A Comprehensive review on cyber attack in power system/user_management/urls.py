from django.urls import path
from . import views

app_name = 'user_management'

urlpatterns = [
    path('', views.user_list, name='list'),
    path('create/', views.create_user, name='create'),
    path('edit/<int:pk>/', views.edit_user, name='edit'),
    path('toggle/<int:pk>/', views.toggle_user, name='toggle'),
    path('delete/<int:pk>/', views.delete_user, name='delete'),
]