## 🔗👨‍💻 Team

| Name                         | Roll Number  |
| ---------------------------- | ------------ |
| Mohammed Muzzammil Uddin     | 160922748121 |
| Syed Moosa                   | 160922748166 |
| Zuhaib Mohammed Abdul Waheed | 160922748160 |

**Project Guide:**
Mazher Uddin, Assistant Professor

**Co-Guide / HoD:**
Dr. Abdul Rasool Mohammed
Associate Professor & Head of Department, CSE (AIML)

**Institution:**
Lords Institute of Engineering and Technology, Hyderabad

---

# HVDC CyberSec — Cyber-Physical Security Monitoring Platform

## Tech Stack
- Python 3.11.9
- Django 5.x
- MySQL
- Bootstrap 5
- scikit-learn (Random Forest)
- ReportLab (PDF Generation)

---

## Setup Instructions

### Step 1 — Open Project Folder
```
cd D:\HVDC_Security_System
```

### Step 2 — Activate Virtual Environment
```
venv\Scripts\activate
```

### Step 3 — Install Requirements
```
pip install -r requirements.txt
```

### Step 4 — Create MySQL Database
Open MySQL shell and run:
```sql
CREATE DATABASE hvdc_cybersec_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'hvdc_user'@'localhost' IDENTIFIED BY 'hvdc_pass_2024';
GRANT ALL PRIVILEGES ON hvdc_cybersec_db.* TO 'hvdc_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 5 — Run Migrations
```
python manage.py makemigrations accounts
python manage.py makemigrations monitoring
python manage.py makemigrations threat_detection
python manage.py makemigrations reports
python manage.py makemigrations simulation
python manage.py makemigrations alerts
python manage.py makemigrations vulnerability
python manage.py makemigrations defense
python manage.py makemigrations dashboard
python manage.py migrate
```

### Step 6 — Generate Dataset
```
python datasets/generate_dataset.py
```

### Step 7 — Train AI Model
```
python ml_models/train_model.py
```

### Step 8 — Load All Sample Data

Run Django shell:
```
python manage.py shell
```

Paste this **entire block** at once:

```python
import random
from django.utils import timezone
from datetime import timedelta, date
from accounts.models import CustomUser

admin_user = CustomUser.objects.filter(is_superuser=True).first()
if not admin_user:
    admin_user = CustomUser.objects.first()
print(f"Using user: {admin_user.username}")

# ============================================================
# 1. HVDC READINGS (Monitoring)
# ============================================================
from monitoring.models import HVDCReading, NetworkTraffic

HVDCReading.objects.all().delete()
NetworkTraffic.objects.all().delete()

statuses = ['normal','normal','normal','normal','warning','fault']
for i in range(60):
    HVDCReading.objects.create(
        dc_voltage=500 + random.uniform(-15, 15),
        dc_current=2.0 + random.uniform(-0.3, 0.3),
        ac_voltage_rectifier=220 + random.uniform(-8, 8),
        ac_voltage_inverter=215 + random.uniform(-8, 8),
        active_power=1000 + random.uniform(-80, 80),
        reactive_power=50 + random.uniform(-15, 15),
        firing_angle_rectifier=15 + random.uniform(-3, 3),
        extinction_angle_inverter=18 + random.uniform(-3, 3),
        network_packet_rate=random.randint(100, 400),
        communication_latency=random.uniform(3, 10),
        converter_status=random.choice(statuses),
        data_source='sensor'
    )

for i in range(10):
    HVDCReading.objects.create(
        dc_voltage=480 + random.uniform(-30, 30),
        dc_current=3.5 + random.uniform(-0.5, 0.5),
        ac_voltage_rectifier=200 + random.uniform(-15, 15),
        ac_voltage_inverter=195 + random.uniform(-15, 15),
        active_power=850 + random.uniform(-100, 100),
        reactive_power=120 + random.uniform(-20, 20),
        firing_angle_rectifier=30 + random.uniform(-5, 5),
        extinction_angle_inverter=35 + random.uniform(-5, 5),
        network_packet_rate=random.randint(5000, 40000),
        communication_latency=random.uniform(100, 300),
        converter_status='fault',
        data_source='sensor'
    )

