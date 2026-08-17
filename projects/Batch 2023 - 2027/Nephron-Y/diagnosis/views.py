import csv
import json
from io import TextIOWrapper
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import PatientRecord, CartItem, CustomCurePlan
from django.core.mail import send_mail 

# === LOCAL ML LIBRARIES ===
import joblib
import numpy as np
# ==========================
from django.conf import settings
from twilio.rest import Client
# === MACHINE LEARNING MODEL LOADING ===
ML_MODEL_PATH = 'ckd_model.pkl' 
ML_REGRESSOR_PATH = 'ckd_regressor.pkl' 

try:
    ml_model = joblib.load(ML_MODEL_PATH)
    regressor_model = joblib.load(ML_REGRESSOR_PATH)
    print("✅ ML Models (Classifier and Regressor) loaded successfully.")
except FileNotFoundError:
    print(f"❌ ERROR: Model files not found. Ensure models are in the root directory.")
    ml_model = None
    regressor_model = None
# ======================================

# === DYNAMIC TEXT GENERATION ===

def generate_dynamic_report(patient_data, is_doctor=False, raw_prediction=0):
    """Generates contextually dynamic reports based on ML prediction and patient data."""
    sc = patient_data['sc']
    bp = patient_data['bp']
    al = patient_data['al']
    
    if raw_prediction == 1:
        risk_tag = "High Risk"
        severity = "Yes. Urgent medical review is strongly recommended."
        
        if not is_doctor:
            return f"""RISK LEVEL: High Risk\n\nANALYSIS: The analytical model detected strong indicators of CKD. Your key concern is elevated Creatinine (SC: {sc} mg/dL) and high Blood Pressure (BP: {bp} mmHg). These values significantly increase kidney workload.\n\nPRECAUTIONS: \n1. Maintain BP below 130/80 mmHg using diet/medication.\n2. Severely restrict sodium intake (<1500mg/day).\n3. Consult a physician immediately for confirmation tests.\n\nSEVERITY: {severity}"""
        else:
            return f"""1. DIAGNOSTIC ASSESSMENT: CKD Stage II/III indicated. High probability based on SC ({sc} mg/dL) and Albumin ({al}). Immediate clinical follow-up required.\n2. PHARMACOLOGICAL STRATEGY: Initiate ACE inhibitor (e.g., Lisinopril) or ARB to reduce proteinuria and manage BP ({bp} mmHg). Avoid NSAIDs.\n3. CLINICAL INTERVENTIONS: Refer to renal dietitian. Schedule repeat SC/BUN panel in 4 weeks.\n4. MONITORING PLAN: Target BP < 130/80 mmHg."""
    else:
        if not is_doctor:
            return f"""RISK LEVEL: Low Risk\n\nANALYSIS: The analytical model indicates a low probability of Chronic Kidney Disease. All current markers (SC: {sc} mg/dL, BP: {bp} mmHg) are within typical healthy ranges.\n\nPRECAUTIONS: \n1. Continue routine yearly checkups including eGFR.\n2. Maintain hydration.\n3. Control blood pressure to prevent future risk.\n\nSEVERITY: No. Continue routine care."""
        else:
            return f"""1. DIAGNOSTIC ASSESSMENT: CKD is not statistically indicated by ML model. Markers are within acceptable limits (SC: {sc} mg/dL).\n2. PHARMACOLOGICAL STRATEGY: No specific intervention needed. Encourage continuation of current regimen.\n3. CLINICAL INTERVENTIONS: Lifestyle counseling focusing on sustained blood pressure control.\n4. MONITORING PLAN: Routine annual follow-up is sufficient."""

# === ML FUNCTIONS ===

def predict_ckd_risk(data):
    if ml_model is None:
        if data.get('sc', 1.0) > 1.4 or data.get('al', 0) > 1 or data.get('bp', 80) > 90:
            return 1 
        return 0
    
    input_values = [
        data.get('age', 40), data.get('bp', 80), data.get('sg', 1.018), data.get('al', 0),
        data.get('su', 0), data.get('sc', 1.0), 14.0, 42, 1, 1, 
    ]
    input_array = np.array([input_values])
    return ml_model.predict(input_array)[0]

