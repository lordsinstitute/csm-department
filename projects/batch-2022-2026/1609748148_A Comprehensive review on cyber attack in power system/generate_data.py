import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'npp_core.settings')
django.setup()

from authentication.models import CustomUser
from threats.models import PlantAsset, ThreatCategory, Threat, Vulnerability
from risk_assessment.models import TAMAssessment
from security_controls.models import SecurityControl

print("Creating users...")
if not CustomUser.objects.filter(username='analyst').exists():
    CustomUser.objects.create_user(
        username='analyst', email='analyst@npp.gov', password='Analyst@1234',
        first_name='Sarah', last_name='Connor', role='analyst', department='Cyber Security'
    )
    print("  analyst created")
else:
    print("  analyst already exists, skipping")

if not CustomUser.objects.filter(username='operator').exists():
    CustomUser.objects.create_user(
        username='operator', email='operator@npp.gov', password='Operator@1234',
        first_name='John', last_name='Smith', role='operator', department='Operations'
    )
    print("  operator created")
else:
    print("  operator already exists, skipping")

# Make sure your superuser has admin role
for su in CustomUser.objects.filter(is_superuser=True):
    su.role = 'admin'
    su.save()
    print(f"  {su.username} role set to admin")

print("\nCreating assets...")
if PlantAsset.objects.count() == 0:
    assets_data = [
        ('Reactor Control System', 'dcs', 'Reactor Building Level 1', 'critical', '192.168.10.1'),
        ('SCADA Main Server', 'scada', 'Control Room', 'critical', '192.168.10.2'),
        ('Emergency Shutdown PLC', 'plc', 'Safety Room A', 'critical', '192.168.10.3'),
        ('Plant Network Core Switch', 'network', 'Server Room B', 'high', '192.168.10.4'),
        ('Operator Workstation 1', 'workstation', 'Control Room', 'medium', '192.168.10.10'),
        ('Operator Workstation 2', 'workstation', 'Control Room', 'medium', '192.168.10.11'),
        ('Safety Instrumentation System', 'safety', 'Safety Building', 'critical', '192.168.10.5'),
        ('Historian Server', 'server', 'Server Room A', 'high', '192.168.10.6'),
        ('Engineering Workstation', 'workstation', 'Engineering Office', 'high', '192.168.10.12'),
        ('Turbine Control System', 'dcs', 'Turbine Hall', 'high', '192.168.10.7'),
    ]
    assets = []
    for name, atype, location, criticality, ip in assets_data:
        a = PlantAsset.objects.create(name=name, asset_type=atype, location=location,
                                       criticality=criticality, ip_address=ip,
                                       description=f'{name} at {location}')
        assets.append(a)
    print(f"  {len(assets)} assets created")
else:
    assets = list(PlantAsset.objects.all())
    print(f"  assets already exist, skipping ({len(assets)} found)")

print("\nCreating threat categories...")
if ThreatCategory.objects.count() == 0:
    cats = {}
    for cat_name in ['Malware', 'Insider Threat', 'Network Intrusion', 'Physical Access', 'Social Engineering', 'Supply Chain']:
        cats[cat_name] = ThreatCategory.objects.create(name=cat_name, description=f'{cat_name} attack vectors')
    print(f"  {len(cats)} categories created")
else:
    cats = {c.name: c for c in ThreatCategory.objects.all()}
    print(f"  categories already exist, skipping")

print("\nCreating threats...")
if Threat.objects.count() == 0:
    threats_data = [
        ('Stuxnet-Style PLC Attack', 'Malware', 'critical', 'active', 'Network propagation', 'Could disrupt reactor control', 8.5, 9.0),
        ('Ransomware on SCADA Server', 'Malware', 'critical', 'active', 'Email phishing', 'Complete loss of SCADA visibility', 7.0, 9.5),
        ('Insider Data Exfiltration', 'Insider Threat', 'high', 'monitoring', 'Privileged access abuse', 'Sensitive control logic theft', 6.0, 8.0),
        ('Remote Access Exploitation', 'Network Intrusion', 'high', 'active', 'VPN vulnerability', 'Unauthorized control system access', 7.5, 8.5),
        ('Spear Phishing - Engineers', 'Social Engineering', 'medium', 'monitoring', 'Targeted email', 'Credential compromise', 6.5, 6.0),
        ('Unauthorized USB Device', 'Physical Access', 'medium', 'resolved', 'Physical access', 'Malware introduction', 5.0, 6.5),
        ('Supply Chain Software Tamper', 'Supply Chain', 'critical', 'monitoring', 'Vendor update', 'Backdoor in control software', 5.5, 9.5),
        ('DCS Firmware Manipulation', 'Malware', 'critical', 'active', 'Remote exploitation', 'Physical equipment damage', 6.0, 10.0),
        ('Network Scanning Activity', 'Network Intrusion', 'low', 'resolved', 'Automated scanner', 'Asset enumeration', 4.0, 3.0),
        ('Historian Server Breach', 'Network Intrusion', 'high', 'mitigated', 'SQL injection', 'Historical data theft', 5.5, 7.0),
    ]
    for title, cat, sev, status, vector, impact, likelihood, impact_score in threats_data:
        t = Threat.objects.create(
            title=title, category=cats[cat], severity=sev, status=status,
            attack_vector=vector, potential_impact=impact,
            description=f'Detailed analysis of {title} threat to NPP systems.',
            likelihood_score=likelihood, impact_score=impact_score
        )
        t.affected_assets.add(assets[0], assets[1])
    print(f"  {len(threats_data)} threats created")