protocols = ['TCP','UDP','MODBUS','ICMP','DNP3']
for i in range(30):
    NetworkTraffic.objects.create(
        source_ip=f'192.168.{random.randint(1,5)}.{random.randint(1,254)}',
        destination_ip=f'10.0.{random.randint(0,3)}.{random.randint(1,50)}',
        protocol=random.choice(protocols),
        packet_size=random.randint(64, 1500),
        packet_count=random.randint(1, 10000),
        is_anomalous=random.random() < 0.25
    )

print(f"Readings: {HVDCReading.objects.count()} | Traffic: {NetworkTraffic.objects.count()}")

# ============================================================
# 2. THREAT DETECTION
# ============================================================
from threat_detection.models import ThreatLog, AIModel

ThreatLog.objects.all().delete()
AIModel.objects.all().delete()

attack_configs = [
    ('dos',       'critical', (0.88, 0.99), 'High packet rate flood on SCADA communication channel'),
    ('dos',       'high',     (0.75, 0.90), 'UDP flood detected on control network port 502'),
    ('fdi',       'critical', (0.85, 0.98), 'False voltage injection — sensor values inconsistent with physical model'),
    ('fdi',       'high',     (0.70, 0.88), 'Abnormal DC voltage spike inconsistent with physical model'),
    ('cmd_manip', 'critical', (0.90, 0.99), 'Unauthorized modification of firing angle control command'),
    ('cmd_manip', 'high',     (0.78, 0.92), 'Suspicious command sequence on converter control channel'),
    ('replay',    'medium',   (0.65, 0.82), 'Replayed control packet detected with stale timestamp'),
    ('replay',    'high',     (0.72, 0.88), 'Duplicate authentication token reuse detected'),
    ('normal',    'low',      (0.91, 0.99), 'Normal system operation confirmed'),
    ('normal',    'low',      (0.88, 0.99), 'Routine data transmission verified'),
]

for attack_type, severity, conf_range, desc in attack_configs:
    for _ in range(random.randint(2, 5)):
        ThreatLog.objects.create(
            attack_type=attack_type,
            severity=severity,
            confidence_score=round(random.uniform(*conf_range), 3),
            source_ip=f'192.168.{random.randint(1,5)}.{random.randint(1,254)}',
            dc_voltage=500 + random.uniform(-25, 25),
            dc_current=2.0 + random.uniform(-0.6, 0.6),
            active_power=1000 + random.uniform(-150, 150),
            network_packet_rate=random.randint(100, 45000),
            communication_latency=random.uniform(2, 250),
            description=desc,
            is_confirmed=random.random() > 0.4,
            detected_at=timezone.now() - timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23)
            )
        )

AIModel.objects.create(
    name='Random Forest Classifier', version='1.0',
    file_path='ml_models/hvdc_rf_model.pkl',
    accuracy=97.5, precision=97.3, recall=97.5, f1_score=97.4,
    threshold=0.5, is_active=True, trained_on=4000
)
AIModel.objects.create(
    name='Random Forest Classifier', version='0.9',
    file_path='ml_models/hvdc_rf_model_v09.pkl',
    accuracy=94.2, precision=93.8, recall=94.1, f1_score=93.9,
    threshold=0.5, is_active=False, trained_on=3000
)

print(f"Threats: {ThreatLog.objects.count()} | Models: {AIModel.objects.count()}")

# ============================================================
# 3. ALERTS
# ============================================================
from alerts.models import Alert, NotificationPreference

Alert.objects.all().delete()