def generate_all_forecasts(records, steps=5):
    forecasts = {'sc': [], 'bp': [], 'egfr': [], 'sg': []}
    try:
        if not records: return forecasts
        latest_record = records.order_by('-created_at').first()
        if not latest_record: return forecasts
            
        curr_sc = float(latest_record.serum_creatinine)
        curr_bp = float(latest_record.blood_pressure)
        curr_egfr = float(latest_record.egfr) if latest_record.egfr else 90.0
        curr_sg = float(latest_record.specific_gravity) if latest_record.specific_gravity else 1.020
        
        is_high_risk = (latest_record.risk_level == "High Risk")
        
        for i in range(steps):
            if is_high_risk:
                curr_sc += curr_sc * np.random.uniform(0.25, 0.45)  
                curr_bp += np.random.uniform(5.0, 12.0)             
                curr_egfr -= curr_egfr * np.random.uniform(0.15, 0.25) 
                curr_sg = curr_sg - 0.004 if curr_sg > 1.010 else curr_sg + 0.004 
            else:
                curr_sc += np.random.uniform(-0.15, 0.15)
                curr_bp += np.random.uniform(-4.0, 5.0)
                curr_egfr += np.random.uniform(-2.0, 3.0)
                curr_sg += np.random.uniform(-0.002, 0.002)
                
            forecasts['sc'].append(round(max(0.6, curr_sc), 2))
            forecasts['bp'].append(round(max(70, curr_bp), 1))
            forecasts['egfr'].append(round(max(5.0, min(120.0, curr_egfr)), 1))
            forecasts['sg'].append(round(max(1.005, min(1.030, curr_sg)), 3))
        return forecasts
    except Exception as e:
        print(f"⚠️ FORECAST ERROR: {e}")
        return forecasts

def parse_patient_data(row, is_csv=False):
    def safe_int(val, default=0):
        try: return int(val)
        except (ValueError, TypeError): return default
    def safe_float(val, default=0.0):
        try: return float(val)
        except (ValueError, TypeError): return default
    
    bp_key = 'bp' if is_csv else 'blood_pressure'
    sg_key = 'sg' if is_csv else 'specific_gravity'
    sc_key = 'sc' if is_csv else 'serum_creatinine'
    
    data = {
        'name': row.get('name', 'Manual Entry'),
        'age': safe_int(row.get('age', 40)),
        'bp': safe_int(row.get(bp_key, 80)),
        'sg': safe_float(row.get(sg_key, 1.018)),
        'al': safe_int(row.get('albumin', '0')),
        'su': safe_int(row.get('sugar', '0')),
        'sc': safe_float(row.get(sc_key, 1.0)),
        'hemo': safe_float(row.get('hemoglobin', 14.0)), # <-- FIX: Now extracts Hemoglobin
        'egfr_str': row.get('egfr') or '0', 
        'prot': row.get('proteinuria', row.get('prot', 'Negative')),
    }
    data['egfr'] = safe_float(data['egfr_str']) if data['egfr_str'] else None
    return data

# === VIEWS ===

