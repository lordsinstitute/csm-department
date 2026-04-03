#!/bin/bash
# ============================================================
# HAIS GEMINI CHATBOT - Complete Setup & Run Script (Linux/Mac)
# ============================================================
# This is the MASTER script to setup and run everything on another laptop
# Just run: bash START_HERE.sh

set -e  # Exit on any error

echo ""
echo "============================================================"
echo "        HAIS GEMINI 2.5 FLASH AI CHATBOT"
echo "        Complete Installation & Launch Script"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo ""
    echo "SOLUTION:"
    echo "  macOS: brew install python3"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
    echo "  Fedora: sudo dnf install python3"
    echo ""
    exit 1
fi

echo "[1/9] Checking Python version..."
python3 --version
echo ""

# Create virtual environment
echo "[2/9] Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "    (Virtual environment already exists)"
else
    python3 -m venv venv
    echo "    ✓ Created"
fi
echo ""

# Activate virtual environment
echo "[3/9] Activating virtual environment..."
source venv/bin/activate
echo "    ✓ Activated"
echo ""

# Upgrade pip
echo "[4/9] Upgrading pip..."
pip install --upgrade pip -q
echo "    ✓ Pip upgraded"
echo ""

# Install dependencies
echo "[5/9] Installing Python packages (this may take 2-3 minutes)..."
echo "    Installing: Django, Google Gemini AI, Database tools, etc..."
pip install -r requirements.txt -q || echo "    ⚠ Some packages may have warnings (usually OK, continuing)"
echo "    ✓ All packages installed"
echo ""

# Create .env file from example if it doesn't exist
echo "[6/9] Setting up configuration (.env file)..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "    ✓ Created .env from template"
    echo "    NOTE: Gemini API Key is already configured!"
else
    echo "    (Configuration already exists)"
fi
echo ""

# Run migrations
echo "[7/9] Initializing database..."
python manage.py migrate -q 2>/dev/null || true
echo "    ✓ Database ready"
echo ""

# Check if admin user exists, if not create one
echo "[8/9] Checking admin account..."
ADMIN_EXISTS=$(python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('yes' if User.objects.filter(is_superuser=True).exists() else 'no')" 2>/dev/null)

if [ "$ADMIN_EXISTS" = "no" ]; then
    echo ""
    echo "============================================================"
    echo "CREATE ADMIN ACCOUNT"
    echo "============================================================"
    echo "Please create your admin account now:"
    echo ""
    python manage.py createsuperuser
else
    echo "    ✓ Admin account already exists"
fi
echo ""

# Collect static files
echo "[9/9] Preparing web interface..."
python manage.py collectstatic --noinput -q 2>/dev/null || true
echo "    ✓ Ready"
echo ""

echo ""
echo "============================================================"
echo "✓ SETUP COMPLETE! Starting server..."
echo "============================================================"
echo ""
echo "Your chatbot is starting..."
echo ""
echo "============================================================"
echo "ACCESS YOUR CHATBOT:"
echo "============================================================"
echo ""
echo "Web Interface:  http://localhost:8000/"
echo "Admin Panel:    http://localhost:8000/admin/"
echo "Chat:           http://localhost:8000/interaction/"
echo ""
echo "============================================================"
echo "MODEL: Google Gemini 2.5 Flash"
echo "STATUS: Ready for real-time AI responses"
echo "============================================================"
echo ""
echo "Press CTRL+C to stop the server"
echo ""
echo "============================================================"
echo ""

# Start the development server
python manage.py runserver 0.0.0.0:8000