alerts_data = [
    ('Critical DoS Attack Detected',    'Massive TCP flood on SCADA network port 502. Packet rate: 45,000/sec. Immediate action required.',                 'critical', 'AI Detector',     False),
    ('False Data Injection Attempt',     'Sensor voltage reading 520kV vs physical model prediction 500kV. Data integrity compromised.',                      'critical', 'AI Detector',     False),
    ('Command Manipulation Detected',    'Firing angle command modified from 15 to 31 degrees. Unauthorized control message intercepted.',                    'danger',   'AI Detector',     False),
    ('DC Voltage Anomaly',              'DC voltage dropped to 471kV — below safe operating threshold of 480kV.',                                            'warning',  'Monitoring',      False),
    ('High Communication Latency',       'Network latency on control channel exceeded 200ms. Normal range: 3-10ms.',                                         'warning',  'Network Monitor', False),
    ('Replay Attack Identified',         'Stale authentication token reused. Packet timestamp 47 seconds old.',                                              'danger',   'AI Detector',     False),
    ('Converter Status Warning',         'Rectifier converter entered warning state. Extinction angle outside normal range.',                                 'warning',  'Monitoring',      False),
    ('Unauthorized Login Attempt',       'Multiple failed login attempts from IP 192.168.3.45. Account locked after 5 attempts.',                            'critical', 'Auth System',     False),
    ('Firewall Rule Violation',          'Outbound connection on port 23 (Telnet) blocked. Source: 10.0.1.12.',                                              'warning',  'Firewall',        True),
    ('System Health Check Passed',       'All HVDC components operating within normal parameters. No anomalies detected.',                                   'info',     'System Monitor',  True),
    ('Scheduled Maintenance Alert',      'Planned maintenance window in 24 hours. Brief monitoring interruptions expected.',                                  'info',     'System',          True),
    ('Model Retraining Recommended',     'AI model accuracy dropped below 95% threshold. Recommend retraining with updated data.',                           'warning',  'AI Monitor',      False),
]

for title, msg, sev, src, resolved in alerts_data:
    a = Alert.objects.create(
        title=title, message=msg, severity=sev, source=src,
        is_resolved=resolved,
        created_at=timezone.now() - timedelta(hours=random.randint(0, 48))
    )
    if resolved:
        a.resolved_at = timezone.now() - timedelta(hours=random.randint(0, 10))
        a.resolved_by = admin_user
        a.save()

NotificationPreference.objects.get_or_create(
    user=admin_user,
    defaults={
        'email_on_critical': True,
        'email_on_high': True,
        'email_on_medium': False,
        'dashboard_notifications': True,
        'alert_sound': True,
    }
)

print(f"Alerts: {Alert.objects.count()} ({Alert.objects.filter(is_resolved=False).count()} active)")

# ============================================================
# 4. SIMULATION
# ============================================================
from simulation.models import AttackScenario, SimulationRun

AttackScenario.objects.all().delete()
SimulationRun.objects.all().delete()

scenarios_data = [
    (
        'DoS Flood Attack', 'dos',
        'Simulates a high-volume TCP/UDP flood attack targeting the HVDC SCADA communication network. Tests system resilience under extreme packet loads.',
        {'packet_rate': 50000, 'duration_sec': 60, 'target_port': 502, 'protocol': 'TCP'}
    ),
    (
        'False Voltage Injection', 'fdi',
        'Injects falsely elevated DC voltage readings into the sensor data stream to manipulate control system decisions.',
        {'target_sensor': 'dc_voltage', 'injection_value': 525.0, 'duration_sec': 30}
    ),
    (
        'Command Manipulation Attack', 'cmd_manip',
        'Alters firing angle commands sent to the HVDC rectifier converter, potentially causing instability in power transmission.',
        {'target_command': 'firing_angle', 'modified_value': 35.0, 'original_value': 15.0}
    ),
    (
        'Replay Attack Simulation', 'replay',
        'Replays previously captured valid control commands to cause unintended system state changes and bypass authentication.',
        {'delay_seconds': 45, 'packet_count': 1000, 'target': 'auth_channel'}
    ),
    (
        'Multi-Vector Combined Attack', 'cmd_manip',
        'Sophisticated multi-stage attack combining DoS flooding with simultaneous false data injection to overwhelm detection systems.',
        {'stages': ['dos', 'fdi'], 'coordination': 'simultaneous', 'duration_sec': 120}
    ),
]

created_scenarios = []
for name, atype, desc, params in scenarios_data:
    sc = AttackScenario.objects.create(
        name=name, attack_type=atype, description=desc, parameters=params
    )
    created_scenarios.append(sc)

