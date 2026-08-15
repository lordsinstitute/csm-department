from django.contrib import admin
from .models import Threat, Vulnerability, PlantAsset, ThreatCategory

admin.site.register(Threat)
admin.site.register(Vulnerability)
admin.site.register(PlantAsset)
admin.site.register(ThreatCategory)