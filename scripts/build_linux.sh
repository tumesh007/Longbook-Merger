#!/bin/bash
# Build Linux executable using PyInstaller

set -e

echo "Building Linux executable..."

cd "$(dirname "$0")/.."

# Install build dependencies
pip install -r requirements.txt
pip install pyinstaller

# Create spec file if needed
if [ ! -f "LongBookMerger.spec" ]; then
    pyinstaller --onefile --windowed src/main.py --name LongBookMerger
else
    pyinstaller LongBookMerger-v1.1.spec
fi

echo "Build complete!"
echo "Executable: dist/LongBookMerger"
