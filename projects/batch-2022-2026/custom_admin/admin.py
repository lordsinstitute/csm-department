from django.contrib import admin
from .models import SystemLog, SystemConfig

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'level', 'module', 'user', 'message_preview']
    list_filter = ['level', 'timestamp', 'module']
    search_fields = ['message', 'module', 'user__username']
    readonly_fields = ['timestamp', 'user', 'ip_address', 'message']
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'

@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ['key', 'value_preview', 'updated_at']
    search_fields = ['key', 'description']
    readonly_fields = ['updated_at']
    
    def value_preview(self, obj):
        return obj.value[:50] + '...' if len(obj.value) > 50 else obj.value
    value_preview.short_description = 'Value'