results_list = [
    {'detection_result': 'Detected', 'mitigation': 'DoS protection activated', 'packets_blocked': 48320},
    {'detection_result': 'Detected', 'mitigation': 'Sensor validation triggered', 'anomaly_score': 0.94},
    {'detection_result': 'Detected', 'mitigation': 'Command rejected, original restored', 'confidence': 0.91},
    {'detection_result': 'Detected', 'mitigation': 'Token invalidated, session reset', 'stale_packets': 1000},
    {'detection_result': 'Partially Detected', 'mitigation': 'Stage 1 blocked, Stage 2 delayed', 'confidence': 0.78},
]

for i, scenario in enumerate(created_scenarios):
    for j in range(random.randint(1, 3)):
        v_impact = random.uniform(-20, -5) if scenario.attack_type in ['dos','cmd_manip'] else random.uniform(5, 25)
        p_impact = random.uniform(-35, -10) if scenario.attack_type == 'dos' else random.uniform(-15, 20)
        SimulationRun.objects.create(
            scenario=scenario,
            run_by=admin_user,
            status='completed',
            completed_at=timezone.now() - timedelta(hours=random.randint(1, 72)),
            voltage_impact=round(v_impact, 2),
            power_impact=round(p_impact, 2),
            detection_time_ms=random.randint(45, 850),
            results=results_list[i % len(results_list)],
            notes=f'Test run {j+1} — system response within expected parameters.'
        )

print(f"Scenarios: {AttackScenario.objects.count()} | Runs: {SimulationRun.objects.count()}")

# ============================================================
# 5. VULNERABILITY
# ============================================================
from vulnerability.models import Vulnerability, RiskAssessment

Vulnerability.objects.all().delete()
RiskAssessment.objects.all().delete()

vulns_data = [
    ('Unencrypted MODBUS Communication', 'SCADA',          'critical', 9.1, 'open',        'Implement TLS encryption on all MODBUS TCP connections. Use VPN for remote access.'),
    ('Default Credentials on HMI Panel', 'HMI',            'critical', 9.8, 'in_progress', 'Change all default passwords. Implement MFA. Review all access logs.'),
    ('Missing Firmware Updates',         'RTU Firmware',   'high',     7.5, 'open',        'Apply vendor-supplied firmware patches within next scheduled maintenance window.'),
    ('Weak Authentication Protocol',     'Auth System',    'high',     7.8, 'in_progress', 'Upgrade from MD5 to SHA-256 hashing. Implement session timeout policies.'),
    ('Exposed Control Network Port',     'Network',        'high',     8.2, 'open',        'Close port 23 (Telnet). Restrict port 502 to known IP addresses via ACL rules.'),
    ('No Network Segmentation',          'Network',        'medium',   6.5, 'open',        'Implement VLAN separation between IT and OT networks. Deploy DMZ architecture.'),
    ('Insufficient Audit Logging',       'SCADA Software', 'medium',   5.3, 'resolved',    'Enable comprehensive audit logging. Configure log retention for 90 days minimum.'),
    ('Outdated SSL Certificate',         'Web Interface',  'medium',   5.8, 'resolved',    'Renew SSL certificate. Implement automated certificate renewal process.'),
    ('Physical Access Control Weakness', 'Physical',       'low',      3.2, 'open',        'Install card-reader access control. Add CCTV monitoring at control room entrance.'),
    ('Backup Power Vulnerability',       'Infrastructure', 'low',      2.8, 'open',        'Test UPS monthly. Ensure backup generator can sustain 72-hour operation.'),
]

created_vulns = []
for title, component, severity, cvss, status, action in vulns_data:
    v = Vulnerability.objects.create(
        title=title,
        description=f'Vulnerability identified in the {component} component of the HVDC cyber-physical system.',
        component=component, severity=severity, cvss_score=cvss,
        status=status, discovered_by=admin_user, corrective_action=action,
        remediation_deadline=date.today() + timedelta(days=random.randint(7, 90))
    )
    created_vulns.append(v)

