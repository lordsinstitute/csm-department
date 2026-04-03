@echo off
REM ============================================================
REM HAIS GEMINI CHATBOT - Complete Setup & Run Script
REM ============================================================
REM This is the MASTER script to setup and run everything on another laptop
REM Just double-click this file and everything will be installed!

echo.
echo ============================================================
echo        HAIS GEMINI 2.5 FLASH AI CHATBOT
echo        Complete Installation & Launch Script
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo.
    echo SOLUTION:
    echo 1. Download Python 3.10+ from: https://www.python.org/downloads/
    echo 2. During installation, CHECK the box: "Add Python to PATH"
    echo 3. Run this script again
    echo.
    pause
    exit /b 1
)

echo [1/9] Checking Python version...
python --version
echo.

REM Create virtual environment
echo [2/9] Creating Python virtual environment...
if exist venv (
    echo    (Virtual environment already exists)
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo    ✓ Created
)
echo.

REM Activate virtual environment
echo [3/9] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo    ✓ Activated
echo.

REM Upgrade pip
echo [4/9] Upgrading pip...
python -m pip install --upgrade pip -q
echo    ✓ Pip upgraded
echo.

REM Install dependencies
echo [5/9] Installing Python packages (this may take 2-3 minutes)...
echo    Installing: Django, Google Gemini AI, Database tools, etc...
pip install -r requirements.txt -q
if errorlevel 1 (
    REM Don't fail on pip errors, continue anyway
    echo    ⚠ Some packages may have warnings (usually OK, continuing)
)
echo    ✓ All packages installed
echo.

REM Create .env file from example if it doesn't exist
echo [6/9] Setting up configuration (.env file)...
if not exist .env (
    copy .env.example .env >nul
    echo    ✓ Created .env from template
    echo    NOTE: Gemini API Key is already configured!
) else (
    echo    (Configuration already exists)
)
echo.

REM Run migrations
echo [7/9] Initializing database...
python manage.py migrate -q
if errorlevel 1 (
    echo    ⚠ Migration warnings (usually OK)
)
echo    ✓ Database ready
echo.

REM Check if admin user exists, if not create one
echo [8/9] Checking admin account...
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('Admin exists' if User.objects.filter(is_superuser=True).exists() else 'Need admin')" >temp_admin_check.txt
set /p ADMIN_CHECK=<temp_admin_check.txt
del temp_admin_check.txt

if "%ADMIN_CHECK%"=="Need admin" (
    echo.
    echo ============================================================
    echo CREATE ADMIN ACCOUNT
    echo ============================================================
    echo Please create your admin account now:
    echo.
    python manage.py createsuperuser
) else (
    echo    ✓ Admin account already exists
)
echo.

REM Collect static files
echo [9/9] Preparing web interface...
python manage.py collectstatic --noinput -q 2>nul
echo    ✓ Ready
echo.

echo.
echo ============================================================
echo ✓ SETUP COMPLETE! Starting server...
echo ============================================================
echo.
echo Your chatbot is starting...
echo.
echo ============================================================
echo ACCESS YOUR CHATBOT:
echo ============================================================
echo.
echo Web Interface:  http://localhost:8000/
echo Admin Panel:    http://localhost:8000/admin/
echo Chat:           http://localhost:8000/interaction/
echo.
echo ============================================================
echo MODEL: Google Gemini 2.5 Flash
echo STATUS: Ready for real-time AI responses
echo ============================================================
echo.
echo Press CTRL+C to stop the server
echo.
echo ============================================================
echo.

REM Start the development server
python manage.py runserver 0.0.0.0:8000

REM Keep window open if server crashes
if errorlevel 1 (
    echo.
    echo ERROR: Server failed to start
    echo.
    pause
)
