from django.db import models

class DetectionLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    packet_size = models.IntegerField()
    flow_duration = models.FloatField()
    src_bytes = models.IntegerField()
    dst_bytes = models.IntegerField()
    protocol = models.CharField(max_length=10)
    flag = models.CharField(max_length=10)
    prediction = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.timestamp} - {self.prediction}"
