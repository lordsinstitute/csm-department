from django.contrib import admin
from .models import UserProfile,Chat,Message



# Register your models here.
class adminmodel(admin.ModelAdmin):
    list_display = ('first_name','last_name','email','mobile','status')
    search_fields = ('email','mobile')

admin.site.register(UserProfile,adminmodel)
admin.site.register(Chat)
admin.site.register(Message)

