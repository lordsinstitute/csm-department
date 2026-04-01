from django.shortcuts import render

import os
from django.shortcuts import render
from django.contrib import messages
from users.models import UserRegistrationModel

from django.shortcuts import render
from django.contrib import messages

def adminLoginCheck(request):
    if request.method == 'POST':
        usrid = request.POST.get('loginid')
        pswd = request.POST.get('password')  # should match input name in HTML
        print("User ID is = ", usrid)
        print('Password = ', pswd)

        if usrid == 'admin' and pswd == 'admin':
            users_count = UserRegistrationModel.objects.count()
            active_users = UserRegistrationModel.objects.filter(status='activated').count()
            return render(request, 'admins/AdminHome.html', {'users_count': users_count, 'active_users': active_users})

        else:
            messages.error(request, 'Invalid login ID or password')
            return render(request, 'AdminLogin.html')  # This should match the actual template path

    return render(request, 'AdminLogin.html')  # fallback if not POST

def adminHome(request):
    users_count = UserRegistrationModel.objects.count()
    active_users = UserRegistrationModel.objects.filter(status='activated').count()
    return render(request, 'admins/AdminHome.html', {'users_count': users_count, 'active_users': active_users})

def RegisterUsersView(request):
    data = UserRegistrationModel.objects.all()
    return render(request,'admins/viewregisters.html',{'obj':data})


def activateUser(request):
    if request.method == 'GET':
        id = request.GET.get('uid')
        status = 'activated'
        print("PID = ", id, status)
        UserRegistrationModel.objects.filter(id=id).update(status=status)
        data = UserRegistrationModel.objects.all()
        return render(request,'admins/viewregisters.html',{'obj':data})



def DeactivateUsers(request):
    if request.method == 'GET':
        uid = request.GET.get('uid')
        if uid:
            print("Deactivating user ID = ", uid)
            UserRegistrationModel.objects.filter(id=uid).update(status='deactivated')
        else:
            print("No user ID provided for deactivation.")

        data = UserRegistrationModel.objects.all()
        return render(request, 'admins/viewregisters.html', {'obj': data})
    



def deleteUser(request):
    if request.method == 'GET':
        id = request.GET.get('uid')
        
        #print("PID = ", id, status)
        UserRegistrationModel.objects.filter(id=id).delete()
        data = UserRegistrationModel.objects.all()
        return render(request,'admins/viewregisters.html',{'obj':data})
    