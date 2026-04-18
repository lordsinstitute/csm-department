from django.db import models
from django.utils import timezone

class UserProfile(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15,unique=True)
    password = models.CharField(max_length=128)  # Store hashed password
    login_time = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    number_of_visitors = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, default='waiting')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



from django.db import models
from django.contrib.auth.models import User

class Chat(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.CharField(max_length=10)  # 'user' or 'bot'
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)






