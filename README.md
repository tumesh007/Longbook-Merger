# LongBookMerger v1.1

**Merge fixed-width PNB CBSL/Finacle Long Book `.rpt` files into A4 landscape PDFs.**

> **Author:** Tumesh 
> **GitHub:** https://github.com/tumesh007/Longbook-Merger  
> **Version:** 1.1

---

## What is Fixed in v1.1

| Issue | Root Cause | Fix Applied |
|-------|-----------|-------------|
| **2 papers per sheet** | Margins were too loose (10mm all sides) + headers/footers consumed ~22mm extra space + line leading was 1.22x | Margins tightened to **8/8/5/5 mm** (L/R/T/B); line leading reduced to **1.03x**; headers/footers **disabled by default** |
| **Compact mode not working** | Only disabled headers/footers; did not remove cover pages | Added `is_cover_page()` detection from working script; compact now strips title/cover pages with ≤16 lines and no "TRAN ID" |
| **Font sizing inaccurate** | Used ReportLab `stringWidth()` which differs from actual Courier rendering | Switched to **Courier width factor 0.60** matching the working script |
| **HTML handling gaps** | BeautifulSoup-only approach missed `<pre>` blocks and `&nbsp;` preservation | Added `looks_like_html()` + `html_report_to_text()` with `<pre>` extraction, `&nbsp;` → space conversion, and `<hr>` → form-feed |

---

## File Structure

```
LongBookMerger-v1.1/
├── main.py              # Entry point
├── gui.py               # PySide6 desktop UI
├── pdf_generator.py     # PDF rendering engine (ReportLab)
├── parser.py            # Report parsing (.rpt / .html / .txt)
├── html_detector.py     # Content-based HTML sniffing
├── sorter.py            # Filename date detection & chronological sort
├── bookmarks.py         # ReportLab bookmark key generation
├── index_page.py        # Table of contents drawing
├── settings.py          # QSettings persistence wrapper
├── utils.py             # File collection, ZIP extraction, logging
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## Quick Start (Run from Source)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python main.py
```

---

## Building Standalone Executables

### Option A: Windows Executable (PyInstaller)

#### Step 1 — Install PyInstaller

```bash
pip install pyinstaller
```

#### Step 2 — Build

```bash
pyinstaller --noconfirm --onefile --windowed   --name "LongBookMerger-v1.1"   --add-data "assets;assets"   --icon=assets/icon.ico   main.py
```

> **Note:** If you do not have an `assets/` folder or icon, omit `--add-data` and `--icon` flags.

#### Output

- `dist/LongBookMerger-v1.1.exe` — single-file Windows executable

#### Optional: Create an Installer (Inno Setup)

1. Download and install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Create a script `setup.iss`:

```iss
[Setup]
AppName=LongBookMerger
AppVersion=1.1
DefaultDirName={autopf}\LongBookMerger
OutputBaseFilename=LongBookMerger-v1.1-Setup
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\LongBookMerger-v1.1.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\LongBookMerger"; Filename: "{app}\LongBookMerger-v1.1.exe"
Name: "{commondesktop}\LongBookMerger"; Filename: "{app}\LongBookMerger-v1.1.exe"
```

3. Compile in Inno Setup Compiler → produces `LongBookMerger-v1.1-Setup.exe`

---

### Option B: Linux AppImage

AppImage is a **single-file portable Linux executable** that works on most distributions without installation.

#### Prerequisites

```bash
sudo apt update
sudo apt install python3-dev python3-pip python3-venv patchelf desktop-file-utils
pip install appimage-builder
```

> If `appimage-builder` is unavailable via pip, download the AppImage from:  
> https://github.com/AppImageCrafters/appimage-builder/releases

#### Step 1 — Create Virtual Environment

```bash
cd LongBookMerger-v1.1
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Step 2 — Create AppDir Structure

```bash
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/lib
mkdir -p AppDir/usr/share/applications
mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps
```

#### Step 3 — Copy Application Files

```bash
cp main.py gui.py pdf_generator.py parser.py html_detector.py sorter.py bookmarks.py index_page.py settings.py utils.py AppDir/usr/bin/
cp requirements.txt AppDir/
```

#### Step 4 — Create Desktop Entry

Create `AppDir/usr/share/applications/longbookmerger.desktop`:

```desktop
[Desktop Entry]
Name=LongBookMerger
Exec=longbookmerger
Icon=longbookmerger
Type=Application
Categories=Office;Finance;
Comment=Merge PNB Long Book reports into PDF
```

Create symlink:

```bash
ln -s usr/share/applications/longbookmerger.desktop AppDir/longbookmerger.desktop
```

#### Step 5 — Create Launcher Script

Create `AppDir/AppRun`:

```bash
#!/bin/bash
HERE="$(dirname "$(readlink -f "$0")")"
export PYTHONPATH="${HERE}/usr/bin:${PYTHONPATH}"
export PATH="${HERE}/usr/bin:${PATH}"
python3 "${HERE}/usr/bin/main.py" "$@"
```

Make it executable:

```bash
chmod +x AppDir/AppRun
```

Create symlink for binary:

```bash
ln -s AppRun AppDir/usr/bin/longbookmerger
```

#### Step 6 — Create AppImageBuilder Recipe

Create `AppImageBuilder.yml`:

```yaml
version: 1
script:
  - rm -rf AppDir | true
  - mkdir -p AppDir/usr/bin
  - cp *.py AppDir/usr/bin/
  - cp requirements.txt AppDir/
  - mkdir -p AppDir/usr/share/applications
  - cp AppDir/usr/share/applications/longbookmerger.desktop AppDir/ || true
  - chmod +x AppDir/AppRun

