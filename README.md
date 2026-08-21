# LongBook Merger

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Status](https://img.shields.io/badge/status-Active-green)

## Overview

**LongBook Merger** is a fast, offline desktop application for merging CBSL/Finacle Long Book reports into print-ready A4 Landscape PDF files.

Designed for banking professionals who regularly export and print long books from CBSL/Finacle systems.

## Features

- 🚀 **Fast Processing** - Offline operation, no cloud dependency
- 🎨 **Beautiful GUI** - PyQt5-based user interface
- 📄 **A4 Landscape PDFs** - Print-optimized output format
- 🔀 **Batch Processing** - Handle multiple files
- ⚙️ **Customizable** - Configure fonts, margins, page breaks
- 🖥️ **Cross-Platform** - Windows, Linux, macOS
- 📊 **Smart Parsing** - Auto-detect CBSL/Finacle formats
- 🔖 **Bookmarks & TOC** - Auto-generated table of contents

## Quick Start

### Requirements
- Python 3.8 or higher
- 100 MB disk space
- 2 GB RAM (minimum)

### Installation

#### Linux / macOS
```bash
# Clone repository
git clone https://github.com/tumesh007/Longbook-Merger.git
cd Longbook-Merger

# Run setup
bash scripts/setup.sh

# Launch application
bash scripts/run.sh
```

#### Windows
```batch
cd Longbook-Merger
scripts\setup.bat
scripts\run.bat
```

### Usage

1. **Launch** the application
2. **Select** Long Book export files (supports CBSL CSV, Finacle HTML)
3. **Configure** output options (fonts, margins, etc.)
4. **Generate** - Click "Create PDF"
5. **Save** to desired location

## Supported Formats

| Format | Support | Notes |
|--------|---------|-------|
| CBSL CSV Export | ✅ Full | Standard CBSL format |
| Finacle HTML | ✅ Full | Direct Finacle export |
| Plain CSV | ✅ Partial | Basic table format |
| Plain HTML | ✅ Partial | Basic HTML tables |

## Building Executables

### AppImage (Linux)
```bash
bash scripts/build_appimage.sh
```

### Windows Executable
```batch
scripts\build_windows.bat
```

## Project Structure

```
Longbook-Merger/
├── src/longbook_merger/       # Main package
│   ├── __init__.py
│   ├── main.py                # Entry point
│   ├── gui.py                 # PyQt5 GUI
│   ├── parser.py              # Format parsers
│   ├── pdf_generator.py       # PDF generation
│   ├── bookmarks.py           # TOC/bookmarks
│   ├── html_detector.py       # HTML format detection
│   ├── index_page.py          # Index page generation
│   ├── parser.py              # Core parsing logic
│   ├── pdf_generator.py       # PDF output
│   ├── settings.py            # Settings management
│   ├── sorter.py              # Page sorting
│   └── utils.py               # Utilities
├── config/                    # Configuration files
├── docs/                      # Documentation
├── packaging/                 # Build artifacts & configs
│   ├── AppRun                 # AppImage entry point
│   ├── AppImageBuilder.yml    # AppImage config
│   ├── appimage_builder.yml   # AppImage config (alt)
│   ├── LongBookMerger.desktop # Desktop entry
│   └── LongBookMerger-v1.1.spec # PyInstaller spec
├── scripts/                   # Build/deploy scripts
│   ├── setup.sh / .bat        # Dependency install
│   ├── run.sh / .bat          # Run application
│   ├── build_appimage.sh      # Build AppImage
│   ├── build_linux.sh         # Build Linux binary
│   └── setup.sh / .bat        # Environment setup
├── config/                    # Config files
├── docs/                      # Documentation
├── README.md
├── LICENSE
├── requirements.txt
├── pyproject.toml
├── .gitignore
└── run.sh                     # Quick run script
```

## Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Run directly
python -m src.longbook_merger
```

## License

MIT License - see [LICENSE](LICENSE) for details.
