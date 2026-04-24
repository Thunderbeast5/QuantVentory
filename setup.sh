#!/bin/bash
# 🚀 QUANTVENTORY QUICK START SCRIPT
# Run this to get up and running in one command

echo "⚛  QUANTVENTORY SETUP"
echo "===================="
echo ""

# Step 1: Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi
echo "✅ Python $(python3 --version | cut -d' ' -f2) found"

# Step 2: Create venv
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi
echo "✅ Virtual environment ready"

# Step 3: Activate venv
echo "📌 Activating venv..."
source venv/bin/activate

# Step 4: Install dependencies
echo "📥 Installing dependencies (this may take 2-5 minutes)..."
pip install -q -r requirements.txt 2>/dev/null
echo "✅ Dependencies installed"

# Step 5: Test setup
echo ""
echo "🔍 Verifying installation..."
if python3 test_setup.py; then
    echo ""
    echo "✅ EVERYTHING IS READY!"
    echo ""
    echo "🚀 To start the app, run:"
    echo "   streamlit run app.py"
    echo ""
else
    echo "⚠️  Some issues detected. Check output above."
    exit 1
fi
