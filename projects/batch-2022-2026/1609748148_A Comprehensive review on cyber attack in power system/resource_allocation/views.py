from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from .models import ResourceAllocation
from threats.models import PlantAsset
from risk_assessment.models import TAMAssessment
from security_controls.models import SecurityControl
from authentication.decorators import role_required

class AllocationForm(forms.ModelForm):
    class Meta:
        model = ResourceAllocation
        fields = ['title', 'asset', 'priority', 'assigned_controls',
                  'budget_allocated', 'personnel_assigned', 'notes']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxSelectMultiple):
                pass
            else:
                field.widget.attrs['class'] = 'form-control'

@login_required
def allocation_list(request):
    allocations = ResourceAllocation.objects.all().order_by('priority', '-created_at')
    # Get high-risk assets for prioritization panel
    high_risk_assessments = TAMAssessment.objects.filter(
        risk_level__in=['critical', 'high']
    ).order_by('-overall_risk_score')[:8]
    context = {
        'allocations': allocations,
        'high_risk_assessments': high_risk_assessments,
        'critical_count': allocations.filter(priority='critical').count(),
        'high_count': allocations.filter(priority='high').count(),
    }
    return render(request, 'resource_allocation/allocation_list.html', context)

@login_required
@role_required('admin')
def allocation_create(request):
    # Pre-fill asset if passed via query param
    initial = {}
    asset_id = request.GET.get('asset')
    if asset_id:
        initial['asset'] = asset_id
    form = AllocationForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        allocation = form.save(commit=False)
        allocation.allocated_by = request.user.username
        allocation.save()
        form.save_m2m()
        messages.success(request, f'Resource allocation created for {allocation.asset.name}.')
        return redirect('resource_allocation:list')
    assets_with_risk = []
    for asset in PlantAsset.objects.all():
        latest = TAMAssessment.objects.filter(asset=asset).order_by('-assessment_date').first()
        assets_with_risk.append({'asset': asset, 'latest': latest})
    return render(request, 'resource_allocation/allocation_form.html', {
        'form': form, 'assets_with_risk': assets_with_risk, 'action': 'Create'
    })

@login_required
@role_required('admin')
def allocation_edit(request, pk):
    allocation = get_object_or_404(ResourceAllocation, pk=pk)
    form = AllocationForm(request.POST or None, instance=allocation)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Allocation updated.')
        return redirect('resource_allocation:list')
    return render(request, 'resource_allocation/allocation_form.html', {
        'form': form, 'action': 'Edit', 'allocation': allocation
    })

@login_required
@role_required('admin')
def allocation_delete(request, pk):
    allocation = get_object_or_404(ResourceAllocation, pk=pk)
    if request.method == 'POST':
        allocation.delete()
        messages.success(request, 'Allocation deleted.')
        return redirect('resource_allocation:list')
    return render(request, 'resource_allocation/allocation_confirm_delete.html', {'allocation': allocation})