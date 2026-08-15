from django.db import models

class UserProfile(models.Model):    
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    status = models.CharField(max_length=20,  default='waiting')
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'