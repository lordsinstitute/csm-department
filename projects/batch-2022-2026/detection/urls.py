from django.urls import path
from . import views

app_name = 'detection'

urlpatterns = [
    path('detect/<int:image_id>/', views.detect_microaneurysms, name='detect'),
    path('result/<int:result_id>/', views.detection_result, name='result'),
    path('results/', views.detection_list, name='list'),
    path('settings/', views.detection_settings, name='settings'),
    path('api/status/<int:image_id>/', views.api_detection_status, name='api_status'),
    path('stream/patient/<int:patient_id>/', views.detection_event_stream, name='stream'),
]