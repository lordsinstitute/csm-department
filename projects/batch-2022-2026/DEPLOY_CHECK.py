#!/usr/bin/env python3
"""
HAIS Deployment Verification Script
Checks if the chatbot is ready to run on any computer (Windows/Mac/Linux)
Run this BEFORE trying to start the chatbot
"""

import os
import sys
import platform
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 8):
        return True, f"✓ Python {version} (OK)"
    return False, f"✗ Python {version} (Need 3.8+)"

def check_file_exists(filename):
    """Check if a file exists"""
    return os.path.exists(filename)

def check_folder_exists(foldername):
    """Check if a folder exists"""
    return os.path.isdir(foldername)

def check_env_file():
    """Check .env file configuration"""
    if not os.path.exists('.env'):
        return False, "✗ .env file missing"
    
    with open('.env', 'r') as f:
        content = f.read()
        if 'GEMINI_API_KEY' not in content:
            return False, "✗ GEMINI_API_KEY not in .env"
        if 'AIzaSy' not in content:
            return False, "✗ API key appears empty"
    
    return True, "✓ .env configured with Gemini API key"

def check_critical_folders():
    """Check critical application folders"""
    folders = [
        'hais_core',
        'users',
        'recommendations',
        'templates',
        'static'
    ]
    missing = [f for f in folders if not check_folder_exists(f)]
    
    if missing:
        return False, f"✗ Missing folders: {', '.join(missing)}"
    return True, "✓ All critical folders exist"

def check_critical_files():
    """Check critical application files"""
    files = [
        'manage.py',
        'requirements.txt',
        '.env',
        'db.sqlite3'
    ]
    missing = [f for f in files if not check_file_exists(f)]
    
    if missing:
        return False, f"✗ Missing files: {', '.join(missing)}"
    return True, "✓ All critical files exist"

def check_django():
    """Check if Django is installed"""
    try:
        import django
        return True, f"✓ Django {django.VERSION[0]}.{django.VERSION[1]} installed"
    except ImportError:
        return False, "✗ Django not installed (run: pip install -r requirements.txt)"

def check_gemini():
    """Check if Gemini package is installed"""
    try:
        import google.generativeai
        return True, "✓ Google Generative AI (Gemini) installed"
    except ImportError:
        return False, "✗ Gemini package not installed (run: pip install google-generativeai)"

def check_database():
    """Check if database exists and is valid"""
    if not os.path.exists('db.sqlite3'):
        return False, "✗ Database not found (will be created on first run)"
    
    try:
        import sqlite3
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        
        if not tables:
            return False, "✗ Database is empty (needs migration)"
        return True, f"✓ Database valid ({len(tables)} tables)"
    except Exception as e:
        return False, f"✗ Database error: {e}"

def check_ai_service():
    """Check if AI service loads correctly"""
    try:
        # Suppress warnings for this check
        import warnings
        warnings.filterwarnings('ignore')
        from hais_core.ai_service import ai_service
        return True, "✓ AI Service (Gemini) loads successfully"
    except ImportError as e:
        return False, f"✗ AI Service error: {e}"
    except Exception as e:
        return False, f"✗ AI Service error: {e}"

def run_deployment_check():
    """Run all checks"""
    print("\n" + "="*60)
    print("     HAIS CHATBOT - DEPLOYMENT VERIFICATION")
    print("="*60 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Python Packages", check_django),
        ("Gemini AI Package", check_gemini),
        ("Configuration File", check_env_file),
        ("Critical Files", check_critical_files),
        ("Critical Folders", check_critical_folders),
        ("Database", check_database),
        ("AI Service", check_ai_service),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            success, message = check_func()
            results.append((success, message))
            print(message)
        except Exception as e:
            message = f"✗ {name}: {e}"
            results.append((False, message))
            print(message)
        print()
    
    # Summary
    total = len(results)
    passed = sum(1 for success, _ in results if success)
    
    print("="*60)
    print(f"RESULTS: {passed}/{total} checks passed")
    print("="*60 + "\n")
    
    if passed == total:
        print("✓ ALL SYSTEMS OK - Ready to run!")
        print("\nNext steps:")
        print("1. Run: START_HERE.bat (Windows) or bash START_HERE.sh (Mac/Linux)")
        print("2. Wait ~5 minutes for setup")
        print("3. Open: http://localhost:8000/")
        print("\n✓✓✓ Chatbot will be ready to use! ✓✓✓\n")
        return 0
    else:
        failed = total - passed
        print(f"✗ {failed} issue(s) found that need fixing:\n")
        
        for success, message in results:
            if not success:
                if "Django" in message and not success:
                    print("FIX: Run this command:")
                    print("   Windows: pip install -r requirements.txt")
                    print("   Mac/Linux: pip3 install -r requirements.txt\n")
                elif "Gemini" in message:
                    print("FIX: Run this command:")
                    print("   pip install google-generativeai\n")
                elif "GEMINI_API_KEY" in message:
                    print("FIX: Edit .env file and add GEMINI_API_KEY\n")
                elif "Database" in message and "empty" in message:
                    print("FIX: Run this command:")
                    print("   python manage.py migrate\n")
        
        print("\nAfter fixing issues above, run this script again!")
        return 1

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.exit(run_deployment_check())
