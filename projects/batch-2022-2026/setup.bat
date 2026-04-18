@echo off
REM ============================================================
REM HAIS Project Setup Script for Windows
REM ============================================================
REM This script sets up the HAIS project on a Windows machine

echo.
echo ============================================================
echo HAIS Project Setup for Windows
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    exit /b 1
)

echo [1/7] Checking Python version...
python --version

REM Create virtual environment
echo.
echo [2/7] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        exit /b 1
    )
)

REM Activate virtual environment
echo.
echo [3/7] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    exit /b 1
)

REM Upgrade pip
echo.
echo [4/7] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip
    exit /b 1
)

REM Install dependencies
echo.
echo [5/7] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)

REM Create .env file from example if it doesn't exist
echo.
echo [6/7] Setting up environment configuration...
if not exist .env (
    copy .env.example .env
    echo Created .env file from .env.example
    echo Please edit .env and add your configuration (especially OPENAI_API_KEY if using AI features)
) else (
    echo .env file already exists. Skipping creation.
)

REM Run migrations
echo.
echo [7/7] Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo WARNING: Migrations may have issues, but continuing...
)

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Next steps:
echo   1. Edit .env file with your configuration (especially OPENAI_API_KEY)
echo   2. Create a superuser (if first time): python manage.py createsuperuser
echo   3. Run the development server: python manage.py runserver
echo.
echo To run the server:
echo   1. Activate virtual environment: venv\Scripts\activate.bat
echo   2. Run server: python manage.py runserver
echo.
echo Access the application at: http://127.0.0.1:8000
echo Admin panel at: http://127.0.0.1:8000/django-admin/
echo.
pause
