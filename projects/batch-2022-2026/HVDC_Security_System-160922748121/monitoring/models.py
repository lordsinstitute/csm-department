from django.db import models

class HVDCReading(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    dc_voltage = models.FloatField(help_text='DC Voltage in kV')
    dc_current = models.FloatField(help_text='DC Current in kA')
    ac_voltage_rectifier = models.FloatField(help_text='AC voltage at rectifier in kV')
    ac_voltage_inverter = models.FloatField(help_text='AC voltage at inverter in kV')
    active_power = models.FloatField(help_text='Active power in MW')
    reactive_power = models.FloatField(help_text='Reactive power in MVAR')
    firing_angle_rectifier = models.FloatField(help_text='Degrees')
    extinction_angle_inverter = models.FloatField(help_text='Degrees')
    converter_status = models.CharField(max_length=20,
        choices=[('normal','Normal'),('warning','Warning'),('fault','Fault')],
        default='normal')
    network_packet_rate = models.IntegerField(default=0, help_text='packets/sec')
    communication_latency = models.FloatField(default=0.0, help_text='ms')
    data_source = models.CharField(max_length=50, default='sensor')

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'Reading @ {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")} | {self.dc_voltage}kV'

class NetworkTraffic(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    source_ip = models.GenericIPAddressField()
    destination_ip = models.GenericIPAddressField()
    protocol = models.CharField(max_length=20)
    packet_size = models.IntegerField()
    packet_count = models.IntegerField()
    is_anomalous = models.BooleanField(default=False)

    class Meta: ordering = ['-timestamp']
