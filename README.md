# LongBookMerger

A fast, offline desktop application for **merging CBSL/Finacle Long Book reports into print-ready A4 Landscape PDF files**.

LongBookMerger is designed for banking professionals who regularly print long books exported from CBSL/Finacle. It automatically detects report formats, merges multiple reports, and produces clean PDFs optimized for A4 landscape printing.

---

## Features

* Merge multiple Long Book reports into a single PDF
* Supports:

  * `.rpt`
  * `.txt`
  * `.html`
  * `.htm`
* Automatically detects fake HTML files (plain text saved with `.html` extension)
* Supports ZIP files or folders as input
* Automatic chronological sorting
* A4 Landscape formatting
* Monospaced report rendering
* Automatic font sizing
* Preserves report alignment
* Generates Full and Compact PDFs
* Removes unnecessary blank pages (optional)
* PDF bookmarks
* Index page (optional)
* Modern Ubuntu GUI
* Works completely offline

---

## Screenshots

(Add screenshots here)

* Main Window
* Selecting Reports
* PDF Generation Progress
* Generated PDF

---

## Installation

### Ubuntu

1. Download the latest `LongBookMerger.AppImage` from the **Releases** page.
2. Make it executable:

```bash
chmod +x LongBookMerger.AppImage
```

3. Run:

```bash
./LongBookMerger.AppImage
```

---

## Creating a Desktop Shortcut

You can launch the application directly, or create a desktop/menu shortcut using the provided installation script.

---

## Usage

1. Launch LongBookMerger.
2. Select a ZIP file or a folder containing reports.
3. Choose the output folder.
4. Configure the desired options.
5. Click **Generate PDF**.

Generated files include:

* `LongBook_Full.pdf`
* `LongBook_Compact.pdf`

---

## Supported Report Formats

LongBookMerger automatically detects:

* Fixed-width text reports
* Reports incorrectly saved with the `.html` extension
* Genuine HTML reports

No manual renaming is required.

---

## Requirements

* Ubuntu 22.04 or later
* x86_64 architecture

No Python installation is required when using the AppImage.

---

## Building from Source

```bash
git clone https://github.com/<your-username>/LongBookMerger.git

cd LongBookMerger

pip install -r requirements.txt

python src/main.py
```

To build the AppImage:

```bash
./build_appimage.sh
```

---

## License

MIT License

---

## Contributing

Bug reports, feature requests, and pull requests are welcome.

---

## Roadmap

* Windows executable
* Batch printing
* PDF compression
* Dark mode
* Automatic update checker
* Multi-language support

---

## Author

**Tumesh Kakkar**

Created to simplify the printing of CBSL/Finacle Long Book reports.

---

## Disclaimer

This application is an independent utility and is **not affiliated with, endorsed by, or supported by CBSL, Finacle, Infosys, Punjab National Bank, or any other bank or software vendor.**

Users are responsible for verifying the accuracy of generated PDFs before official use.
