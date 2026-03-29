from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
	       path('Login.html', views.Login, name="Login"), 
	       path('Register.html', views.Register, name="Register"),
	       path('Signup', views.Signup, name="Signup"),
	       path('UserLogin', views.UserLogin, name="UserLogin"),
	       path('UploadFile.html', views.UploadFile, name="UploadFile"), 
	       path('UploadFileAction', views.UploadFileAction, name="UploadFileAction"),
	       path('DownloadFile', views.DownloadFile, name="DownloadFile"),
	       path('DownloadAction', views.DownloadAction, name="DownloadAction"),
	       path('ChangePassword.html', views.ChangePassword, name="ChangePassword"),
	       path('ChangePasswordAction', views.ChangePasswordAction, name="ChangePasswordAction"),
	       path('Graph', views.Graph, name="Graph"),	      
]