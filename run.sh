#!/bin/bash
# LongBookMerger v1.1 — Auto launcher with virtual environment
# Run: ./run.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create venv if missing
if [ ! -d "venv" ]; then
    echo "[LongBookMerger] Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install/update dependencies if needed
if [ ! -f "venv/.deps-installed" ] || [ "requirements.txt" -nt "venv/.deps-installed" ]; then
    echo "[LongBookMerger] Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/.deps-installed
fi

# Launch app
echo "[LongBookMerger] Starting LongBookMerger v1.1..."
python main.py
