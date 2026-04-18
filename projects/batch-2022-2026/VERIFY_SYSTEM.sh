#!/bin/bash
# System Verification Script (Linux/Mac)

echo ""
echo "============================================================"
echo "        SYSTEM VERIFICATION CHECK"
echo "============================================================"
echo ""

# Check Python
echo "[1/5] Checking Python..."
python3 --version
if [ $? -ne 0 ]; then
    echo "    ERROR: Python 3 not found"
    exit 1
else
    echo "    ✓ Python OK"
fi
echo ""

# Check virtual environment
echo "[2/5] Checking virtual environment..."
if [ -d "venv" ]; then
    echo "    ✓ Virtual environment exists"
else
    echo "    ERROR: Virtual environment not found - run START_HERE.sh first"
    exit 1
fi
echo ""

# Check requirements
echo "[3/5] Checking installed packages..."
source venv/bin/activate
pip list | grep -i "Django" >/dev/null
if [ $? -ne 0 ]; then
    echo "    ERROR: Django not installed"
    exit 1
else
    echo "    ✓ Django installed"
fi

pip list | grep -i "google-generativeai" >/dev/null
if [ $? -ne 0 ]; then
    echo "    ERROR: google-generativeai not installed"
    exit 1
else
    echo "    ✓ Google Generative AI installed"
fi
echo ""

# Check database
echo "[4/5] Checking database..."
if [ -f "db.sqlite3" ]; then
    echo "    ✓ Database file exists"
else
    echo "    ERROR: Database not found"
    exit 1
fi
echo ""

# Check .env
echo "[5/5] Checking configuration..."
if [ -f ".env" ]; then
    echo "    ✓ Configuration file exists"
    if grep -q "GEMINI_API_KEY" .env; then
        echo "    ✓ Gemini API Key configured"
    else
        echo "    WARNING: GEMINI_API_KEY not found in .env"
    fi
else
    echo "    ERROR: .env file not found"
    exit 1
fi
echo ""

echo "============================================================"
echo "✓ ALL SYSTEMS OK - Ready to run!"
echo "============================================================"
echo ""
echo "Next: Run 'bash START_HERE.sh' to start the chatbot"
echo ""
