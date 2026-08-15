from django.db import models
from threats.models import PlantAsset
from security_controls.models import SecurityControl

class ResourceAllocation(models.Model):
    PRIORITY_CHOICES = [
        ('critical', 'Critical Priority'),
        ('high', 'High Priority'),
        ('medium', 'Medium Priority'),
        ('low', 'Low Priority'),
    ]
    asset = models.ForeignKey(PlantAsset, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    assigned_controls = models.ManyToManyField(SecurityControl, blank=True)
    budget_allocated = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    personnel_assigned = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    allocated_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.asset.name}"