ra1 = RiskAssessment.objects.create(
    title='Q1 2026 HVDC System Risk Assessment',
    conducted_by=admin_user,
    overall_risk_score=7.8,
    findings=(
        'Critical findings in Q1 2026:\n'
        '1. Unencrypted MODBUS communication is highest risk vector\n'
        '2. Default HMI credentials remain unchanged\n'
        '3. No IT/OT network segmentation exists\n'
        '4. Firmware patches 6 months overdue\n'
        'Overall system risk: HIGH. Immediate remediation required.'
    ),
    recommendations=(
        '1. IMMEDIATE: Change all default credentials within 48 hours\n'
        '2. HIGH: Implement network segmentation within 2 weeks\n'
        '3. HIGH: Deploy TLS encryption on MODBUS within 1 month\n'
        '4. MEDIUM: Apply firmware patches at next maintenance window\n'
        '5. ONGOING: Monthly vulnerability scans, quarterly risk reviews'
    )
)
ra1.vulnerabilities.set(created_vulns[:6])

ra2 = RiskAssessment.objects.create(
    title='Post-Incident Security Review — Feb 2026',
    conducted_by=admin_user,
    overall_risk_score=6.2,
    findings=(
        'Post-incident assessment following DoS attack on Feb 12, 2026.\n'
        'System detected and mitigated attack within 450ms.\n'
        'AI model performed at 97.5% accuracy during incident.\n'
        'Network segmentation gaps exploited — lateral movement observed.'
    ),
    recommendations=(
        '1. Enhance IDS rules for MODBUS protocol anomalies\n'
        '2. Implement rate limiting on control network interfaces\n'
        '3. Update incident response playbooks\n'
        '4. Conduct tabletop exercise within 30 days'
    )
)
ra2.vulnerabilities.set(created_vulns[2:5])

print(f"Vulnerabilities: {Vulnerability.objects.count()} | Risk Assessments: {RiskAssessment.objects.count()}")

# ============================================================
# 6. DEFENSE & MITIGATION
# ============================================================
from defense.models import SecurityPolicy, MitigationAction

SecurityPolicy.objects.all().delete()
MitigationAction.objects.all().delete()

policies = [
    ('AES-256 Data Encryption',     'encryption',     True,  {'algorithm': 'AES-256-GCM', 'key_rotation_days': 90, 'scope': 'all_communications'}),
    ('Multi-Factor Authentication', 'authentication', True,  {'method': 'TOTP', 'backup_codes': True, 'session_timeout_min': 30}),
    ('MODBUS Protocol Firewall',    'firewall',       True,  {'allowed_ips': ['10.0.1.0/24', '192.168.1.0/24'], 'blocked_ports': [23, 21, 25]}),
    ('Anomaly-Based IDS',           'ids',            True,  {'sensitivity': 'high', 'baseline_window_hours': 24, 'alert_threshold': 0.85}),
    ('Automated Backup Policy',     'backup',         True,  {'frequency': 'daily', 'retention_days': 30, 'encryption': True}),
    ('Rate Limiting Policy',        'firewall',       False, {'max_packets_per_sec': 1000, 'burst_limit': 5000, 'action': 'drop'}),
    ('Certificate Pinning',         'authentication', True,  {'pin_expiry_days': 365, 'backup_pins': 2}),
    ('SCADA Protocol Whitelisting', 'ids',            True,  {'allowed_protocols': ['MODBUS', 'DNP3', 'IEC61850'], 'block_unknown': True}),
]

for name, ptype, enabled, config in policies:
    SecurityPolicy.objects.create(
        name=name,
        description=f'Security policy for {name.lower()} in HVDC cyber-physical system protection.',
        policy_type=ptype, is_enabled=enabled,
        created_by=admin_user, config_data=config
    )

mitigation_data = [
    ('block_suspicious_ip',      'AI Detector', 'executed', 'Blocked 3 IPs: 192.168.3.45, 192.168.3.46, 10.0.2.88. Firewall rules updated.'),
    ('enable_dos_protection',    'Admin',       'executed', 'DoS protection activated. Rate limiting: 1000 pkt/sec. Attack traffic dropped 96%.'),
    ('rotate_encryption_keys',   'System',      'executed', 'AES-256 keys rotated. New keys distributed to all nodes. Old keys invalidated.'),
    ('reset_firewall_rules',     'Admin',       'executed', 'Firewall rules reset to baseline. 12 new rules applied from security policy.'),
    ('isolate_compromised_node', 'AI Detector', 'executed', 'Node 192.168.1.44 isolated from control network. Traffic redirected through proxy.'),
    ('enable_dos_protection',    'Automated',   'executed', 'Automated response — DoS protection enabled within 450ms of detection.'),
    ('block_suspicious_ip',      'Admin',       'failed',   'Failed to update firewall rules — connection timeout to management interface.'),
    ('rotate_encryption_keys',   'Scheduled',   'executed', 'Scheduled key rotation complete. Certificate validity extended 90 days.'),
]

