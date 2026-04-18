# HAIS Project - Setup and Run Guide (No Shell Dependencies)

This guide works on **Windows, Mac, and Linux** without requiring shell commands.

---

## 🚀 Quick Start (Windows/Mac/Linux)

### 1. Install Dependencies
```
Open Command Prompt/Terminal and run:
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 2. Set Up Database
```
python manage.py migrate
python manage.py createsuperuser
```

### 3. Start the Development Server
```
python manage.py runserver 8000
```

Then open: **http://127.0.0.1:8000**

---

## 📊 Dashboard & Data Management (Pure Python - No Shell)

### Check Trust Data
```
python check_trust_data.py
```
This shows all trust metrics and ethical alignments by user.

### Create Test Interaction Data
```
python test_interaction.py
```
This creates sample trust metrics for testing the dashboard.

### Clean/Reset Data
```
python manage.py shell
>>> from trust_ethics.models import TrustMetric, EthicalAlignment
>>> TrustMetric.objects.all().delete()
>>> EthicalAlignment.objects.all().delete()
>>> exit()
```

---

## 🔧 Project Structure (No Changes Needed)

The project is designed to work on any laptop. All scripts use:
- ✅ Pure Python (no shell commands)
- ✅ Django ORM (database operations)
- ✅ Portable paths (not hardcoded)
- ✅ Standard Python libraries only

### Key Files Modified (Live Updates)
- `admin_management/views.py` - Dynamic dashboard metrics
- `trust_ethics/views.py` - Dynamic trust dashboard with charts
- `trust_ethics/dashboard.html` - 2 interactive graphs
- `recommendations/views.py` - Dynamic recommendations stats
- `user_interaction/views.py` - Auto-creates trust metrics on user interaction

---

## 📈 Dashboard URLs

Visit these pages to see live-updating dashboards:

| Dashboard | URL | Updates When |
|-----------|-----|--------------|
| Admin Portal | http://127.0.0.1:8000/admin-management/dashboard/ | New logins/operations |
| Analytics | http://127.0.0.1:8000/admin-management/analytics/ | Users interact with AI |
| Trust Metrics | http://127.0.0.1:8000/trust/ | Users ask questions |
| Recommendations | http://127.0.0.1:8000/recommendations/ | New recommendations created |

---

## 🔄 How Data Updates Work

### Interactive Update Flow
```
1. User (any laptop) goes to: http://127.0.0.1:8000/interaction/
2. User asks a question
3. AI generates response with confidence score
4. System AUTOMATICALLY creates:
   - TrustMetric (confidence → 0-100 scale)
   - 4 EthicalAlignment records (Alignment, Transparency, Accountability, Fairness)
5. User visits Trust dashboard: http://127.0.0.1:8000/trust/
6. Charts automatically show NEW data!
```

### Database Tables Updated
- `trust_ethics_trustmetric` - One entry per interaction
- `trust_ethics_ethicalalignment` - Four entries per interaction
- `admin_management_auditlog` - Tracks admin operations
- `feedback_feedback` - User feedback tracking
- `user_interaction_userinput` - All user inputs
- `user_interaction_airesponse` - All AI responses

---

## 🖥️ Running on Another Laptop

### Step 1: Copy Project Files
Copy the entire `hais_project2` folder to your new laptop.

### Step 2: Install Python
- **Windows**: Download from python.org
- **Mac**: `brew install python3`
- **Linux**: `sudo apt install python3`

### Step 3: Install Dependencies
```
cd hais_project2
python -m pip install -r requirements.txt
```

### Step 4: Apply Migrations (IMPORTANT!)
```
python manage.py migrate
```

### Step 5: Start Server
```
python manage.py runserver 8000
```

### Step 6: Create Admin Account (First Time Only)
```
python manage.py createsuperuser
```

---

## 📝 Available Python Utility Scripts

All scripts work on any laptop without shell dependencies:

### 1. Check Trust Data
```
python check_trust_data.py
```
**Output**: Shows all trust metrics and ethical alignments by user

### 2. Test Interaction Data
```
python test_interaction.py
```
**Output**: Creates sample metrics for dashboard testing

### 3. Clear Database (using Django Shell)
Create file `clear_data.py`:
```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hais_core.settings')
django.setup()

from trust_ethics.models import TrustMetric, EthicalAlignment
from feedback.models import Feedback

print("Clearing data...")
TrustMetric.objects.all().delete()
EthicalAlignment.objects.all().delete()
print("✅ Data cleared!")
```

Then run:
```
python clear_data.py
```

---

## 🔍 Troubleshooting

### Issue: "ModuleNotFoundError" when running scripts
**Solution**: Make sure you're in the project directory:
```
cd path/to/hais_project2
python check_trust_data.py
```

### Issue: "django.core.exceptions.ImproperlyConfigured"
**Solution**: Ensure settings.py path is correct in scripts

### Issue: Database locked
**Solution**: Stop the server first, then run utility scripts

### Issue: Charts show "No data"
**Solution**: Run test_interaction.py to create sample data, then refresh dashboard

---

## 📊 Expected Dashboard Results

After running `python test_interaction.py`, you should see:

### Trust Metrics Dashboard
- ✅ Trust Evolution chart (line chart)
- ✅ Ethical Alignment chart (doughnut: 85%, 92%, 88%, 90%)
- ✅ Both charts with real data (not empty states)

### Admin Dashboard
- ✅ Total Users: Dynamic count
- ✅ User Satisfaction: Dynamic percentage
- ✅ Monthly Interactions: Dynamic count
- ✅ System Uptime: Dynamic percentage

---

## 🛠️ Development Notes

### All Pure Python (No Shell Commands Used)
- ❌ No bash scripts
- ❌ No PowerShell scripts
- ❌ No shell.sh files
- ✅ All Python files
- ✅ All Django management commands
- ✅ All ORM queries

### Portable to Any System
- ✅ Works on Windows, Mac, Linux
- ✅ No hardcoded paths
- ✅ No system-specific dependencies
- ✅ Standard Python library only (except Django, numpy, scikit-learn for ML)

---

## 📞 Support

If dashboards don't update:
1. Run `python check_trust_data.py` to verify data exists
2. Run `python test_interaction.py` to create sample data
3. Refresh browser
4. Check Django server console for errors

---

**Last Updated**: February 14, 2026
**Project Version**: HAIS 2.0 (Updated)
**Compatibility**: Python 3.8+, Django 5.0.6
