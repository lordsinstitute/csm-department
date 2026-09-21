"""
URL configuration for traffic_signal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from users import views as user_views
from admins import views as admin_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_views.home, name='home'),
    path('user_profile_create/', user_views.user_profile_create, name='user_profile_create'),
    path('userlogin/', user_views.user_login, name='userlogin'),
    path('userhome/', user_views.user_home, name='userhome'),
    path('yolo_predict/', user_views.upload_file, name='yolo_predict'),
    path('upload_file/', user_views.upload_file, name='upload_file'),
    path('live/', user_views.live_feed, name='live_feed'),
    path('live_view/', user_views.live_view, name='live_view'),
    path('metrics/', user_views.metrics_view, name='metrics'),


    path('adminlogin/', admin_views.adminlogin, name='adminlogin'),
    path('adminhome/', admin_views.adminhome, name='adminhome'),
    path('view_users/', admin_views.view_users, name='view_users'),
    path('activate_user/<int:user_id>/', admin_views.activate_user, name='activate_user'),
    path('block_user/<int:user_id>/', admin_views.block_user, name='block_user'),
    path('delete_user/<int:user_id>/', admin_views.delete_user, name='delete_user'),
]