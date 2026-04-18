import os
from django.shortcuts import render
from django.contrib import messages
from users.forms import UserRegistrationForm
from users.models import UserRegistrationModel


def AdminLoginCheck(request):
    if request.method == 'POST':
        usrid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        admin_user = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin')
        if usrid == admin_user and pswd == admin_pass:
            return render(request, 'admins/AdminHome.html')
        messages.success(request, 'Please check your login details.')
    return render(request, 'AdminLogin.html', {})

def AdminHome(request):
    return render(request, 'admins/AdminHome.html',{})

def RegisterUsersView(request):
    data = UserRegistrationModel.objects.all()
    return render(request,'admins/viewregisterusers.html',{'data':data})


def ActivaUsers(request):
    if request.method == 'GET':
        id = request.GET.get('uid')
        status = 'activated'
        print("PID = ", id, status)
        UserRegistrationModel.objects.filter(id=id).update(status=status)
        data = UserRegistrationModel.objects.all()
        return render(request,'admins/viewregisterusers.html',{'data':data})


from django.shortcuts import render
from users.forms import UserRegistrationForm


def index(request):
    return render(request, 'index.html', {})

def AdminLogin(request):
    return render(request, 'AdminLogin.html', {})

def UserLogin(request):
    return render(request, 'UserLogin.html', {})


def UserRegister(request):
    form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})