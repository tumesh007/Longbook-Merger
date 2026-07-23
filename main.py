"""Application entry point — LongBookMerger v1.1.

v1.1 Fixes:
  - Fixed "2 papers per sheet" overflow by tightening margins (8/8/5/5 mm)
  - Fixed compact mode to properly remove cover pages
  - Reduced line leading from 1.22x to 1.03x font size
  - Disabled headers/footers by default to maximize usable page area
  - Improved HTML detection with pre-block extraction and &nbsp; handling
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QMessageBox

from gui import run_app
from utils import setup_logging


def main() -> int:
    """Start LongBookMerger v1.1."""

    log_file = setup_logging()
    logging.info("LongBookMerger v1.1 starting. Log file: %s", log_file)
    try:
        return run_app(Path(__file__).resolve().parent)
    except Exception as exc:
        logging.exception("Fatal application error")
        QMessageBox.critical(None, "LongBookMerger v1.1", f"LongBookMerger v1.1 could not start.\n\n{exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
