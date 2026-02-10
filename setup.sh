#!/bin/bash
# Setup script for News Trading Bot on macOS
# This script creates virtual environment and installs all dependencies

set -e  # Exit on error

echo "=========================================="
echo "News Trading Bot - macOS Setup"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Step 1: Create virtual environment
echo ""
echo "[1/4] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists"
    read -p "Remove and recreate? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo "✓ Virtual environment recreated"
    else
        echo "✓ Using existing virtual environment"
    fi
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Step 2: Activate virtual environment
echo ""
echo "[2/4] Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Step 3: Upgrade pip
echo ""
echo "[3/4] Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ pip upgraded"

# Step 4: Install dependencies
echo ""
echo "[4/4] Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt --quiet
echo "✓ All dependencies installed"

# Verify siliconmetatrader5 installation
echo ""
echo "=========================================="
echo "Verifying Installation"
echo "=========================================="

if python3 -c "from siliconmetatrader5 import MetaTrader5" 2>/dev/null; then
    echo "✓ siliconmetatrader5 installed successfully"
else
    echo "❌ siliconmetatrader5 installation failed"
    exit 1
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p logs
mkdir -p state
echo "✓ Directories created"

# Summary
echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Activate venv: source venv/bin/activate"
echo "  2. Setup MT5 bridge (see docs/MT5_SETUP.md)"
echo "  3. Test connection: python3 test_mt5_connection.py"
echo "  4. Run bot: python3 main.py --mode dev"
echo ""
echo "Important:"
echo "  - MT5 bridge must run on localhost:8001"
echo "  - Keep MT5 terminal open and logged in"
echo "  - See docs/VENV_SETUP.md for detailed guide"
echo ""
