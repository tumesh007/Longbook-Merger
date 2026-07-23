"""Content-based detection for real HTML files."""

from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup


HTML_MARKERS = ("<html", "<!doctype html", "<head", "<body", "</html>")


def is_html_file(path: Path, sample_size: int = 8192) -> bool:
    """Return True when a file appears to be genuine HTML.

    CBSL/Finacle sometimes writes fixed-width text into files ending in
    ``.html``. This function intentionally ignores the extension and sniffs the
    file content.
    """

    try:
        data = path.read_bytes()[:sample_size]
    except OSError:
        return False

    if b"\x00" in data:
        return False

    text = data.decode("utf-8", errors="ignore").lstrip().lower()
    if any(marker in text for marker in HTML_MARKERS):
        return True

    if "<" not in text or ">" not in text:
        return False

    soup = BeautifulSoup(text, "lxml")
    return bool(soup.find(["html", "head", "body", "table", "pre"]))
