#!/bin/bash
# Build AppImage for Linux

set -e

echo "Building AppImage..."

cd "$(dirname "$0")/.."

# Install dependencies
pip install -r requirements.txt

# Build using appimage-builder
appimage-builder --recipe appimage_builder.yml

echo "AppImage build complete!"
echo "Output: LongBookMerger-*.AppImage"
