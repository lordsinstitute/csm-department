import os
import random
import shutil
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, StreamingHttpResponse
import time
import json
from django.db.models import Q
from images.models import RetinaImage
from .models import DetectionResult, Microaneurysm
from .forms import DetectionSettingsForm, DetectionFilterForm
from .model import predict_image

@login_required
def detect_microaneurysms(request, image_id):
    """Handle microaneurysm detection for a specific image"""
    retina_image = get_object_or_404(RetinaImage, pk=image_id, uploaded_by=request.user)
    
    # Check if detection already exists
    if hasattr(retina_image, 'detection_result'):
        messages.info(request, 'Detection already performed for this image.')
        return redirect('images:image_detail', pk=image_id)
    
    if request.method == 'POST':
        try:
            # Create detection result with processing status
            detection_result = DetectionResult.objects.create(
                retina_image=retina_image,
                status='processing'
            )
            
            # Perform prediction using trained/fallback model
            detection_data = predict_image(retina_image)
            
            # Update detection result with processed data
            detection_result.processed_image = detection_data['processed_image_relative_path']
            # Handle non-fundus (safe) predictions
            if detection_data.get('non_fundus'):
                detection_result.microaneurysms_count = 0
                detection_result.lesion_area = 0.0
                detection_result.confidence_score = 0.0
                detection_result.safe_prediction = True
                detection_result.processing_time = detection_data.get('processing_time', 0.1)
                detection_result.status = 'completed'
                detection_result.save()

                # Mark image as non-fundus
                retina_image.image_type = 'NON_FUNDUS'
                retina_image.save()
            else:
                detection_result.microaneurysms_count = detection_data['ma_count']
                detection_result.lesion_area = detection_data['lesion_area']
                detection_result.confidence_score = detection_data['confidence']
                detection_result.processing_time = detection_data['processing_time']
                detection_result.status = 'completed'
                detection_result.save()

                # Create microaneurysm objects
                for ma_data in detection_data['microaneurysms']:
                    Microaneurysm.objects.create(
                        detection_result=detection_result,
                        x_coordinate=ma_data['x'],
                        y_coordinate=ma_data['y'],
                        diameter=ma_data['diameter'],
                        confidence=ma_data['confidence']
                    )
            
            messages.success(request, f'Detection completed! Found {detection_data["ma_count"]} microaneurysms.')
            return redirect('detection:result', result_id=detection_result.id)
            
        except Exception as e:
            # Handle detection failure
            if 'detection_result' in locals():
                detection_result.status = 'failed'
                detection_result.error_message = str(e)
                detection_result.save()
                messages.error(request, f'Detection failed: {str(e)}')
            else:
                messages.error(request, 'Detection failed to initialize.')
            
            return redirect('images:image_detail', pk=image_id)
    
    # GET request - show detection confirmation page
    return render(request, 'detection/detect.html', {'image': retina_image})


def detection_event_stream(request, patient_id):
    """Server-Sent Events stream that pushes new completed detections for a patient."""
    def event_stream():
        last_seen = None
        while True:
            last = DetectionResult.objects.filter(retina_image__patient__id=patient_id, status='completed').order_by('-detection_date').first()
            if last and last.id != last_seen:
                last_seen = last.id
                payload = {
                    'id': last.id,
                    'patient_id': last.retina_image.patient.id,
                    'microaneurysms_count': last.microaneurysms_count,
                    'confidence_score': last.confidence_score,
                    'lesion_area': last.lesion_area,
                    'detection_date': last.detection_date.strftime('%b %d, %H:%M'),
                    'safe_prediction': getattr(last, 'safe_prediction', False)
                }
                yield f"data: {json.dumps(payload)}\n\n"
            time.sleep(2)
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

# Note: Detection logic has been moved to detection/model.py
# The perform_mock_detection function is deprecated.
# Use predict_image() from detection.model instead for all detections.

@login_required
def detection_result(request, result_id):
    """Display detection results"""
    try:
        result = get_object_or_404(DetectionResult, pk=result_id, retina_image__uploaded_by=request.user)
        microaneurysms = result.microaneurysms.all()
        
        return render(request, 'detection/result.html', {
            'result': result,
            'microaneurysms': microaneurysms
        })
    except Exception as e:
        messages.error(request, f"Error loading detection results: {str(e)}")
        return redirect('detection:list')

@login_required
def detection_list(request):
    """List all detection results with filtering"""
    form = DetectionFilterForm(request.GET, user=request.user)
    results = DetectionResult.objects.filter(
        retina_image__uploaded_by=request.user
    ).select_related('retina_image__patient').order_by('-detection_date')
    
    # Apply filters
    if form.is_valid():
        status = form.cleaned_data.get('status')
        patient = form.cleaned_data.get('patient')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        
        if status:
            results = results.filter(status=status)
        if patient:
            results = results.filter(retina_image__patient=patient)
        if date_from:
            results = results.filter(detection_date__date__gte=date_from)
        if date_to:
            results = results.filter(detection_date__date__lte=date_to)
    
    return render(request, 'detection/list.html', {
        'results': results,
        'form': form
    })

@login_required
def detection_settings(request):
    """Detection settings page"""
    if request.method == 'POST':
        form = DetectionSettingsForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Detection settings updated successfully!')
            return redirect('detection:settings')
    else:
        form = DetectionSettingsForm()
    
    return render(request, 'detection/settings.html', {'form': form})

@login_required
def api_detection_status(request, image_id):
    """API endpoint to check detection status"""
    retina_image = get_object_or_404(RetinaImage, pk=image_id, uploaded_by=request.user)
    
    if hasattr(retina_image, 'detection_result'):
        result = retina_image.detection_result
        return JsonResponse({
            'status': result.status,
            'microaneurysms_count': result.microaneurysms_count,
            'confidence_score': result.confidence_score,
            'processing_time': result.processing_time
        })
    else:
        return JsonResponse({'status': 'not_started'})