AppDir:
  path: ./AppDir
  app_info:
    id: com.pnbtools.longbookmerger
    name: LongBookMerger
    icon: longbookmerger
    version: 1.1
    exec: usr/bin/longbookmerger
    exec_args: $@
  apt:
    arch: amd64
    sources:
      - sourceline: 'deb http://archive.ubuntu.com/ubuntu/ jammy main restricted universe multiverse'
        key_url: 'http://keyserver.ubuntu.com/pks/lookup?op=get&search=0x871920D1991BC93C'
    include:
      - python3
      - python3-pip
      - python3-venv
      - libqt6widgets6
      - libqt6gui6
      - libqt6core6
  files:
    include:
      - /usr/bin/python3*
      - /usr/lib/python3*/**
    exclude:
      - usr/share/man
      - usr/share/doc/*/README.*
      - usr/share/doc/*/changelog.*
      - usr/share/doc/*/NEWS.*
      - usr/share/doc/*/TODO.*
  runtime:
    env:
      PYTHONHOME: "${APPDIR}/usr"
      PYTHONPATH: "${APPDIR}/usr/lib/python3.10:${APPDIR}/usr/lib/python3.10/lib-dynload"

AppImage:
  arch: x86_64
  update-information: guess
  sign-key: None
```

> Adjust `python3.10` in `PYTHONPATH` to match your system Python version (`python3 --version`).

#### Step 7 — Install Dependencies into AppDir

```bash
source venv/bin/activate
pip install --target=AppDir/usr/lib -r requirements.txt
```

#### Step 8 — Build the AppImage

```bash
appimage-builder --recipe AppImageBuilder.yml
```

Output: `LongBookMerger-1.1-x86_64.AppImage`

#### Step 9 — Test

```bash
chmod +x LongBookMerger-1.1-x86_64.AppImage
./LongBookMerger-1.1-x86_64.AppImage
```

---

### Option C: Simple Linux Binary (PyInstaller)

If AppImage is too complex, use PyInstaller directly:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed   --name "LongBookMerger-v1.1"   --add-data "assets:assets"   main.py
```

Output: `dist/LongBookMerger-v1.1` (single executable file)

---

## Usage Guide

### Input
- **Drag & drop** `.rpt`, `.txt`, `.html`, `.htm` files, **folders**, or **ZIP archives**
- Reports are **auto-sorted chronologically** by detecting `DD-MM-YYYY` in filenames

### Output Variants
| Variant | Description |
|---------|-------------|
| **Full PDF** | All pages including covers, with optional bookmarks |
| **Compact PDF** | Removes cover/title pages, maximizes content density |
| **With Index** | Full PDF + clickable table of contents |
| **Booklet** | Re-orders pages for duplex booklet printing |

### Recommended Settings (v1.1 Defaults)
- ✅ **Auto Font Size** — ON (auto-fits widest report to page width)
- ✅ **Detect Fake HTML** — ON (handles `.html` files that are really fixed-width text)
- ✅ **Remove Blank Pages** — ON
- ❌ **Print Report Title / Filename / Date** — OFF by default (enable only if you have space)
- ❌ **Page X of Y / Timestamp** — OFF by default

> Enabling headers/footers will reduce usable page area and may reintroduce the "2 papers per sheet" issue on very wide reports.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'PySide6'` | Run `pip install -r requirements.txt` |
| `lxml not found` | Install system package: `sudo apt install python3-lxml` (Ubuntu) or `pip install lxml` |
| PDF pages still overflow | Disable headers/footers, enable **Auto Font Size**, or reduce font size manually |
| Compact PDF still has cover pages | Ensure **"Keep Cover Pages"** is unchecked and **"Remove Blank Pages"** is checked |
| AppImage fails to start | Check `PYTHONPATH` in AppRun matches your Python version; try running with `--appimage-extract` and inspect |

---

## Changelog

### v1.1 (2026-07-23)
- Fixed "2 papers per sheet" by tightening margins and reducing line leading
- Fixed compact mode to properly strip cover pages
- Improved HTML report detection and conversion
- Headers/footers now disabled by default to maximize usable area
- Added Courier width factor for accurate font sizing

### v1.0
- Initial release with GUI, ZIP support, bookmarks, and index generation

---

## License

MIT License — free for personal and professional use within PNB and beyond.

---

## Contact

For issues or feature requests, open an issue at:  
https://github.com/tumesh007/Longbook-Merger/issues
