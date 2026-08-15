from django.contrib import admin
from .models import Dataset


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "total_images", "train_count", "val_count", "test_count", "uploaded_by", "created_at"]
    list_filter = ["status"]
    search_fields = ["name"]
