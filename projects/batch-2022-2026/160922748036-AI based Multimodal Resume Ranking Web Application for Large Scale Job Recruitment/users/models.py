from django.db import models

# Create your models here.


class UserRegistrationModel(models.Model):
    name = models.CharField(max_length=100)
    loginid = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=100)
    mobile = models.CharField(unique=True, max_length=100)
    email = models.CharField(unique=True, max_length=100)
    state = models.CharField(default="NONE",max_length=100)
    status = models.CharField(max_length=100)

    def __str__(self):
        return self.loginid

    class Meta:
        db_table = 'UserRegistrations'





# models.py
from django.db import models

class RankedResume(models.Model):
    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=255, blank=True)
    similarity_score = models.FloatField()
    resume_file = models.FileField(upload_to='resumes/', null=True)
    status = models.CharField(max_length=20, default='present')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"


    