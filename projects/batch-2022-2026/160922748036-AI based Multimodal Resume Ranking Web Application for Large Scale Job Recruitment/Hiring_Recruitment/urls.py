"""Hiring_Recruitment URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from Hiring_Recruitment import views as mainview
from admins import views as admins
from users import views as usr

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", mainview.index, name="index"),
    path("AdminLogin/", mainview.AdminLogin, name="AdminLogin"),
    path("UserLogin/", mainview.UserLogin, name="UserLogin"),
    path("UserRegister/", mainview.UserRegister, name="UserRegister"),

    # adminviews
    path("AdminLoginCheck/", admins.AdminLoginCheck, name="AdminLoginCheck"),
    path("AdminHome/", admins.AdminHome, name="AdminHome"),
    path('RegisterUsersView/', admins.RegisterUsersView, name='RegisterUsersView'),
    path('ActivaUsers/', admins.ActivaUsers, name='ActivaUsers'),



    # User Views

    path("UserRegisterActions/", usr.UserRegisterActions,name="UserRegisterActions"),
    path("UserLoginCheck/", usr.UserLoginCheck, name="UserLoginCheck"),
    path("UserHome/", usr.UserHome, name="UserHome"),
    path('upload_resumes/', usr.index, name='upload_resumes'),
    path('application/',usr.application,name='application'),
    path('past_applications/', usr.past_applications, name='past_applications'),
    path('training/', usr.training, name='training'),

    path('send-email/', usr.send_offer_letter_to_candidate, name='send_email'),

    
    
]
