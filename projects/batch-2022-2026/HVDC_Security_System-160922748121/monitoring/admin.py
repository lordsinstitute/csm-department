from django.contrib import admin
from .models import HVDCReading, NetworkTraffic

@admin.register(HVDCReading)
class HVDCReadingAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'dc_voltage', 'dc_current', 'active_power', 'converter_status']
    list_filter = ['converter_status']

@admin.register(NetworkTraffic)
class NetworkTrafficAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'source_ip', 'destination_ip', 'protocol', 'is_anomalous']
    list_filter = ['is_anomalous', 'protocol']
