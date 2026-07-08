# LongBookMerger

LongBookMerger is a production desktop application for Ubuntu that merges CBSL/Finacle Long Book reports into professionally formatted A4 landscape PDF files.

It accepts ZIP files, folders, drag-and-drop inputs, and files ending in `.rpt`, `.txt`, `.html`, `.htm`, or no extension. File type detection is content-based: fixed-width reports saved with a `.html` extension are treated as plain text automatically.

## Features

- Native PySide6 desktop interface
- Drag and drop for reports, folders, and ZIP archives
- Content-based HTML detection
- Chronological sorting from filename dates such as `17-05-2026`, `17_05_2026`, `17052026`, `20260517`, and `17.05.2026`
- A4 landscape PDF output with 10 mm margins
- Monospaced report rendering with automatic font sizing
- Form feed page breaks
- Removal of blank, header-only, and separator-only pages
- Optional headers and footers
- Clickable PDF bookmarks
- Contents/index PDF
- Optional booklet-ordered PDF
- Persistent settings using QSettings
- Full traceback logging in `LongBookMerger.log`

## Generated Files

Depending on selected checkboxes, the output folder receives:

- `LongBook_Full.pdf`
- `LongBook_Compact.pdf`
- `LongBook_With_Index.pdf`
- `LongBook_Booklet.pdf`

## Installation for Users

Download or build `LongBookMerger.AppImage`, then run:

```bash
chmod +x LongBookMerger.AppImage
./LongBookMerger.AppImage
```

The AppImage bundles Python and the application dependencies, so Python does not need to be installed on the target machine.

## Build on Ubuntu 24.04

Install system build requirements:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip patchelf desktop-file-utils appstream file
```

Build the AppImage:

```bash
cd LongBookMerger
chmod +x build_appimage.sh AppRun
./build_appimage.sh
```

The result is:

```text
dist/LongBookMerger.AppImage
```

## Running from Source

```bash
cd LongBookMerger
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

## Usage

1. Click **Browse Files** to select report files or ZIP archives, or click **Browse Folder** to select a folder.
2. Drop reports, folders, or ZIP files directly onto the main window when preferred.
3. Choose an output folder.
4. Select the desired PDF and formatting options.
5. Click **Generate**.

## Screenshots

The main window contains input selection, output folder selection, PDF options, progress, status log, and Generate/Cancel controls.

## Troubleshooting

Logs are written to the platform log directory through `appdirs`. On Ubuntu this is normally:

```text
~/.cache/LongBookMerger/log/LongBookMerger.log
```

If the application does not open on a minimal Ubuntu installation, install common desktop libraries:

```bash
sudo apt install -y libxcb-cursor0 libxkbcommon-x11-0 libgl1
```

If AppImage creation fails, confirm that `appimage-builder` installed successfully in the build virtualenv and that the build machine has internet access for apt and Python packages.

## Project Layout

```text
LongBookMerger/
  src/
    main.py
    gui.py
    parser.py
    pdf_generator.py
    html_detector.py
    sorter.py
    bookmarks.py
    index_page.py
    settings.py
    utils.py
  assets/
    icon.svg
  fonts/
  README.md
  requirements.txt
  pyproject.toml
  build_appimage.sh
  LongBookMerger.desktop
  AppRun
  appimage_builder.yml
  LICENSE
  .gitignore
```
