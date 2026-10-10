from django.contrib import admin
from .models import SecurityControl, ControlAuditLog

admin.site.register(SecurityControl)
admin.site.register(ControlAuditLog)