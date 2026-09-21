from django.db import models

class PlantAsset(models.Model):
    ASSET_TYPE_CHOICES = [
        ('scada', 'SCADA System'),
        ('dcs', 'Distributed Control System'),
        ('plc', 'Programmable Logic Controller'),
        ('network', 'Network Infrastructure'),
        ('server', 'Server'),
        ('workstation', 'Workstation'),
        ('safety', 'Safety System'),
    ]
    CRITICALITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    name = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=50, choices=ASSET_TYPE_CHOICES)
    location = models.CharField(max_length=200)
    criticality = models.CharField(max_length=20, choices=CRITICALITY_CHOICES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.asset_type})"

class ThreatCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Threat(models.Model):
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('mitigated', 'Mitigated'),
        ('monitoring', 'Monitoring'),
        ('resolved', 'Resolved'),
    ]
    title = models.CharField(max_length=200)
    category = models.ForeignKey(ThreatCategory, on_delete=models.SET_NULL, null=True)
    affected_assets = models.ManyToManyField(PlantAsset)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    description = models.TextField()
    attack_vector = models.CharField(max_length=100)
    potential_impact = models.TextField()
    likelihood_score = models.FloatField(default=0.0)
    impact_score = models.FloatField(default=0.0)
    detected_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def risk_score(self):
        return round(self.likelihood_score * self.impact_score, 2)

class Vulnerability(models.Model):
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    asset = models.ForeignKey(PlantAsset, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    cve_id = models.CharField(max_length=50, blank=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    description = models.TextField()
    cvss_score = models.FloatField(default=0.0)
    is_patched = models.BooleanField(default=False)
    discovered_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cve_id} - {self.title}"