def landing(request):
    if request.user.is_authenticated:
        return redirect('choice') 
    return render(request, 'diagnosis/landing.html')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('choice') 
    else:
        form = UserCreationForm()
    return render(request, 'diagnosis/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('choice')
    else:
        form = AuthenticationForm()
    return render(request, 'diagnosis/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('landing')

@login_required(login_url='/login/')
def choice_view(request):
    return render(request, 'diagnosis/choice.html')

@login_required(login_url='/login/') 
def dashboard(request):
    # ONLY SHOW RECORDS BELONGING TO THE LOGGED IN USER
    recent_patients = PatientRecord.objects.filter(name=request.user.username).order_by('-created_at')[:10]

    # Calculate health score for the Liquid Kidney visual on the Patient side
    for p in recent_patients:
        if p.egfr: 
            p.health_score = min(int(p.egfr), 100)
        elif p.serum_creatinine:
            cr_val = float(p.serum_creatinine)
            estimated_health = 100 - ((cr_val - 1.0) * 25)
            p.health_score = max(0, min(100, int(estimated_health)))
        else: 
            p.health_score = 0

    if request.method == "POST":
        is_csv_upload = 'csv_file' in request.FILES
        data_source = request.FILES['csv_file'] if is_csv_upload else [request.POST]
        
        try:
            if is_csv_upload:
                file_data = TextIOWrapper(data_source.file, encoding='utf-8-sig')
                data_iterator = list(csv.DictReader(file_data)) # Load into memory
            else:
                data_iterator = data_source
            
            for row in data_iterator:
                patient_data = parse_patient_data(row, is_csv=is_csv_upload)
                
                # FORCE the name to be the logged-in user's name for security
                patient_data['name'] = request.user.username
                
                # FIX: Calculate eGFR dynamically if not provided in CSV
                sc = patient_data['sc']
                age = patient_data['age']
                if sc > 0 and age > 0:
                    calculated_egfr = 186 * (sc ** -1.154) * (age ** -0.203)
                else:
                    calculated_egfr = 0
                patient_data['egfr'] = calculated_egfr
                
                raw_prediction = predict_ckd_risk(patient_data) 
                risk_level = "High Risk" if raw_prediction == 1 else "Low Risk"
                full_report = generate_dynamic_report(patient_data, is_doctor=False, raw_prediction=raw_prediction)
                
                # --- AGENTIC ROUTING & SAVING ---
                if risk_level == "High Risk":
                    assigned_dept = "Nephrology Critical Care"
                    routing_stat = "URGENT: Routed to Specialist"
                    
                    try:
                        send_mail(
                            subject=f"URGENT TRIAGE ALERT: {patient_data['name']}",
                            message=f"Agentic Alert: Patient {patient_data['name']} has been flagged as HIGH RISK.\n\n"
                                    f"Key Vitals:\n"
                                    f"- Creatinine: {patient_data['sc']} mg/dL\n"
                                    f"- Blood Pressure: {patient_data['bp']} mmHg\n\n"
                                    f"Please log in to the Nephron-X portal immediately to review.",
                            from_email="triage@nephronx.com", 
                            recipient_list=["mohammedassiddiqui@gmail.com"], 
                            fail_silently=False,
                        )
                        print("✅ High Risk Email sent to mohammedassiddiqui@gmail.com")
                    except Exception as email_err:
                        print(f"⚠️ Email Agent failed: {email_err}")
                else:
                    assigned_dept = "General Practice"
                    routing_stat = "Routine Monitoring"

                # FIX: Added hemoglobin to the database commit!
                PatientRecord.objects.create(
                    name=patient_data['name'], 
                    age=patient_data['age'], 
                    blood_pressure=patient_data['bp'], 
                    specific_gravity=patient_data['sg'],
                    albumin=patient_data['al'], 
                    sugar=patient_data['su'], 
                    serum_creatinine=patient_data['sc'], 
                    hemoglobin=patient_data['hemo'], # <--- This prevents the crash!
                    egfr=patient_data['egfr'], 
                    
                    prediction_result=full_report, 
                    risk_level=risk_level,
                    assigned_department=assigned_dept,
                    routing_status=routing_stat
                )
                
            return redirect('dashboard')
        
        except Exception as e:
            print(f"❌ CRITICAL ERROR PROCESSING CSV: {e}")
            return redirect('dashboard')

    return render(request, 'diagnosis/home.html', {'recent_patients': recent_patients})

@login_required(login_url='/login/')
def doctor_view(request):
    """
    Main Clinical Dashboard: Handles manual entry, CSV uploads, 
    AI diagnostics, and Agentic Routing.
    """
    custom_plans = CustomCurePlan.objects.all().order_by('created_at')
    
    # AGENTIC SILO: Pull the latest 15 patients routed to this specific department
    recent_patients = PatientRecord.objects.filter(
        assigned_department="Nephrology Critical Care"
    ).order_by('-created_at')[:15]
    
    # Logic to calculate health_score for the "Liquid Kidney" UI element
    for p in recent_patients:
        if p.egfr: 
            p.health_score = min(int(p.egfr), 100)
        elif p.serum_creatinine:
            # Fallback calculation if eGFR wasn't stored
            cr_val = float(p.serum_creatinine)
            estimated_health = 100 - ((cr_val - 1.0) * 25)
            p.health_score = max(0, min(100, int(estimated_health)))
        else: 
            p.health_score = 0

    if request.method == "POST":
        is_csv_upload = 'csv_file' in request.FILES
        
        try:
            if is_csv_upload:
                data_source = request.FILES['csv_file']
                file_data = TextIOWrapper(data_source.file, encoding='utf-8')
                data_iterator = csv.DictReader(file_data)
            else:
                # Wrap the single form POST in a list to use the same loop
                data_iterator = [request.POST]
            
            for row in data_iterator:
                # 1. DATA EXTRACTION (Mapping UI fields to Logic)
                # Use .get() with defaults to prevent KeyErrors
                name = row.get('name')
                age = int(row.get('age', 0))
                bp = float(row.get('blood_pressure', 0))
                sc = float(row.get('serum_creatinine', 0))
                
                # New Advanced Markers
                sugar = float(row.get('sugar', 0))
                albumin = float(row.get('albumin', 0))
                hemoglobin = float(row.get('hemoglobin', 0))
                sg = float(row.get('specific_gravity', 1.020))
                
                # 2. MEDICAL LOGIC: Calculate eGFR (CKD-EPI Simplified)
                # Formula: 186 * (SC^-1.154) * (Age^-0.203)
                if sc > 0 and age > 0:
                    calculated_egfr = 186 * (sc ** -1.154) * (age ** -0.203)
                else:
                    calculated_egfr = 0

                # 3. AI PREDICTION & REPORTING
                # Prepare data for your ML model/utility functions
                patient_payload = {
                    'name': name, 'age': age, 'bp': bp, 'sc': sc,
                    'su': sugar, 'al': albumin, 'hemo': hemoglobin, 
                    'sg': sg, 'egfr': calculated_egfr
                }
                
                # Replace with your actual ML prediction logic
                # raw_prediction = predict_ckd_risk(patient_payload) 
                # For demo: High Risk if eGFR < 60 or Albumin is high
                is_high_risk = calculated_egfr < 60 or albumin > 30
                risk_level = "High Risk" if is_high_risk else "Low Risk"
                
                # Generate the text-based strategy
                # cure_plan = generate_dynamic_report(patient_payload, is_doctor=True)
                cure_plan = f"Clinical Strategy for {name}: Monitor eGFR ({calculated_egfr:.1f})."

                # 4. AGENTIC ROUTING
                if risk_level == "High Risk":
                    assigned_dept = "Nephrology Critical Care"
                    routing_stat = "URGENT: Routed to Specialist"
                    
                    # Agentic Alert: Automatic Email Dispatch
                    send_mail(
                        subject=f"URGENT TRIAGE ALERT: {name}",
                        message=f"Agentic Alert: Patient {name} flagged as HIGH RISK.\n\n"
                                f"Key Vitals:\n- eGFR: {calculated_egfr:.1f}\n"
                                f"- Creatinine: {sc}\n- BP: {bp}\n\n"
                                f"Review immediately in Nephron-X Portal.",
                        from_email="triage-agent@nephronx.com",
                        recipient_list=["mohammedassiddiqui@gmail.com"],
                        fail_silently=True,
                    )
                else:
                    assigned_dept = "General Practice"
                    routing_stat = "Routine Monitoring"

                # 5. DATABASE COMMIT
                PatientRecord.objects.create(
                    name=name, 
                    age=age, 
                    blood_pressure=bp, 
                    serum_creatinine=sc,
                    sugar=sugar,
                    albumin=albumin,
                    hemoglobin=hemoglobin,
                    specific_gravity=sg,
                    egfr=calculated_egfr,
                    prediction_result=cure_plan, 
                    risk_level=risk_level,
                    assigned_department=assigned_dept,
                    routing_status=routing_stat
                )
            
            return redirect('doctor_dashboard')
        
        except Exception as e:
            print(f"❌ ERROR PROCESSING DATA: {e}")
            # You might want to add a django message here to alert the user
            return redirect('doctor_dashboard')

    return render(request, 'diagnosis/doctor_dashboard.html', {
        'recent_patients': recent_patients,
        'custom_plans': custom_plans
    })

# ANALYTICS VIEW
@login_required(login_url='/login/')
def analytics_view(request):
    # CHINESE WALL: Doctors see everyone, Patients see only themselves
    if request.user.groups.filter(name='Doctors').exists() or request.user.is_staff:
        records = PatientRecord.objects.all().order_by('created_at')
    else:
        records = PatientRecord.objects.filter(name=request.user.username).order_by('created_at')

    # Use the filtered records for forecasting
    forecast_records = records.order_by('-created_at')
    forecasts = generate_all_forecasts(forecast_records)
    forecast_dates = [f'Forecast T+{i+1}' for i in range(5)]

    historical_dates = [r.created_at.strftime('%Y-%m-%d') for r in records]
    historical_bp = [r.blood_pressure for r in records]
    historical_sc = [float(r.serum_creatinine) for r in records]
    historical_sg = [float(r.specific_gravity) for r in records]
    historical_egfr = [float(r.egfr) if r.egfr else 0 for r in records]
    
    context = {
        'dates': json.dumps(historical_dates),
        'bp_data': json.dumps(historical_bp),
        'sc_data': json.dumps(historical_sc),
        'sg_data': json.dumps(historical_sg),
        'egfr_data': json.dumps(historical_egfr),
        'bp_forecast': json.dumps(forecasts['bp']),
        'sc_forecast': json.dumps(forecasts['sc']),
        'egfr_forecast': json.dumps(forecasts['egfr']),
        'sg_forecast': json.dumps(forecasts['sg']),
        'forecast_dates': json.dumps(forecast_dates),
        'historical_dates_and_forecast_dates': json.dumps(historical_dates + forecast_dates),
    }
    return render(request, 'diagnosis/analytics.html', context)

# MEDICAL SHOP VIEW
@login_required(login_url='/login/')
def shop_view(request):
    cart_count = CartItem.objects.filter(user=request.user).count()
    products = [
        {"name": "PhosLo (Calcium Acetate)", "strength": "667mg", "price": 15.99, "image": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=500&q=60", "desc": "Phosphate binder for high blood phosphorus levels."},
        {"name": "Renvela (Sevelamer)", "strength": "800mg", "price": 24.50, "image": "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?auto=format&fit=crop&w=500&q=60", "desc": "Controls serum phosphorus in patients with CKD."},
        {"name": "Ketosteril", "strength": "600mg", "price": 45.00, "image": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?auto=format&fit=crop&w=500&q=60", "desc": "Amino acid therapy to delay dialysis initiation."},
        {"name": "Lasix (Furosemide)", "strength": "40mg", "price": 5.99, "image": "https://images.unsplash.com/photo-1585435557343-3b092031a831?auto=format&fit=crop&w=500&q=60", "desc": "Diuretic to reduce fluid retention (edema)."},
        {"name": "EPO Injection", "strength": "4000 IU", "price": 120.00, "image": "https://images.unsplash.com/photo-1583947215259-38e31be8751f?auto=format&fit=crop&w=500&q=60", "desc": "Treats anemia associated with kidney disease."},
    ]
    return render(request, 'diagnosis/shop.html', {'products': products, 'cart_count': cart_count})

@login_required(login_url='/login/')
def add_to_cart(request):
    if request.method == "POST":
        name = request.POST.get('name')
        price = request.POST.get('price')
        image = request.POST.get('image')
        existing_item = CartItem.objects.filter(user=request.user, product_name=name).first()
        if existing_item:
            existing_item.quantity += 1
            existing_item.save()
        else:
            CartItem.objects.create(user=request.user, product_name=name, price=price, image_url=image, quantity=1)
        return redirect('shop')
    return redirect('shop')

@login_required(login_url='/login/')
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart_items)
    return render(request, 'diagnosis/cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required(login_url='/login/')
def remove_cart_item(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id, user=request.user)
        cart_item.delete()
    except CartItem.DoesNotExist:
        pass
    return redirect('cart')

@login_required(login_url='/login/')
def delete_record(request, record_id):
    record = get_object_or_404(PatientRecord, id=record_id)
    record.delete()
    previous_url = request.META.get('HTTP_REFERER', 'dashboard')
    return redirect(previous_url)

@login_required(login_url='/login/')
def delete_patient(request, record_id):
    """Simple archive function to remove records from the queue."""
    patient = get_object_or_404(PatientRecord, id=record_id)
    patient.delete()
    return redirect('doctor_dashboard')

def submit_feedback(request, record_id):
    if request.method == "POST":
        patient = PatientRecord.objects.get(id=record_id)
        action = request.POST.get('feedback_action')
        
        if action == "Approved Option 1":
            # Keep the original AI text
            patient.doctor_feedback = "Approved"
            patient.save()

        elif action == "Approved Option 2":
            # Replace AI text with the Option 2 Protocol text
            option2_text = "Dialysis optimization, sodium restriction (<2g/day), and immediate nephrologist consultation. Monitor SC/eGFR levels daily."
            patient.prediction_result = option2_text
            patient.doctor_feedback = "Approved"
            patient.save()

        elif action == "Approved Knowledge Base":
            # Pull the text from the hidden inputs we added in the HTML
            manual_text = request.POST.get('manual_text')
            plan_name = request.POST.get('custom_plan_name')
            patient.prediction_result = f"KNOWLEDGE BASE ({plan_name}):\n{manual_text}"
            patient.doctor_feedback = "Approved"
            patient.save()
            
        elif action == "Manual":
            # Save new protocol to DB and update the current patient
            plan_name = request.POST.get('custom_plan_name')
            plan_content = request.POST.get('manual_text')
            
            # Save to global memory
            CustomCurePlan.objects.create(
                plan_name=plan_name,
                plan_content=plan_content
            )
            
            # Update current patient
            patient.prediction_result = f"MANUAL INTERVENTION ({plan_name}):\n{plan_content}"
            patient.doctor_feedback = "Approved"
            patient.save()

        return redirect('doctor_dashboard')
    


# ==========================================
# EMERGENCY SOS SYSTEM
# ==========================================
@login_required(login_url='/login/')
def emergency_sos(request):
    try:
        # Securely grab credentials from settings.py
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Make the phone ring!
        call = client.calls.create(
            # This is what the robot voice will say when you answer:
            twiml='<Response><Say voice="alice" language="en-US">Critical Alert. A patient has just triggered the Emergency S O S button in the Nephron X portal. Please check the clinical dashboard immediately.</Say></Response>',
            to='+919959364017',  # <--- MUST BE YOUR VERIFIED CELL PHONE NUMBER!
            from_=settings.TWILIO_PHONE_NUMBER
        )
        print(f"🚨 SOS Call Initiated! Call SID: {call.sid}")
        
    except Exception as e:
        print(f"❌ SOS Call Failed: {e}")
        
    # Send the patient back to their dashboard after clicking
    return redirect('dashboard')