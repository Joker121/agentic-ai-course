#!/bin/bash
# Installation script for the Agentic AI Course

set -e

echo "🚀 Agentic AI Course — Installation"
echo "==================================="

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Check if Python 3.11+
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]; }; then
    echo "❌ Python 3.11+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version check passed"

# Create virtual environment
echo ""
echo "📦 Setting up virtual environment..."
python3 -m venv .venv
source .venv/bin/activate
echo "✅ Virtual environment created"

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Copy environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "📝 Created .env file from .env.example"
    echo "⚠️  Please edit .env with your API keys before proceeding"
fi

echo ""
echo "==================================="
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your LLM_API_KEY"
echo "  2. Run: source .venv/bin/activate"
echo "  3. Run: pip install -r requirements.txt"
echo "  4. Run: python modules/m0-hello/main.py"
echo "  5. Deploy: railway up"
echo ""
