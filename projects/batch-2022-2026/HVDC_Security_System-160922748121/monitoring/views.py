from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import HVDCReading, NetworkTraffic
import json

@login_required
def monitor_dashboard(request):
    readings = HVDCReading.objects.order_by('-timestamp')[:50]
    latest = readings.first()
    latest_params = []
    if latest:
        latest_params = [
            ('DC Voltage',    f'{latest.dc_voltage:.2f}',          'kV',    '#00b4d8'),
            ('DC Current',    f'{latest.dc_current:.3f}',          'kA',    '#f59e0b'),
            ('Active Power',  f'{latest.active_power:.1f}',        'MW',    '#10b981'),
            ('Packet Rate',   str(latest.network_packet_rate),     'pkt/s', '#a855f7'),
        ]
    ctx = {
        'readings': readings,
        'latest': latest,
        'latest_params': latest_params,
    }
    return render(request, 'monitoring/dashboard.html', ctx)
@login_required
def live_data_api(request):
    """Returns JSON of latest 20 readings for charts."""
    readings = HVDCReading.objects.order_by('-timestamp')[:20]
    data = [{'time': r.timestamp.strftime('%H:%M:%S'),
             'voltage': r.dc_voltage, 'current': r.dc_current,
             'power': r.active_power, 'status': r.converter_status}
            for r in readings]
    return JsonResponse({'data': list(reversed(data))})

@login_required
def network_traffic(request):
    traffic = NetworkTraffic.objects.order_by('-timestamp')[:100]
    return render(request, 'monitoring/network_traffic.html', {'traffic': traffic})