for action, triggered_by, status, result in mitigation_data:
    MitigationAction.objects.create(
        action_name=action,
        triggered_by=triggered_by,
        status=status,
        result=result,
        is_automated=(triggered_by == 'Automated'),
        executed_at=timezone.now() - timedelta(hours=random.randint(0, 120))
    )

print(f"Policies: {SecurityPolicy.objects.count()} | Mitigations: {MitigationAction.objects.count()}")

# ============================================================
# 7. REPORTS
# ============================================================
from reports.models import Report

Report.objects.all().delete()

reports_data = [
    ('Threat Analysis Report — March 2026',      'threat_summary', date(2026,3,1),  date(2026,3,3),  'Total 32 threats detected. 4 critical DoS attacks mitigated. AI model accuracy 97.5%.'),
    ('Q1 Vulnerability Assessment Report',        'vulnerability',  date(2026,1,1),  date(2026,3,31), '10 vulnerabilities identified. 2 resolved. 3 critical require immediate attention.'),
    ('Post-Incident Compliance Report',           'compliance',     date(2026,2,12), date(2026,2,13), 'DoS incident Feb 12 reviewed. Response time 450ms. All protocols correctly followed.'),
    ('Monthly Security Summary — February 2026', 'threat_summary', date(2026,2,1),  date(2026,2,28), '28 threats detected. 100% detection rate. 6 mitigation actions executed.'),
    ('Command Manipulation Incident Report',      'incident',       date(2026,2,20), date(2026,2,20), 'Firing angle manipulation detected and blocked. No physical impact. Root cause: exposed port 502.'),
]

for title, rtype, pfrom, pto, summary in reports_data:
    Report.objects.create(
        title=title, report_type=rtype,
        generated_by=admin_user,
        period_from=pfrom, period_to=pto,
        summary=summary
    )

print(f"Reports: {Report.objects.count()}")

# ============================================================
# FINAL SUMMARY
# ============================================================
from monitoring.models import HVDCReading, NetworkTraffic
from threat_detection.models import ThreatLog, AIModel
from alerts.models import Alert
from simulation.models import AttackScenario, SimulationRun
from vulnerability.models import Vulnerability, RiskAssessment
from defense.models import SecurityPolicy, MitigationAction
from reports.models import Report

print("\n" + "="*55)
print("    ALL SAMPLE DATA LOADED SUCCESSFULLY")
print("="*55)
print(f"  HVDC Readings       : {HVDCReading.objects.count()}")
print(f"  Network Traffic     : {NetworkTraffic.objects.count()}")
print(f"  Threat Logs         : {ThreatLog.objects.count()}")
print(f"  AI Models           : {AIModel.objects.count()}")
print(f"  Alerts              : {Alert.objects.count()} ({Alert.objects.filter(is_resolved=False).count()} active)")
print(f"  Attack Scenarios    : {AttackScenario.objects.count()}")
print(f"  Simulation Runs     : {SimulationRun.objects.count()}")
print(f"  Vulnerabilities     : {Vulnerability.objects.count()}")
print(f"  Risk Assessments    : {RiskAssessment.objects.count()}")
print(f"  Security Policies   : {SecurityPolicy.objects.count()}")
print(f"  Mitigation Actions  : {MitigationAction.objects.count()}")
print(f"  Reports             : {Report.objects.count()}")
print("="*55)
exit()
```

### Step 9 — Collect Static Files
```
python manage.py collectstatic --no-input
```

### Step 10 — Create Superuser (Admin)
```
python manage.py createsuperuser

