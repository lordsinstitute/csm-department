from django.db import models
from django.contrib.auth.models import User


class Dataset(models.Model):
    STATUS_CHOICES = [
        ("raw",        "Raw"),
        ("processed",  "Processed"),
        ("training",   "Training"),
        ("validated",  "Validated"),
    ]
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="datasets/uploads/", blank=True, null=True)
    source_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="raw")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    total_images = models.IntegerField(default=0)
    train_count = models.IntegerField(default=0)
    val_count = models.IntegerField(default=0)
    test_count = models.IntegerField(default=0)
    classes = models.JSONField(default=list)  # e.g. ["sea_cucumber","sea_urchin","shell"]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created_at"]
