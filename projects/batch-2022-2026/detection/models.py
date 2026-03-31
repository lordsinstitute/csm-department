from django.db import models
from images.models import RetinaImage

class DetectionResult(models.Model):
    retina_image = models.OneToOneField(RetinaImage, on_delete=models.CASCADE, related_name='detection_result')
    processed_image = models.ImageField(upload_to='retina_images/processed/', blank=True, max_length=500)
    microaneurysms_count = models.IntegerField(default=0)
    lesion_area = models.FloatField(default=0.0)
    confidence_score = models.FloatField(default=0.0)
    safe_prediction = models.BooleanField(default=False)
    detection_date = models.DateTimeField(auto_now_add=True)
    processing_time = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=(
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ), default='pending')
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"Detection for {self.retina_image.patient.patient_id}"

class Microaneurysm(models.Model):
    detection_result = models.ForeignKey(DetectionResult, on_delete=models.CASCADE, related_name='microaneurysms')
    x_coordinate = models.IntegerField()
    y_coordinate = models.IntegerField()
    diameter = models.FloatField()
    confidence = models.FloatField()
    
    class Meta:
        ordering = ['-confidence']

    def __str__(self):
        return f"MA at ({self.x_coordinate}, {self.y_coordinate})"