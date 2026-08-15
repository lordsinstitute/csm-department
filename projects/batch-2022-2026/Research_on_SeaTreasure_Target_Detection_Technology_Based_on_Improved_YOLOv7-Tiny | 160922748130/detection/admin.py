from django.contrib import admin
from .models import DetectionJob, DetectionResult, ModelMetrics


@admin.register(DetectionJob)
class DetectionJobAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "job_type", "status", "total_detections", "inference_time_ms", "created_at"]
    list_filter = ["status", "job_type"]
    search_fields = ["user__username", "name"]
    readonly_fields = ["created_at", "completed_at"]


@admin.register(DetectionResult)
class DetectionResultAdmin(admin.ModelAdmin):
    list_display = ["id", "job", "species", "confidence", "frame_number"]
    list_filter = ["species"]
    search_fields = ["job__id", "species"]


@admin.register(ModelMetrics)
class ModelMetricsAdmin(admin.ModelAdmin):
    list_display = ["model_name", "model_version", "map50", "precision", "recall", "avg_inference_time_ms", "created_at"]
