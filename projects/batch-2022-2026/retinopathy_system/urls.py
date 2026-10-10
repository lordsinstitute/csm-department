from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', include('custom_admin.urls')),
    path('', include('dashboard.urls')),
    path('users/', include('users.urls')),
    path('images/', include('images.urls')),
    path('detection/', include('detection.urls')),
    path('tracking/', include('tracking.urls')),
    path('reports/', include('reports.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)