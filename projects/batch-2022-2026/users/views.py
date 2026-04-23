from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from users.forms import UserRegistrationForm
from .models import UserRegistrationModel

import os
import re
import pandas as pd
import requests
import json

# ---- Grok API ----
GROK_API_KEY = getattr(settings, "GROK_API_KEY", None) or os.getenv("GROK_API_KEY") or "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"
GROK_API_URL = "https://api.x.ai/v1/chat/completions"



def base(request):
    return render(request, 'base.html')


def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'You have been successfully registered')
            return render(request, 'UserRegistration.html')  
        else:
            messages.error(request, 'Email or Mobile Already Exists')
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistration.html', {'form': form})



def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('password')
        try:
            user = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            if user.status == "activated":
                request.session['id'] = user.id
                request.session['loggeduser'] = user.name
                return redirect('UserHome')
            else:
                messages.error(request, '⚠️ Your account is not activated.')
        except UserRegistrationModel.DoesNotExist:
            messages.error(request, '❌ Invalid Login ID or Password')
    return render(request, 'UserLogin.html')


def UserHome(request):
    return render(request, 'users/UserHome.html')



def predict_anomaly(request):
    """
    Accepts cloud security metrics and detects anomalies using rule-based logic + Grok AI
    """
    anomaly_status = threat_category = severity_level = confidence_score = explanation = raw_response = None

    if request.method == 'POST':
        api_calls = request.POST.get('api_calls', '').strip()
        error_rate = request.POST.get('error_rate', '').strip()
        cpu_usage = request.POST.get('cpu_usage', '').strip()
        packet_size = request.POST.get('packet_size', '').strip()
        flow_duration = request.POST.get('flow_duration', '').strip()
        login_frequency = request.POST.get('login_frequency', '').strip()
        access_pattern = request.POST.get('access_pattern', '').strip()

        if not (api_calls and error_rate and cpu_usage and packet_size and flow_duration and login_frequency):
            messages.error(request, "⚠️ Please fill in all required fields.")
        else:
            try:
                # Convert to numbers for analysis
                api_calls_num = float(api_calls)
                error_rate_num = float(error_rate)
                cpu_usage_num = float(cpu_usage)
                packet_size_num = float(packet_size)
                flow_duration_num = float(flow_duration)
                login_frequency_num = float(login_frequency)

                # Rule-based threat detection (fallback if API fails)
                def detect_threat_locally():
                    threats = []
                    severity = "Low"
                    confidence = 0

                    # DDoS Detection
                    if api_calls_num > 500 and error_rate_num > 3:
                        threats.append("DDoS Attack")
                        severity = "Critical" if api_calls_num > 700 else "High"
                        confidence = min(95, 70 + (api_calls_num - 500) / 10)

                    # Data Exfiltration Detection
                    elif packet_size_num > 1000 and cpu_usage_num > 55:
                        threats.append("Data Exfiltration")
                        severity = "High" if packet_size_num > 1200 else "Medium"
                        confidence = min(92, 65 + (packet_size_num - 1000) / 20)

                    # Brute Force Detection
                    elif login_frequency_num > 10 and error_rate_num > 2:
                        threats.append("Brute Force Attack")
                        severity = "High" if login_frequency_num > 12 else "Medium"
                        confidence = min(90, 60 + login_frequency_num * 2)

                    # Unauthorized Access Detection
                    elif cpu_usage_num > 70 and flow_duration_num < 1.0:
                        threats.append("Unauthorized Access")
                        severity = "Medium"
                        confidence = 75

                    # Normal Activity
                    else:
                        threats.append("Normal Activity")
                        severity = "Low"
                        confidence = 98

                    return threats[0], severity, confidence

                # Try Grok API first
                try:
                    prompt = f"""You are an expert in real-time cloud security and anomaly detection.

Analyze the cloud environment metrics below and provide a structured security assessment in EXACTLY this format:

Anomaly Status: <Normal or Threat Detected>
Threat Category: <DDoS Attack, Data Exfiltration, Brute Force, Unauthorized Access, Zero-Day Exploit, or Normal Activity>
Severity Level: <Low, Medium, High, Critical>
Confidence: <number>%
Analysis: <3-4 detailed lines explaining the security assessment, potential threats, and recommended actions>

Cloud Security Metrics:
- API Calls per Minute: {api_calls}
- Error Rate: {error_rate}%
- CPU Usage: {cpu_usage}%
- Packet Size: {packet_size} bytes
- Flow Duration: {flow_duration} seconds
- Login Frequency: {login_frequency} per day
- Access Pattern Notes: {access_pattern}

Analyze for potential security threats including DDoS attacks, data exfiltration, brute force attempts, and unauthorized access patterns."""

                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {GROK_API_KEY}"
                    }

                    payload = {
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are Grok, an AI assistant specialized in cloud security and threat detection."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "model": "grok-beta",
                        "stream": False,
                        "temperature": 0
                    }

                    response = requests.post(GROK_API_URL, headers=headers, json=payload, timeout=30)

                    if response.status_code == 200:
                        result = response.json()
                        raw_response = result['choices'][0]['message']['content'].strip()

                        # Extract structured data
                        status_match = re.search(r"Anomaly Status\s*:\s*(.*)", raw_response, re.IGNORECASE)
                        category_match = re.search(r"Threat Category\s*:\s*(.*)", raw_response, re.IGNORECASE)
                        severity_match = re.search(r"Severity Level\s*:\s*(.*)", raw_response, re.IGNORECASE)
                        conf_match = re.search(r"Confidence\s*:\s*([0-9]{1,3})\s*%", raw_response, re.IGNORECASE)
                        analysis_match = re.search(r"Analysis\s*:\s*(.*)", raw_response, re.IGNORECASE | re.DOTALL)

                        anomaly_status = (status_match.group(1).strip() if status_match else "Threat Detected")
                        threat_category = (category_match.group(1).strip() if category_match else "Unknown")
                        severity_level = (severity_match.group(1).strip() if severity_match else "Medium")
                        confidence_score = (conf_match.group(1).strip() + "%" if conf_match else "85%")
                        explanation = (analysis_match.group(1).strip() if analysis_match else raw_response)
                    else:
                        raise Exception("API returned non-200 status")

                except Exception as api_error:
                    # Fallback to rule-based detection
                    threat_cat, sev_level, conf = detect_threat_locally()

                    threat_category = threat_cat
                    severity_level = sev_level
                    confidence_score = f"{int(conf)}%"

                    if threat_category == "Normal Activity":
                        anomaly_status = "Normal"
                        explanation = f"All metrics are within normal ranges. API calls: {api_calls}/min (normal: 100-200), Error rate: {error_rate}% (normal: <1%), CPU usage: {cpu_usage}% (normal: 30-50%). No security threats detected. System is operating normally."
                    else:
                        anomaly_status = "Threat Detected"

                        if threat_category == "DDoS Attack":
                            explanation = f"CRITICAL ALERT: Detected potential DDoS attack. API calls spiked to {api_calls}/min (normal: 100-200) with error rate at {error_rate}% (normal: <1%). This indicates a distributed denial-of-service attack attempting to overwhelm your infrastructure. RECOMMENDED ACTIONS: Enable rate limiting, activate DDoS protection, block suspicious IPs, scale infrastructure resources."

                        elif threat_category == "Data Exfiltration":
                            explanation = f"HIGH ALERT: Suspicious data exfiltration detected. Packet size increased to {packet_size} bytes (normal: 400-600) with CPU usage at {cpu_usage}% (normal: 30-50%). This pattern suggests unauthorized data transfer. RECOMMENDED ACTIONS: Review outbound traffic, check for unauthorized access, audit data access logs, implement data loss prevention (DLP) policies."

                        elif threat_category == "Brute Force Attack":
                            explanation = f"HIGH ALERT: Brute force attack detected. Login frequency at {login_frequency}/day (normal: 3-6) with elevated error rate {error_rate}%. Multiple failed authentication attempts indicate credential stuffing or password guessing attack. RECOMMENDED ACTIONS: Enable account lockout policies, implement CAPTCHA, enable multi-factor authentication (MFA), monitor failed login attempts."

                        elif threat_category == "Unauthorized Access":
                            explanation = f"MEDIUM ALERT: Potential unauthorized access detected. CPU usage at {cpu_usage}% with short flow duration {flow_duration}s suggests suspicious activity. RECOMMENDED ACTIONS: Review access logs, verify user permissions, check for privilege escalation, audit recent system changes."

                    raw_response = f"Rule-Based Detection (Grok API unavailable)\n\nMetrics Analysis:\n- API Calls: {api_calls}/min\n- Error Rate: {error_rate}%\n- CPU Usage: {cpu_usage}%\n- Packet Size: {packet_size} bytes\n- Flow Duration: {flow_duration}s\n- Login Frequency: {login_frequency}/day\n\nDetection Result: {threat_category}\nSeverity: {severity_level}\nConfidence: {confidence_score}"

                    messages.info(request, "Using rule-based detection (Grok API unavailable)")

            except ValueError as e:
                messages.error(request, "Invalid input values. Please enter valid numbers.")
                explanation = "Invalid input data provided."
            except Exception as e:
                raw_response = f"Error: {str(e)}"
                explanation = "Could not process security analysis."
                messages.error(request, f"Error: {str(e)}")

    return render(request, 'users/generate.html', {
        'anomaly_status': anomaly_status,
        'threat_category': threat_category,
        'severity_level': severity_level,
        'confidence_score': confidence_score,
        'explanation': explanation,
        'raw_response': raw_response
    })
