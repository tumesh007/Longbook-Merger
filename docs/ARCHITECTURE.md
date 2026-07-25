# LongBook Merger Architecture

## Overview

LongBook Merger is a Python-based desktop application using PyQt5 for the GUI.

## Module Structure

```
src/
├── main.py              # Entry point
├── gui.py               # PyQt5 GUI components
├── parser.py            # Parse Long Book formats
├── pdf_generator.py     # PDF creation and formatting
├── html_detector.py     # Detect HTML content
├── sorter.py            # Sort and organize data
├── utils.py             # Utility functions
├── settings.py          # Configuration management
├── bookmarks.py         # PDF bookmarks/TOC
└── index_page.py        # Generate index pages
```

## Data Flow

1. User selects input files via GUI
2. Parser reads and parses file contents
3. Data is sorted and organized
4. PDF generator creates output document
5. Bookmarks and index generated
6. PDF is saved to disk

## Key Classes

### GUI (PyQt5)
- Main window and dialogs
- File selection
- Progress tracking
- Output preview

### Parser
- CBSL format parsing
- Finacle CSV parsing
- HTML content detection
- Data validation

### PDF Generator
- ReportLab-based PDF creation
- A4 Landscape formatting
- Header/footer management
- Style application

## Dependencies

- PyQt5 - GUI framework
- ReportLab - PDF generation
- Python 3.8+

See requirements.txt for complete list.
