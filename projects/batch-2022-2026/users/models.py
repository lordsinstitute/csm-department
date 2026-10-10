from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
class UserRegistrationModel(models.Model):
    name = models.CharField(max_length=100)
    loginid = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=100)
    mobile = models.CharField(unique=True, max_length=100)
    email = models.CharField(unique=True, max_length=100)
    locality = models.CharField(max_length=100)
    address = models.CharField(max_length=1000)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    status = models.CharField(max_length=100)

    def __str__(self):
        return self.loginid

    class Meta:
        db_table = 'UserRegistrations'


# from django.db import models

# class TumorPrediction(models.Model):
#     patient_name = models.CharField(max_length=100)
#     uploaded_mri = models.ImageField(upload_to='uploads/mri/')
#     uploaded_pet = models.ImageField(upload_to='uploads/pet/')
#     fused_image = models.ImageField(upload_to='uploads/fused/', blank=True, null=True)
#     prediction_result = models.CharField(max_length=50, blank=True, null=True)
#     confidence_score = models.FloatField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.patient_name} - {self.prediction_result or 'Pending'}"

