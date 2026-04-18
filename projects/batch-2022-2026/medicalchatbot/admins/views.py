from django.shortcuts import render,redirect
from django.contrib import messages
from django.utils.timezone import now
from django.views.decorators.cache import never_cache
from users.models import UserProfile

# Create your views here.
def adminlogin(request):
    return render(request,'adminlogin.html')
          
def adminlogincheck(request):
    if request.method == "POST":
        userid = request.POST.get('userid', '').strip()
        password = request.POST.get('password', '').strip()
        if (userid.lower() == 'admin') and (password.lower() == 'admin'):
            print('Valid admin login redirecting to AdminHome page')
            request.session['admin_logged_in'] = True
            request.session['admin_userid'] = userid
            return redirect('adminhome')  # redirect to adminhome view
        else:
            print('Invalid login credentials')
            messages.error(request,'INVALID LOGIN CREDINTIALS')
            return render(request, 'adminlogin.html', {'error': 'Invalid Admin ID or Password'})
    return render(request, 'adminlogin.html')


@never_cache
def adminhome(request):
    if not request.session.get('admin_logged_in'):
        return redirect('adminlogin')  # redirect to login page if not logged in

    userid = request.session.get('admin_userid', 'admin')
    current_time = now()
    return render(request, 'admins/AdminHome.html', {
        'userid': userid,
        'current_time': current_time
    })


def adminlogout(request):
    request.session.flush()
    return redirect('adminlogin')

def registreddusers(request):
    objects = UserProfile.objects.all()
    return render(request,'admins/registredusers.html',{'objects':objects})


from django.shortcuts import redirect, get_object_or_404

def activateuser(request, id):
    objects = UserProfile.objects.get(id=id)
    objects.status = 'active'
    objects.save()
    messages.success(request, f'User with ID-{id} is activated.')
    return redirect(registreddusers)

def blockuser(request, id):
    objects = UserProfile.objects.get(id=id)
    objects.status = 'blocked'  
    objects.save()
    messages.warning(request, f'User with ID-{id} is blocked.')
    return redirect(registreddusers)

def unblockuser(request,id):
    objects = UserProfile.objects.get(id=id)
    objects.status = 'active'
    objects.save()
    messages.success(request,f'User With ID -{id} is Unblocked')
    return redirect(registreddusers)

def deleteuser(request,id):
    objects = UserProfile.objects.get(id=id)
    objects.delete()
    messages.error(request,f'User With ID -{id} is deleted')

    return redirect(registreddusers)   





