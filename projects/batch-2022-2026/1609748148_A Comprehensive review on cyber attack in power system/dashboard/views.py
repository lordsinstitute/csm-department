from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from threats.models import Threat, Vulnerability, PlantAsset
from risk_assessment.models import TAMAssessment
from security_controls.models import SecurityControl
import json

@login_required
def home(request):
    threats = Threat.objects.all()
    assessments = TAMAssessment.objects.order_by('-assessment_date')[:5]
    
    severity_data = {
        'critical': threats.filter(severity='critical').count(),
        'high': threats.filter(severity='high').count(),
        'medium': threats.filter(severity='medium').count(),
        'low': threats.filter(severity='low').count(),
    }
    
    control_status = {
        'implemented': SecurityControl.objects.filter(status='implemented').count(),
        'partial': SecurityControl.objects.filter(status='partial').count(),
        'planned': SecurityControl.objects.filter(status='planned').count(),
        'not_implemented': SecurityControl.objects.filter(status='not_implemented').count(),
    }
    
    context = {
        'total_assets': PlantAsset.objects.count(),
        'total_threats': threats.count(),
        'critical_threats': threats.filter(severity='critical').count(),
        'active_threats': threats.filter(status='active').count(),
        'total_assessments': TAMAssessment.objects.count(),
        'total_controls': SecurityControl.objects.count(),
        'recent_assessments': assessments,
        'recent_threats': threats.order_by('-detected_date')[:5],
        'severity_data': json.dumps(severity_data),
        'control_status': json.dumps(control_status),
        'vulnerabilities_unpatched': Vulnerability.objects.filter(is_patched=False).count(),
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def admin_home(request):
    if request.user.role != 'admin':
        from django.shortcuts import redirect
        return redirect('dashboard:home')
    return home(request)