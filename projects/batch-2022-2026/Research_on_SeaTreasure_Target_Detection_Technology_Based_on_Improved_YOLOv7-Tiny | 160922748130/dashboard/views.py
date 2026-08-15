from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from accounts.models import UserProfile
from detection.models import DetectionJob, DetectionResult, ModelMetrics
from datasets.models import Dataset


def is_admin(user):
    try:
        return user.profile.role == "admin"
    except Exception:
        return user.is_superuser


@login_required
def index(request):
    """Route to user or admin dashboard."""
    if is_admin(request.user):
        return redirect("dashboard:admin_dashboard")
    return redirect("dashboard:user_dashboard")


@login_required
def user_dashboard(request):
    """User dashboard: personal stats, recent jobs."""
    user = request.user
    jobs = DetectionJob.objects.filter(user=user)
    recent_jobs = jobs[:5]
    total_jobs = jobs.count()
    completed = jobs.filter(status="completed").count()
    total_detections = jobs.aggregate(t=Count("results"))["t"] or 0
    species_dist = DetectionResult.objects.filter(job__user=user).values("species").annotate(count=Count("id"))
    metrics = ModelMetrics.objects.first()

    context = {
        "recent_jobs": recent_jobs,
        "total_jobs": total_jobs,
        "completed": completed,
        "total_detections": total_detections,
        "species_dist": list(species_dist),
        "metrics": metrics,
    }
    return render(request, "dashboard/user_dashboard.html", context)


@login_required
def admin_dashboard(request):
    """Admin dashboard: full system overview."""
    if not is_admin(request.user):
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect("dashboard:user_dashboard")

    total_users = User.objects.count()
    total_jobs = DetectionJob.objects.count()
    completed_jobs = DetectionJob.objects.filter(status="completed").count()
    failed_jobs = DetectionJob.objects.filter(status="failed").count()
    total_detections = DetectionResult.objects.count()
    total_datasets = Dataset.objects.count()

    # Recent activity
    recent_jobs = DetectionJob.objects.select_related("user").order_by("-created_at")[:10]
    recent_users = User.objects.order_by("-date_joined")[:5]

    # Species distribution
    species_dist = DetectionResult.objects.values("species").annotate(count=Count("id"))

    # Daily job trend (last 7 days)
    import datetime as dt
    today = timezone.now().date()
    trend = []
    for i in range(6, -1, -1):
        day = today - dt.timedelta(days=i)
        start = timezone.make_aware(dt.datetime.combine(day, dt.time.min))
        end = timezone.make_aware(dt.datetime.combine(day, dt.time.max))
        cnt = DetectionJob.objects.filter(created_at__range=(start, end)).count()
        trend.append({"date": day.strftime("%b %d"), "count": cnt})

    # Average inference time
    avg_inf = DetectionJob.objects.filter(status="completed").aggregate(
        avg=Avg("inference_time_ms")
    )["avg"] or 0


    metrics = ModelMetrics.objects.first()

    context = {
        "total_users": total_users,
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "total_detections": total_detections,
        "total_datasets": total_datasets,
        "recent_jobs": recent_jobs,
        "recent_users": recent_users,
        "species_dist": list(species_dist),
        "trend": trend,
        "avg_inf": round(avg_inf, 2),
        "metrics": metrics,
    }
    return render(request, "dashboard/admin_dashboard.html", context)


@login_required
def user_management(request):
    """Admin: Manage all users."""
    if not is_admin(request.user):
        return redirect("dashboard:index")
    users = User.objects.select_related("profile").all().order_by("-date_joined")
    return render(request, "dashboard/user_management.html", {"users": users})


@login_required
def toggle_user_status(request, user_id):
    """Admin: Enable/disable a user account."""
    if not is_admin(request.user):
        return redirect("dashboard:index")
    target_user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        target_user.is_active = not target_user.is_active
        target_user.save()
        status = "enabled" if target_user.is_active else "disabled"
        messages.success(request, f"User {target_user.username} {status}.")
    return redirect("dashboard:user_management")


@login_required
def change_user_role(request, user_id):
    """Admin: Change user role."""
    if not is_admin(request.user):
        return redirect("dashboard:index")
    target_user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        new_role = request.POST.get("role", "user")
        try:
            target_user.profile.role = new_role
            target_user.profile.save()
            messages.success(request, f"Role changed to {new_role} for {target_user.username}.")
        except Exception:
            messages.error(request, "Could not update role.")
    return redirect("dashboard:user_management")


@login_required
def system_monitor(request):
    """Admin: System resource monitoring."""
    if not is_admin(request.user):
        return redirect("dashboard:index")
    import platform
    import psutil
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    context = {
        "cpu_percent":    cpu,
        "mem_percent":    mem.percent,
        "mem_used_gb":    round(mem.used / 1e9, 2),
        "mem_total_gb":   round(mem.total / 1e9, 2),
        "disk_percent":   disk.percent,
        "disk_used_gb":   round(disk.used / 1e9, 2),
        "disk_total_gb":  round(disk.total / 1e9, 2),
        "platform":       platform.platform(),
        "python_version": platform.python_version(),
    }
    return render(request, "dashboard/system_monitor.html", context)


@login_required
def model_performance(request):
    """Admin: Detection model performance analytics."""
    if not is_admin(request.user):
        return redirect("dashboard:index")
    metrics_list = ModelMetrics.objects.all()
    return render(request, "dashboard/model_performance.html", {"metrics_list": metrics_list})
