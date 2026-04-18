#!/usr/bin/env python
"""
HAIS Project - Startup Verification Script
Checks if all dependencies are installed and project is ready to run
Pure Python - Works on Windows, Mac, and Linux
"""
import os
import sys
import subprocess

def check_python_version():
    """Check if Python 3.8 or higher is installed"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_django():
    """Check if Django is installed"""
    try:
        import django
        print(f"✅ Django {django.get_version()} installed")
        return True
    except ImportError:
        print("❌ Django not installed. Run: python -m pip install -r requirements.txt")
        return False

def check_required_packages():
    """Check if required packages are installed"""
    required = [
        'django',
        'numpy',
        'sklearn',
        'google',
    ]
    
    all_found = True
    print("\n📦 Checking required packages:")
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - Missing")
            all_found = False
    
    return all_found

def check_database():
    """Check if database is set up"""
    try:
        # Add project root to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hais_core.settings')
        import django
        django.setup()
        
        from django.core.management import call_command
        from django.db import connection
        
        # Try to query users table
        from users.models import CustomUser
        user_count = CustomUser.objects.count()
        print(f"✅ Database connected - {user_count} users found")
        return True
        
    except Exception as e:
        print(f"❌ Database issue: {str(e)}")
        print("   Run: python manage.py migrate")
        return False

def main():
    print("=" * 70)
    print("HAIS PROJECT - STARTUP VERIFICATION")
    print("=" * 70)
    
    checks = [
        ("Python Version", check_python_version),
        ("Django", check_django),
        ("Database", check_database),
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}...")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append(False)
    
    print("\n" + "=" * 70)
    if all(results):
        print("✅ ALL CHECKS PASSED - Project is ready!")
        print("\n🚀 To start the server, run:")
        print("   python manage.py runserver 8000")
        print("\n📊 For utility scripts, run:")
        print("   python check_trust_data.py")
        print("   python test_interaction.py")
        return 0
    else:
        print("❌ Some checks failed - See errors above")
        print("\n💡 Quick fixes:")
        print("   1. Install dependencies: python -m pip install -r requirements.txt")
        print("   2. Run migrations: python manage.py migrate")
        print("   3. Create superuser: python manage.py createsuperuser")
        return 1

if __name__ == '__main__':
    sys.exit(main())