else:
    print(f"  threats already exist, skipping")

print("\nCreating vulnerabilities...")
if Vulnerability.objects.count() == 0:
    vulns_data = [
        (assets[0], 'Unpatched Windows Embedded', 'CVE-2021-34527', 'critical', 9.8, False),
        (assets[1], 'Default SCADA Credentials', 'CVE-2020-12076', 'critical', 9.1, False),
        (assets[2], 'PLC Firmware v2.1 Buffer Overflow', 'CVE-2019-13945', 'high', 8.6, False),
        (assets[3], 'Cisco IOS Vulnerability', 'CVE-2022-20968', 'high', 7.4, True),
        (assets[4], 'Remote Desktop Exposure', 'CVE-2019-0708', 'critical', 9.8, False),
        (assets[5], 'Outdated Antivirus Definitions', '', 'medium', 5.5, True),
        (assets[6], 'Safety System Hardcoded Password', 'CVE-2021-27430', 'critical', 9.0, False),
        (assets[7], 'SQL Server Misconfiguration', 'CVE-2020-0618', 'high', 8.0, True),
        (assets[2], 'Unencrypted Protocol Usage', 'CVE-2018-10952', 'medium', 6.5, False),
        (assets[0], 'Weak TLS Configuration', 'CVE-2021-3449', 'medium', 5.9, True),
    ]
    for asset, title, cve, sev, cvss, patched in vulns_data:
        Vulnerability.objects.create(asset=asset, title=title, cve_id=cve,
                                      severity=sev, cvss_score=cvss, is_patched=patched,
                                      description=f'Vulnerability found in {asset.name}')
    print(f"  {len(vulns_data)} vulnerabilities created")
else:
    print(f"  vulnerabilities already exist, skipping")

print("\nCreating TAM assessments...")
if TAMAssessment.objects.count() == 0:
    assessments_data = [
        (assets[0], 9.5, 9.8, 9.9, 8.5, 9.0, 3.0),
        (assets[1], 8.0, 8.5, 9.0, 7.0, 8.0, 4.0),
        (assets[2], 9.0, 9.5, 9.8, 6.0, 7.5, 5.0),
        (assets[6], 9.8, 9.9, 10.0, 5.5, 6.0, 6.0),
        (assets[9], 7.0, 7.5, 8.0, 5.0, 6.5, 4.5),
    ]
    for asset, conf, integ, avail, likelihood, vuln, ctrl_eff in assessments_data:
        a = TAMAssessment(
            title=f'TAM Assessment - {asset.name}',
            asset=asset, status='completed',
            confidentiality_score=conf, integrity_score=integ, availability_score=avail,
            threat_likelihood=likelihood, vulnerability_factor=vuln,
            control_effectiveness=ctrl_eff, assessed_by='admin'
        )
        a.calculate_risk()
        a.save()
    print(f"  {len(assessments_data)} assessments created")
else:
    print(f"  assessments already exist, skipping")

print("\nCreating security controls...")
if SecurityControl.objects.count() == 0:
    controls_data = [
        ('NEI-13-10-1.1', 'Access Control Policy', 'preventive', 'implemented', 8.5),
        ('NEI-13-10-1.2', 'Account Management', 'preventive', 'implemented', 7.5),
        ('NEI-13-10-2.1', 'Audit and Accountability', 'detective', 'implemented', 8.0),
        ('NEI-13-10-2.2', 'Audit Log Review', 'detective', 'partial', 6.0),
        ('NEI-13-10-3.1', 'Configuration Management', 'preventive', 'implemented', 7.0),
        ('NEI-13-10-3.2', 'Change Control', 'preventive', 'partial', 6.5),
        ('NEI-13-10-4.1', 'Incident Response', 'corrective', 'implemented', 8.0),
        ('NEI-13-10-4.2', 'Incident Reporting', 'corrective', 'implemented', 7.5),
        ('NEI-13-10-5.1', 'Network Protection', 'preventive', 'implemented', 9.0),
        ('NEI-13-10-5.2', 'Intrusion Detection', 'detective', 'partial', 6.5),
        ('NEI-13-10-6.1', 'Media Protection', 'preventive', 'implemented', 7.0),
        ('NEI-13-10-6.2', 'Physical Access Control', 'preventive', 'implemented', 8.5),
        ('NEI-13-10-7.1', 'Personnel Security', 'preventive', 'implemented', 7.5),
        ('NEI-13-10-7.2', 'Security Awareness Training', 'preventive', 'partial', 6.0),
        ('NEI-13-10-8.1', 'System Protection', 'preventive', 'not_implemented', 0.0),
    ]
    for nei_id, title, ctype, status, eff in controls_data:
        SecurityControl.objects.create(
            nei_control_id=nei_id, title=title, control_type=ctype,
            status=status, effectiveness_score=eff,
            description=f'{title} control per NEI 13-10.',
            implementation_guidance=f'Implementation guidance for {title} per NEI 13-10.'
        )
    print(f"  {len(controls_data)} controls created")
else:
    print(f"  security controls already exist, skipping")

print("\n✅ Done!")
print("=" * 40)
print("Login credentials:")
print("  Your superuser (admin role): admin1 / your password")
print("  Analyst:  analyst / Analyst@1234")
print("  Operator: operator / Operator@1234")