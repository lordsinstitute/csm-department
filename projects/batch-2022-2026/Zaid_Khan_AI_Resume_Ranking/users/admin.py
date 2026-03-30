from django.contrib import admin

# Register your models here.
from .models import RankedResume,UserRegistrationModel

admin.site.register(RankedResume)

admin.site.register(UserRegistrationModel)