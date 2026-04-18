@echo off
REM ============================================================
REM System Verification Script
REM ============================================================
REM This verifies that everything is properly installed

echo.
echo ============================================================
echo        SYSTEM VERIFICATION CHECK
echo ============================================================
echo.

REM Check Python
echo [1/5] Checking Python...
python --version
if errorlevel 1 (
    echo    ERROR: Python not found
    exit /b 1
) else (
    echo    ✓ Python OK
)
echo.

REM Check virtual environment
echo [2/5] Checking virtual environment...
if exist venv (
    echo    ✓ Virtual environment exists
) else (
    echo    ERROR: Virtual environment not found - run START_HERE.bat first
    exit /b 1
)
echo.

REM Check requirements
echo [3/5] Checking installed packages...
call venv\Scripts\activate.bat
pip list | findstr "Django" >nul
if errorlevel 1 (
    echo    ERROR: Django not installed
    exit /b 1
) else (
    echo    ✓ Django installed
)

pip list | findstr "google-generativeai" >nul
if errorlevel 1 (
    echo    ERROR: google-generativeai not installed
    exit /b 1
) else (
    echo    ✓ Google Generative AI installed
)
echo.

REM Check database
echo [4/5] Checking database...
if exist db.sqlite3 (
    echo    ✓ Database file exists
) else (
    echo    ERROR: Database not found
    exit /b 1
)
echo.

REM Check .env
echo [5/5] Checking configuration...
if exist .env (
    echo    ✓ Configuration file exists
    REM Check if Gemini API key is there
    findstr /I "GEMINI_API_KEY" .env >nul
    if errorlevel 1 (
        echo    WARNING: GEMINI_API_KEY not found in .env
    ) else (
        echo    ✓ Gemini API Key configured
    )
) else (
    echo    ERROR: .env file not found
    exit /b 1
)
echo.

echo ============================================================
echo ✓ ALL SYSTEMS OK - Ready to run!
echo ============================================================
echo.
echo Next: Run START_HERE.bat to start the chatbot
echo.
pause
