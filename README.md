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

#### Linux
```bash
# Clone or download repository
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

#### macOS
```bash
cd Longbook-Merger
bash scripts/setup.sh
bash scripts/run.sh
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

### Executable (Linux)
```bash
bash scripts/build_linux.sh
```

### Executable (Windows)
```batch
scripts\build_windows.bat
```

## Project Structure

```
Longbook-Merger/
├── src/                    # Source code
│   ├── main.py            # Entry point
│   ├── gui.py             # GUI components
│   ├── parser.py          # File parsing
│   ├── pdf_generator.py   # PDF creation
│   ├── utils.py           # Utilities
│   └── ...
├── config/                # Configuration files
├── scripts/               # Build/run scripts
├── docs/                  # Documentation
├── requirements.txt       # Dependencies
└── README.md              # This file
```

## Dependencies

Core libraries:
- **PyQt5** - GUI framework
- **ReportLab** - PDF generation
- **pandas** - Data processing
- **Pillow** - Image handling

See `requirements.txt` for complete list.

## Configuration

Edit `src/settings.py` to customize:
- Default output directory
- PDF page margins
- Font settings
- Color schemes
- Processing options

## Troubleshooting

### GUI doesn't start
```bash
# Check PyQt5 installation
python3 -c "import PyQt5; print(PyQt5.__version__)"

# Reinstall if needed
pip install --upgrade PyQt5
```

### PDF generation fails
- Verify input files are valid CBSL/Finacle exports
- Check output directory permissions
- Ensure sufficient disk space
- Try with a smaller file first

### Performance issues
- Close other applications
- Use SSD for temporary files
- Reduce number of files per batch

## License

MIT License - See LICENSE file

## Author

**Tumesh007** - [GitHub](https://github.com/tumesh007)

## Support & Issues

- 📖 [Documentation](docs/)
- 🐛 [Report Issues](https://github.com/tumesh007/Longbook-Merger/issues)
- 💬 [GitHub Discussions](https://github.com/tumesh007/Longbook-Merger/discussions)

---

**Latest Version**: 1.1.0  
**Last Updated**: July 2026  
**Status**: Active Development
