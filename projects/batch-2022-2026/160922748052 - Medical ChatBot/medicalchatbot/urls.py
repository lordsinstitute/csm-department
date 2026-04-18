"""
URL configuration for traffic_accident project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from users import views as userviews
from admins import views as adminviews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.basefunction,name = 'basefunction'),
    path('demo/',views.demofunction,name = 'demofunction'),



    #userviews
    path('chatbot/',userviews.chatbot_view,name='chatbot'),
    path('chat/<int:chat_id>/history/', userviews.load_chat_history, name='load_chat_history'),  # load chat history
    path('chat/new/', userviews.create_new_chat, name='create_new_chat'),  # create new chat (POST)
    path('chat/<int:chat_id>/delete/', userviews.delete_chat, name='delete_chat'),
    path('signup_view/',userviews.signup_view,name='signup_view'),
    path('user_login/',userviews.user_login,name='user_login'),
    path('user_login_check/',userviews.user_login_check,name='user_login_check'),
    path('user_home_view/', userviews.user_home_view, name='user_home_view'),
    path('logout/', userviews.user_logout_view, name='user_logout'),


    # -----------------admin side urls----------------------------
    path('adminlogin/',adminviews.adminlogin,name='adminlogin'),
    path('adminlogincheck/',adminviews.adminlogincheck,name='adminlogincheck'),
    path('adminhome/',adminviews.adminhome,name='adminhome'),
    path('adminlogout/',adminviews.adminlogout,name='adminlogout'),
    path('registreddusers/',adminviews.registreddusers,name='registreddusers'),
    path('activateuser/<int:id>/',adminviews.activateuser,name='activateuser'),
    path('blockuser/<int:id>/',adminviews.blockuser,name='blockuser'),
    path('unblockuser/<int:id>/',adminviews.unblockuser,name='unblockuser'),
    path('deleteuser/<int:id>/',adminviews.deleteuser,name='deleteuser')
    

    # path("api/chatbot/", userviews.chatbot_api, name="chatbot_api"),
]
