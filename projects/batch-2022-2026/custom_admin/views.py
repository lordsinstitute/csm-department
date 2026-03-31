from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count
from django.views.decorators.http import require_http_methods
from django.db import connection
from users.models import CustomUser
from images.models import Patient, RetinaImage
from detection.models import DetectionResult
from .models import SystemLog, SystemConfig
import psutil
import os
from datetime import datetime, timedelta

def admin_required(function):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and (u.role == 'admin' or u.is_superuser),
        login_url='/users/login/'
    )
    return actual_decorator(function)

@login_required
@admin_required
def admin_dashboard(request):
    total_users = CustomUser.objects.count()
    total_patients = Patient.objects.count()
    total_images = RetinaImage.objects.count()
    total_detections = DetectionResult.objects.count()
    
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]
    recent_images = RetinaImage.objects.select_related('patient', 'uploaded_by').order_by('-upload_date')[:5]
    
    context = {
        'total_users': total_users,
        'total_patients': total_patients,
        'total_images': total_images,
        'total_detections': total_detections,
        'recent_users': recent_users,
        'recent_images': recent_images,
    }
    
    return render(request, 'custom_admin/dashboard.html', context)

@login_required
@admin_required
def user_management(request):
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    # Get filter and search parameters
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    sort_by = request.GET.get('sort', '-date_joined')
    
    # Start with all users
    users = CustomUser.objects.all()
    
    # Apply search filter
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Apply role filter
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Apply sorting
    valid_sorts = ['-date_joined', 'date_joined', 'username', '-username', 'first_name', '-first_name', 'role', '-role']
    if sort_by not in valid_sorts:
        sort_by = '-date_joined'
    users = users.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'sort_by': sort_by,
        'role_choices': CustomUser.ROLE_CHOICES,
        'total_users': CustomUser.objects.count(),
        'filtered_users': page_obj.paginator.count,
    }
    return render(request, 'custom_admin/user_management.html', context)

@login_required
@admin_required
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.role = request.POST.get('role', user.role)
        user.department = request.POST.get('department', user.department)
        user.phone = request.POST.get('phone', user.phone)
        user.is_active = request.POST.get('is_active') == 'on'
        user.save()
        
        messages.success(request, f'User {user.username} has been updated successfully!')
        return redirect('custom_admin:user_management')
    
    context = {
        'user': user,
        'role_choices': CustomUser.ROLE_CHOICES,
    }
    return render(request, 'custom_admin/edit_user.html', context)

@login_required
@admin_required
@require_http_methods(["POST"])
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    username = user.username
    
    # Prevent deleting yourself
    if user.id == request.user.id:
        messages.error(request, 'You cannot delete your own account!')
        return redirect('custom_admin:user_management')
    
    user.delete()
    messages.success(request, f'User {username} has been deleted successfully!')
    return redirect('custom_admin:user_management')

@login_required
@admin_required
def system_monitoring(request):
    # Get system resource usage
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
    except:
        cpu_percent = 0
        memory = None
        disk = None
    
    # Get database info
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users_customuser")
            db_users = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM images_patient")
            db_patients = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM images_retinaimage")
            db_images = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM detection_detectionresult")
            db_detections = cursor.fetchone()[0]
    except:
        db_users = db_patients = db_images = db_detections = 0
    
    # Get recent system logs (last 24 hours)
    last_24h = datetime.now() - timedelta(hours=24)
    recent_logs = SystemLog.objects.filter(timestamp__gte=last_24h).order_by('-timestamp')[:20]
    
    # Count logs by level
    log_levels = {
        'INFO': SystemLog.objects.filter(level='INFO', timestamp__gte=last_24h).count(),
        'WARNING': SystemLog.objects.filter(level='WARNING', timestamp__gte=last_24h).count(),
        'ERROR': SystemLog.objects.filter(level='ERROR', timestamp__gte=last_24h).count(),
        'CRITICAL': SystemLog.objects.filter(level='CRITICAL', timestamp__gte=last_24h).count(),
    }
    
    context = {
        'cpu_percent': cpu_percent,
        'memory': memory,
        'disk': disk,
        'db_users': db_users,
        'db_patients': db_patients,
        'db_images': db_images,
        'db_detections': db_detections,
        'recent_logs': recent_logs,
        'log_levels': log_levels,
        'server_time': datetime.now(),
    }
    return render(request, 'custom_admin/system_monitoring.html', context)