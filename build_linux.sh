#!/bin/bash
# Build LongBookMerger v1.1 as a single Linux executable using PyInstaller
# Much simpler and more reliable than AppImage for Python GUI apps

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[Build] Setting up build environment..."

# Create isolated build venv
if [ ! -d "build_venv" ]; then
    python3 -m venv build_venv
fi
source build_venv/bin/activate

# Install build tools
pip install --upgrade pip
pip install pyinstaller

# Install app dependencies
pip install -r requirements.txt

echo "[Build] Creating single executable..."

# Build single executable
pyinstaller \
    --noconfirm \
    --onefile \
    --windowed \
    --name "LongBookMerger-v1.1" \
    --hidden-import PySide6 \
    --hidden-import PySide6.QtCore \
    --hidden-import PySide6.QtGui \
    --hidden-import PySide6.QtWidgets \
    --hidden-import reportlab \
    --hidden-import reportlab.pdfbase \
    --hidden-import reportlab.pdfbase._fontdata \
    --hidden-import bs4 \
    --hidden-import lxml \
    --hidden-import PyPDF2 \
    --collect-all PySide6 \
    --collect-all reportlab \
    main.py

echo "[Build] Done!"
echo "[Build] Executable: dist/LongBookMerger-v1.1"
echo ""
echo "To run: ./dist/LongBookMerger-v1.1"
