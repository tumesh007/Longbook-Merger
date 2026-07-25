# LongBook Merger Documentation

## Overview

LongBook Merger is a fast, offline desktop application for merging CBSL/Finacle Long Book reports into print-ready A4 Landscape PDF files.

## Features

- ✅ Fast offline processing
- ✅ Multi-platform support (Windows, Linux, macOS)
- ✅ Beautiful PyQt5 GUI
- ✅ Batch processing
- ✅ Customizable output settings
- ✅ PDF optimization

## Quick Start

### Linux
```bash
cd scripts
./setup.sh
./run.sh
```

### Windows
```batch
scripts\setup.bat
scripts\run.bat
```

## Usage

1. Launch the application
2. Select Long Book export files (CSV or HTML format)
3. Configure output settings
4. Click "Generate PDF"
5. Save to desired location

## Configuration

See `config/` directory for build and runtime configurations.

## Building Executables

### Linux AppImage
```bash
scripts/build_appimage.sh
```

### Linux Executable
```bash
scripts/build_linux.sh
```

### Windows Executable
```batch
scripts\build_windows.bat
```

## Troubleshooting

### GUI doesn't launch
- Ensure PyQt5 is installed: `pip install PyQt5`
- Check Python version is 3.8+
- Try running with: `python3 -u src/main.py`

### PDF generation fails
- Verify input files are in correct format
- Check output directory has write permissions
- Ensure sufficient disk space

## File Format Support

- ✅ CBSL Long Book exports
- ✅ Finacle CSV exports
- ✅ HTML formatted reports
- ✅ Plain text tables
