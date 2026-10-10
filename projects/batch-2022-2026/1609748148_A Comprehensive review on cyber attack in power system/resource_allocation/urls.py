from django.urls import path
from . import views

app_name = 'resource_allocation'

urlpatterns = [
    path('', views.allocation_list, name='list'),
    path('create/', views.allocation_create, name='create'),
    path('<int:pk>/edit/', views.allocation_edit, name='edit'),
    path('<int:pk>/delete/', views.allocation_delete, name='delete'),
]