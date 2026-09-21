from django.db import models
from threats.models import Threat, PlantAsset

class SecurityControl(models.Model):
    CONTROL_TYPE_CHOICES = [
        ('preventive', 'Preventive'),
        ('detective', 'Detective'),
        ('corrective', 'Corrective'),
        ('compensating', 'Compensating'),
    ]
    STATUS_CHOICES = [
        ('implemented', 'Implemented'),
        ('partial', 'Partially Implemented'),
        ('planned', 'Planned'),
        ('not_implemented', 'Not Implemented'),
    ]
    nei_control_id = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    control_type = models.CharField(max_length=30, choices=CONTROL_TYPE_CHOICES)
    description = models.TextField()
    implementation_guidance = models.TextField()
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='planned')
    effectiveness_score = models.FloatField(default=0.0)
    applicable_assets = models.ManyToManyField(PlantAsset, blank=True)
    mitigates_threats = models.ManyToManyField(Threat, blank=True)
    last_reviewed = models.DateField(auto_now=True)
    implemented_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.nei_control_id} - {self.title}"

class ControlAuditLog(models.Model):
    control = models.ForeignKey(SecurityControl, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    performed_by = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.control.nei_control_id} - {self.action}"
    
class SecurityPolicy(models.Model):
    POLICY_STATUS = [
        ('active', 'Active'),
        ('draft', 'Draft'),
        ('retired', 'Retired'),
    ]
    title = models.CharField(max_length=200)
    policy_number = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    scope = models.TextField()
    enforcement_level = models.CharField(max_length=50, choices=[
        ('mandatory', 'Mandatory'),
        ('recommended', 'Recommended'),
        ('optional', 'Optional'),
    ], default='mandatory')
    status = models.CharField(max_length=20, choices=POLICY_STATUS, default='draft')
    version = models.CharField(max_length=20, default='1.0')
    created_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    review_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.policy_number} - {self.title}"

    class Meta:
        verbose_name_plural = "Security Policies"    