from django.shortcuts import render, redirect
from django.contrib import messages
from users.models import UserProfile

def adminlogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == 'admin' and password == 'admin':
            return render(request, 'admins/adminhome.html')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'adminlogin.html')
    return render(request, 'adminlogin.html')

def adminhome(request):
    return render(request, 'admins/adminhome.html')

def view_users(request):
    users = UserProfile.objects.all()
    return render(request, 'admins/view_users.html', {'users': users})

def activate_user(request, user_id):
    user = UserProfile.objects.get(id=user_id)
    user.status = 'active'
    user.save()
    return redirect('view_users')

def block_user(request, user_id):
    user = UserProfile.objects.get(id=user_id)
    user.status = 'waiting'
    user.save()
    return redirect('view_users')

def delete_user(request, user_id):
    user = UserProfile.objects.get(id=user_id)
    user.delete()
    return redirect('view_users')