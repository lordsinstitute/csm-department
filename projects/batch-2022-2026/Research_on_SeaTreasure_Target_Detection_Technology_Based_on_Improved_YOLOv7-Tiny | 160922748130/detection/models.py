from django.db import models
from django.contrib.auth.models import User


class DetectionJob(models.Model):
    STATUS_CHOICES = [
        ("pending",    "Pending"),
        ("processing", "Processing"),
        ("completed",  "Completed"),
        ("failed",     "Failed"),
    ]
    TYPE_CHOICES = [
        ("image", "Image"),
        ("video", "Video"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="detection_jobs")
    name = models.CharField(max_length=200, blank=True)
    job_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="image")
    input_file = models.FileField(upload_to="detection/inputs/")
    output_file = models.FileField(upload_to="detection/outputs/", blank=True, null=True)
    annotated_image = models.ImageField(upload_to="detection/annotated/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    error_message = models.TextField(blank=True)

    # Performance metrics
    inference_time_ms = models.FloatField(null=True, blank=True)
    total_detections = models.IntegerField(default=0)
    confidence_threshold = models.FloatField(default=0.25)
    iou_threshold = models.FloatField(default=0.45)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Job #{self.id} by {self.user.username} - {self.status}"


class DetectionResult(models.Model):
    SPECIES_CHOICES = [
        ("sea_cucumber", "Sea Cucumber"),
        ("sea_urchin",   "Sea Urchin"),
        ("shell",        "Shell"),
        ("other",        "Other"),
    ]

    job = models.ForeignKey(DetectionJob, on_delete=models.CASCADE, related_name="results")
    species = models.CharField(max_length=50, choices=SPECIES_CHOICES)
    confidence = models.FloatField()

    # Bounding box (YOLO format: x_center, y_center, width, height normalized)
    bbox_x = models.FloatField()
    bbox_y = models.FloatField()
    bbox_w = models.FloatField()
    bbox_h = models.FloatField()

    # Pixel coordinates
    pixel_x1 = models.IntegerField(default=0)
    pixel_y1 = models.IntegerField(default=0)
    pixel_x2 = models.IntegerField(default=0)
    pixel_y2 = models.IntegerField(default=0)

    frame_number = models.IntegerField(default=0)  # for video
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-confidence"]

    def __str__(self):
        return f"{self.species} ({self.confidence:.2f}) in Job #{self.job.id}"


class ModelMetrics(models.Model):
    """Stores model performance metrics."""
    model_name = models.CharField(max_length=100, default="UPA-YOLOv7-Tiny")
    model_version = models.CharField(max_length=50, default="1.0")
    map50 = models.FloatField(verbose_name="mAP@0.5", null=True, blank=True)
    map50_95 = models.FloatField(verbose_name="mAP@0.5:0.95", null=True, blank=True)
    precision = models.FloatField(null=True, blank=True)
    recall = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)
    gflops = models.FloatField(verbose_name="GFLOPs", null=True, blank=True)
    parameters_m = models.FloatField(verbose_name="Parameters (M)", null=True, blank=True)
    avg_inference_time_ms = models.FloatField(null=True, blank=True)
    dataset_name = models.CharField(max_length=200, blank=True)
    training_epochs = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Model Metrics"

    def __str__(self):
        return f"{self.model_name} v{self.model_version} mAP:{self.map50}"
