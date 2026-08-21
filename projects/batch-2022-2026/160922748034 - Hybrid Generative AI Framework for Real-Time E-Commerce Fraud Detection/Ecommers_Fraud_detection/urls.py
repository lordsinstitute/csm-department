# Ecommers_Fraud_detection/urls.py
# URL configuration for Generative AI E-Commerce Fraud Detection project

from django.contrib import admin
from django.urls import path
from . import views as mainView
from admins import views as admins
from users import views as usr
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Landing pages
    path('', mainView.index, name='index'),
    path('AdminLogin/', mainView.AdminLogin, name='AdminLogin'),
    path('UserLogin/', mainView.UserLogin, name='UserLogin'),
    path('UserRegister/', mainView.UserRegister, name='UserRegister'),

    # Admin panel
    path('AdminHome/', admins.adminHome, name='AdminHome'),
    path('adminlogin/', admins.adminLoginCheck, name='AdminLoginCheck'),
    path('RegisterUsersView/', admins.RegisterUsersView, name='RegisterUsersView'),
    path('ActivaUsers/', admins.activateUser, name='ActivaUsers'),
    path('deactivate_user/', admins.DeactivateUsers, name='deactivate_user'),
    path('delete_user/', admins.deleteUser, name='delete_user'),

    # User panel
    path('UserHome/', usr.UserHome, name='UserHome'),
    path('register/', usr.UserRegisterActions, name='register'),
    path('UserLoginCheck/', usr.UserLoginCheck, name='UserLoginCheck'),

    # Core features
    path('upload/', usr.upload_dataset, name='upload_dataset'),
    path('analyse/', usr.analyse_dataset, name='analyse_dataset'),
    path('train/', usr.train_models, name='train_models'),
    path('generate/', usr.generate_data, name='generate_data'),
    path('predict/', usr.predict_fraud, name='predict_fraud'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)