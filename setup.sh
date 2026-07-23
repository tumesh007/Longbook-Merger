#!/bin/bash
# LongBookMerger v1.1 — Complete Ubuntu Setup & Launcher
# Usage: ./setup.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  LongBookMerger v1.1 Setup"
echo "=========================================="

# Check if running in venv or system
if [ -z "$VIRTUAL_ENV" ]; then
    echo "[Setup] No virtual environment active."

    # Check if venv exists
    if [ ! -d "venv" ]; then
        echo "[Setup] Creating virtual environment..."
        python3 -m venv venv
    fi

    echo "[Setup] Activating virtual environment..."
    source venv/bin/activate
else
    echo "[Setup] Already in virtual environment: $VIRTUAL_ENV"
fi

# Install dependencies
echo "[Setup] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Mark as installed
touch venv/.deps-installed

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "To run the app, use:"
echo "  ./run.sh"
echo ""
echo "To build a single executable:"
echo "  ./build_linux.sh"
echo ""
read -p "Launch LongBookMerger now? (y/n): " launch
if [[ $launch =~ ^[Yy]$ ]]; then
    python main.py
fi
