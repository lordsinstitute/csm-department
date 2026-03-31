from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from images.models import Patient, RetinaImage
from detection.models import DetectionResult
from tracking.models import PatientVisit

@login_required
def home(request):
    total_patients = Patient.objects.filter(created_by=request.user).count()
    total_images = RetinaImage.objects.filter(uploaded_by=request.user).count()
    total_detections = DetectionResult.objects.filter(
        retina_image__uploaded_by=request.user
    ).count()
    
    recent_images = RetinaImage.objects.filter(
        uploaded_by=request.user
    ).select_related('patient').order_by('-upload_date')[:5]
    
    recent_visits = PatientVisit.objects.filter(
        created_by=request.user
    ).select_related('patient').order_by('-visit_date')[:5]
    
    context = {
        'total_patients': total_patients,
        'total_images': total_images,
        'total_detections': total_detections,
        'recent_images': recent_images,
        'recent_visits': recent_visits,
    }
    
    return render(request, 'dashboard/home.html', context)