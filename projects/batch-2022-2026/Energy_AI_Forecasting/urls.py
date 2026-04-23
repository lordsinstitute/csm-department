"""
URL configuration for Microscopic_image_of_Cancer_cell_Counting_using_Unet project.

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
from . import views as mainView
from admins import views as admins
from users import views as usr
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Main Views
    path("", mainView.index, name="index"),
    path("AdminLogin/", mainView.AdminLogin, name="AdminLogin"),
    path("UserLogin/", mainView.UserLogin, name="UserLogin"),  # Renders login form  # Handles POST

    path("UserRegister/", mainView.UserRegister, name="UserRegister"),  # Renders register form  # Handles POST

    # Admin Views
    path("AdminHome/", admins.adminHome, name="AdminHome"),
    path("adminlogin/", admins.adminLoginCheck, name="AdminLoginCheck"),
    path("RegisterUsersView/", admins.RegisterUsersView, name="RegisterUsersView"),
    path("ActivaUsers/", admins.activateUser, name="ActivaUsers"),
    path("deactivate_user/", admins.DeactivateUsers, name="deactivate_user"),
    path("delete_user/", admins.deleteUser, name="delete_user"),
    

    # User Views
    path("UserHome/", usr.UserHome, name="UserHome"),
    path("",usr.base,name='base'),
    path('predict/', usr.predict_anomaly, name='PredictAnomaly'),
    path("register/", usr.UserRegisterActions, name="register"), 
    path("UserLoginCheck/", usr.UserLoginCheck, name="UserLoginCheck"),
     
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)    

