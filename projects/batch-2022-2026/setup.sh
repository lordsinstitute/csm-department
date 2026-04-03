#!/bin/bash
# ============================================================
# HAIS Project Setup Script for Linux/Mac
# ============================================================
# This script sets up the HAIS project on Linux or Mac systems

set -e  # Exit on error

echo ""
echo "============================================================"
echo "HAIS Project Setup for Linux/Mac"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ using: sudo apt-get install python3 python3-pip python3-venv"
    exit 1
fi

echo "[1/7] Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "[2/7] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo ""
echo "[3/7] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

# Upgrade pip
echo ""
echo "[4/7] Upgrading pip..."
pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to upgrade pip"
    exit 1
fi

# Install dependencies
echo ""
echo "[5/7] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Create .env file from example if it doesn't exist
echo ""
echo "[6/7] Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env file from .env.example"
    echo "Please edit .env and add your configuration (especially OPENAI_API_KEY if using AI features)"
else
    echo ".env file already exists. Skipping creation."
fi

# Run migrations
echo ""
echo "[7/7] Running database migrations..."
python manage.py migrate || echo "WARNING: Migrations may have issues, but continuing..."

echo ""
echo "============================================================"
echo "Setup Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "   1. Edit .env file with your configuration (especially OPENAI_API_KEY)"
echo "   2. Create a superuser (if first time): python manage.py createsuperuser"
echo "   3. Run the development server: python manage.py runserver"
echo ""
echo "To run the server later:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Run server: python manage.py runserver"
echo ""
echo "Access the application at: http://127.0.0.1:8000"
echo "Admin panel at: http://127.0.0.1:8000/django-admin/"
echo ""
