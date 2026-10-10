from django.contrib import admin
from .models import DetectionResult, Microaneurysm

@admin.register(DetectionResult)
class DetectionResultAdmin(admin.ModelAdmin):
    list_display = ['get_patient_id', 'microaneurysms_count', 'confidence_score', 'status', 'detection_date']
    list_filter = ['status', 'detection_date']
    search_fields = ['retina_image__patient__patient_id', 'retina_image__patient__first_name']
    readonly_fields = ['detection_date', 'microaneurysms_count', 'lesion_area', 'confidence_score']
    
    def get_patient_id(self, obj):
        return obj.retina_image.patient.patient_id
    get_patient_id.short_description = 'Patient ID'

@admin.register(Microaneurysm)
class MicroaneurysmAdmin(admin.ModelAdmin):
    list_display = ['get_patient_id', 'x_coordinate', 'y_coordinate', 'diameter', 'confidence']
    list_filter = ['confidence', 'detection_result__detection_date']
    search_fields = ['detection_result__retina_image__patient__patient_id']
    readonly_fields = ['x_coordinate', 'y_coordinate', 'diameter', 'confidence']
    
    def get_patient_id(self, obj):
        return obj.detection_result.retina_image.patient.patient_id
    get_patient_id.short_description = 'Patient ID'