"""
URL configuration for Building Safety through ML-Based Smoke Detection (SmokeGuard AI).
See: https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, re_path
from django.views.static import serve
from admins import views as mainView
from admins import views as admins
from users import views as usr
from django.conf.urls.static import static
from django.conf import settings


def favicon(request):
    svg = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
      <defs>
        <linearGradient id="g" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="#ff9944"/>
          <stop offset="100%" stop-color="#ff3344"/>
        </linearGradient>
      </defs>
      <rect width="64" height="64" rx="12" ry="12" fill="#141210"/>
      <path d="M32 8 C22 20 20 26 20 32 C20 40 26 46 32 46 C38 46 44 40 44 32 C44 27 42 22 36 16 L32 8 Z" fill="url(#g)"/>
      <circle cx="32" cy="40" r="6" fill="#ffffff" fill-opacity="0.9"/>
    </svg>
    """.strip()
    return HttpResponse(svg, content_type="image/svg+xml")


urlpatterns = [
    path('admin/', admin.site.urls),
    path("favicon.ico", favicon, name="favicon"),
    path("", mainView.index, name="index"),
    path("admin-login/", mainView.AdminLogin, name="AdminLogin"),
    path("user-login/", mainView.UserLogin, name="UserLogin"),
    path("user-register/", mainView.UserRegister, name="UserRegister"),

    # Admin views
    path("AdminHome/", admins.AdminHome, name="AdminHome"),
    path("AdminLoginCheck/", admins.AdminLoginCheck, name="AdminLoginCheck"),
    path('RegisterUsersView/', admins.RegisterUsersView, name='RegisterUsersView'),
    path('ActivaUsers/', admins.ActivaUsers, name='ActivaUsers'),

    # User views
    path("UserRegisterActions/", usr.UserRegisterActions, name="UserRegisterActions"),
    path("UserLoginCheck/", usr.UserLoginCheck, name="UserLoginCheck"),
    path("UserHome/", usr.UserHome, name="UserHome"),
    path("DatasetView/", usr.DatasetView, name="DatasetView"),
    path("training/", usr.Training, name="Training"),
    path("prediction/", usr.Prediction, name="prediction"),
    path("cnn-prediction/", usr.CNNPrediction, name="CNNPrediction"),  # CNN module
]

# Always serve media files (uploaded images, YOLO results)
# This replaces the static() helper which only works when DEBUG=True
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
