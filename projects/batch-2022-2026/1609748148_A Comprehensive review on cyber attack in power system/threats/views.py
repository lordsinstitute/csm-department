from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from .models import Threat, Vulnerability, PlantAsset, ThreatCategory

@login_required
def threat_list(request):
    threats = Threat.objects.all().order_by('-detected_date')
    severity_filter = request.GET.get('severity', '')
    status_filter = request.GET.get('status', '')
    
    if severity_filter:
        threats = threats.filter(severity=severity_filter)
    if status_filter:
        threats = threats.filter(status=status_filter)
    
    context = {
        'threats': threats,
        'total_threats': Threat.objects.count(),
        'critical_threats': Threat.objects.filter(severity='critical').count(),
        'active_threats': Threat.objects.filter(status='active').count(),
        'severity_filter': severity_filter,
        'status_filter': status_filter,
    }
    return render(request, 'threats/threat_list.html', context)

@login_required
def threat_detail(request, pk):
    threat = get_object_or_404(Threat, pk=pk)
    return render(request, 'threats/threat_detail.html', {'threat': threat})

@login_required
def vulnerability_list(request):
    vulnerabilities = Vulnerability.objects.all().order_by('-cvss_score')
    assets = PlantAsset.objects.all()
    context = {
        'vulnerabilities': vulnerabilities,
        'assets': assets,
        'critical_vulns': vulnerabilities.filter(severity='critical').count(),
        'unpatched_vulns': vulnerabilities.filter(is_patched=False).count(),
    }
    return render(request, 'threats/vulnerability_list.html', context)

@login_required
def asset_list(request):
    assets = PlantAsset.objects.all()
    return render(request, 'threats/asset_list.html', {'assets': assets})

@login_required
def asset_risk_overview(request):
    from risk_assessment.models import TAMAssessment
    from security_controls.models import SecurityControl

    assets = PlantAsset.objects.all()
    asset_data = []
    for asset in assets:
        latest_assessment = TAMAssessment.objects.filter(
            asset=asset).order_by('-assessment_date').first()
        threat_count = Threat.objects.filter(
            affected_assets=asset, status='active').count()
        vuln_count = Vulnerability.objects.filter(
            asset=asset, is_patched=False).count()
        asset_data.append({
            'asset': asset,
            'assessment': latest_assessment,
            'active_threats': threat_count,
            'unpatched_vulns': vuln_count,
        })

    # Sort by risk score descending
    asset_data.sort(
        key=lambda x: x['assessment'].overall_risk_score if x['assessment'] else 0,
        reverse=True
    )

    return render(request, 'threats/asset_risk_overview.html', {
        'asset_data': asset_data,
    })