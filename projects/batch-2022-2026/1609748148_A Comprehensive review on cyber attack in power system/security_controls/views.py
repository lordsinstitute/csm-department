from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from .models import SecurityControl, ControlAuditLog, SecurityPolicy
from authentication.decorators import role_required

class SecurityControlForm(forms.ModelForm):
    class Meta:
        model = SecurityControl
        fields = ['nei_control_id', 'title', 'control_type', 'description',
                  'implementation_guidance', 'status', 'effectiveness_score',
                  'implemented_date']
        widgets = {'implemented_date': forms.DateInput(attrs={'type': 'date'})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class SecurityPolicyForm(forms.ModelForm):
    class Meta:
        model = SecurityPolicy
        fields = ['title', 'policy_number', 'description', 'scope',
                  'enforcement_level', 'status', 'version', 'review_date']
        widgets = {'review_date': forms.DateInput(attrs={'type': 'date'})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

@login_required
def control_list(request):
    controls = SecurityControl.objects.all()
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    if status_filter:
        controls = controls.filter(status=status_filter)
    if type_filter:
        controls = controls.filter(control_type=type_filter)
    context = {
        'controls': controls,
        'implemented': SecurityControl.objects.filter(status='implemented').count(),
        'partial': SecurityControl.objects.filter(status='partial').count(),
        'planned': SecurityControl.objects.filter(status='planned').count(),
        'not_implemented': SecurityControl.objects.filter(status='not_implemented').count(),
        'status_filter': status_filter,
        'type_filter': type_filter,
    }
    return render(request, 'security_controls/control_list.html', context)

@login_required
def control_detail(request, pk):
    control = get_object_or_404(SecurityControl, pk=pk)
    audit_logs = ControlAuditLog.objects.filter(control=control).order_by('-timestamp')[:10]
    mitigated_threats = control.mitigates_threats.all()
    applicable_assets = control.applicable_assets.all()
    return render(request, 'security_controls/control_detail.html', {
        'control': control,
        'audit_logs': audit_logs,
        'mitigated_threats': mitigated_threats,
        'applicable_assets': applicable_assets,
    })

@login_required
@role_required('admin')
def control_create(request):
    form = SecurityControlForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        control = form.save()
        ControlAuditLog.objects.create(
            control=control, action='Control Created',
            performed_by=request.user.username,
            notes=f'New control {control.nei_control_id} created.'
        )
        messages.success(request, f'Security control {control.nei_control_id} created.')
        return redirect('security_controls:detail', pk=control.pk)
    return render(request, 'security_controls/control_form.html', {'form': form, 'action': 'Create'})

@login_required
@role_required('admin')
def control_edit(request, pk):
    control = get_object_or_404(SecurityControl, pk=pk)
    old_status = control.status
    form = SecurityControlForm(request.POST or None, instance=control)
    if request.method == 'POST' and form.is_valid():
        control = form.save()
        if old_status != control.status:
            ControlAuditLog.objects.create(
                control=control,
                action=f'Status changed: {old_status} → {control.status}',
                performed_by=request.user.username
            )
        else:
            ControlAuditLog.objects.create(
                control=control, action='Control Updated',
                performed_by=request.user.username
            )
        messages.success(request, f'Control {control.nei_control_id} updated.')
        return redirect('security_controls:detail', pk=control.pk)
    return render(request, 'security_controls/control_form.html', {
        'form': form, 'action': 'Edit', 'control': control
    })

@login_required
@role_required('admin')
def control_delete(request, pk):
    control = get_object_or_404(SecurityControl, pk=pk)
    if request.method == 'POST':
        name = control.nei_control_id
        control.delete()
        messages.success(request, f'Control {name} deleted.')
        return redirect('security_controls:list')
    return render(request, 'security_controls/control_confirm_delete.html', {'control': control})

# ── Security Policies ──

@login_required
def policy_list(request):
    policies = SecurityPolicy.objects.all().order_by('-created_at')
    return render(request, 'security_controls/policy_list.html', {
        'policies': policies,
        'active_count': policies.filter(status='active').count(),
        'draft_count': policies.filter(status='draft').count(),
    })

@login_required
@role_required('admin')
def policy_create(request):
    form = SecurityPolicyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        policy = form.save(commit=False)
        policy.created_by = request.user.username
        policy.save()
        messages.success(request, f'Policy {policy.policy_number} created.')
        return redirect('security_controls:policy_list')
    return render(request, 'security_controls/policy_form.html', {'form': form, 'action': 'Create'})

@login_required
@role_required('admin')
def policy_edit(request, pk):
    policy = get_object_or_404(SecurityPolicy, pk=pk)
    form = SecurityPolicyForm(request.POST or None, instance=policy)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Policy {policy.policy_number} updated.')
        return redirect('security_controls:policy_list')
    return render(request, 'security_controls/policy_form.html', {
        'form': form, 'action': 'Edit', 'policy': policy
    })

@login_required
@role_required('admin')
def policy_delete(request, pk):
    policy = get_object_or_404(SecurityPolicy, pk=pk)
    if request.method == 'POST':
        policy.delete()
        messages.success(request, 'Policy deleted.')
        return redirect('security_controls:policy_list')
    return render(request, 'security_controls/policy_confirm_delete.html', {'policy': policy})