Username: admin1
Email:    admin@hvdcsec.com
Password: Admin@1234
```

Then set the admin role:
```
python manage.py shell
```
```python
from accounts.models import CustomUser
u = CustomUser.objects.get(username='admin1')
u.role = 'admin'
u.save()
print("Admin role set:", u.is_admin())
exit()
```

### Step 11 — Run Development Server
```
python manage.py runserver
```

---

## Access URLs

| Page               | URL                                        |
|--------------------|--------------------------------------------|
| Login              | http://127.0.0.1:8000/accounts/login/      |
| Register           | http://127.0.0.1:8000/accounts/register/   |
| Dashboard          | http://127.0.0.1:8000/home/                |
| HVDC Monitoring    | http://127.0.0.1:8000/monitoring/          |
| Threat Detection   | http://127.0.0.1:8000/threat-detection/    |
| Reports            | http://127.0.0.1:8000/reports/             |
| Simulation         | http://127.0.0.1:8000/simulation/          |
| Alerts             | http://127.0.0.1:8000/alerts/              |
| Vulnerability      | http://127.0.0.1:8000/vulnerability/       |
| Defense            | http://127.0.0.1:8000/defense/             |
| Django Admin Panel | http://127.0.0.1:8000/admin/               |

---

## Login Credentials

### Admin
```
Username : admin1
Password : Admin@1234
```

### Test Analyst User
```
Username : analyst1
Password : Analyst@1234
```
> Register at /accounts/register/ then admin sets role to 'analyst' from Users page

### Test Viewer User
```
Username : viewer1
Password : Viewer@1234
```
> Register at /accounts/register/ (default role is viewer)

---

## User Roles

| Role     | Access                                                              |
|----------|---------------------------------------------------------------------|
| Admin    | Full access — user management, AI model control, all dashboards     |
| Analyst  | Monitoring, threats, reports, simulation, alerts, vulnerability     |
| Viewer   | View-only — dashboard, monitoring, alerts                           |

---

## Project Apps

| App              | Purpose                                               |
|------------------|-------------------------------------------------------|
| accounts         | Login, register, roles, profile management            |
| dashboard        | Admin & user dashboards (separate views per role)     |
| monitoring       | HVDC real-time parameters, network traffic            |
| threat_detection | AI-powered cyber attack detection, threat logs        |
| reports          | PDF & CSV report generation and download              |
| simulation       | Predefined attack scenario simulator                  |
| alerts           | Real-time alerts, notification preferences            |
| vulnerability    | Vulnerability register, risk assessments              |
| defense          | Security policies, mitigation actions                 |

---

## AI Model Details

| Property    | Value                                                          |
|-------------|----------------------------------------------------------------|
| Algorithm   | Random Forest Classifier (200 estimators)                      |
| Dataset     | 5,000 synthetic HVDC cyber-physical samples                    |
| Classes     | Normal, DoS, FDI, Command Manipulation, Replay Attack          |
| Features    | DC Voltage, DC Current, AC Voltages, Active Power,             |
|             | Reactive Power, Firing Angle, Extinction Angle,                |
|             | Network Packet Rate, Communication Latency                     |
| Accuracy    | ~97%+                                                          |
| Model Files | ml_models/hvdc_rf_model.pkl, ml_models/scaler.pkl              |

---

## Every Time You Start Development

```
cd D:\HVDC_Security_System
venv\Scripts\activate
python manage.py runserver
```
> Make sure MySQL service is running before starting the server.

---

## Troubleshooting

| Error                       | Fix                                           |
|-----------------------------|-----------------------------------------------|
| django.db.OperationalError  | Start MySQL service                           |
| ModuleNotFoundError         | pip install -r requirements.txt               |
| TemplateDoesNotExist        | Check template file exists in correct folder  |
| No module named 'accounts'  | Check INSTALLED_APPS in settings.py           |
| Table doesn't exist         | python manage.py migrate                      |
| Model file not found        | Run dataset generation and training scripts   |
| Dashboard showing empty     | Run sample data shell script (Step 8)         |
| Reports not showing         | Check reports/views.py uses all() not filter()|
| ImportError in admin.py     | Fix wrong model imports in that app's admin.py|
