from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from authentication.models import CustomUser
from authentication.forms import RegisterForm
from authentication.decorators import role_required
from django import forms

class EditUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'role', 'department', 'phone', 'is_active']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'

@login_required
@role_required('admin')
def user_list(request):
    users = CustomUser.objects.all().order_by('-created_at')
    return render(request, 'user_management/user_list.html', {'users': users})

@login_required
@role_required('admin')
def create_user(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'User created successfully.')
        return redirect('user_management:list')
    return render(request, 'user_management/create_user.html', {'form': form})

@login_required
@role_required('admin')
def edit_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    form = EditUserForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'User {user.username} updated successfully.')
        return redirect('user_management:list')
    return render(request, 'user_management/edit_user.html', {'form': form, 'edit_user': user})

@login_required
@role_required('admin')
def toggle_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    user.is_active = not user.is_active
    user.save()
    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f'User {user.username} has been {status}.')
    return redirect('user_management:list')

@login_required
@role_required('admin')
def delete_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('user_management:list')
    username = user.username
    user.delete()
    messages.success(request, f'User {username} deleted.')
    return redirect('user_management:list')