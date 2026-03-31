from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "organization", "phone", "is_active", "created_at"]
    list_filter = ["role", "is_active"]
    search_fields = ["user__username", "user__email", "organization"]
    list_editable = ["role", "is_active"]
