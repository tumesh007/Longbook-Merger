"""Report parsing for text and HTML CBSL/Finacle exports — v1.1.

Fixes in v1.1:
  - Added is_cover_page() detection for compact mode (matches working script)
  - Improved HTML handling with pre-block extraction and &nbsp; preservation
  - Better tab expansion (8 spaces) before line length measurement
"""

from __future__ import annotations

import html as html_lib
import logging
import re
from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup

from html_detector import is_html_file
from sorter import display_date


SEPARATOR_CHARS = set("-_=* .\t\r\n")

# v1.1: HTML sniffing pattern from working script
HTML_SNIFF_PATTERN = re.compile(
    r"<!doctype\s+html|<html[\s>]|<head[\s>]|<body[\s>]|<pre[\s>]|<table[\s>]",
    re.IGNORECASE,
)


@dataclass(slots=True)
class ReportPage:
    """A logical report page."""

    lines: list[str]


@dataclass(slots=True)
class ParsedReport:
    """Parsed report ready for PDF rendering."""

    source_path: Path
    title: str
    report_date: str
    pages: list[ReportPage]
    is_html: bool


def decode_report_bytes(data: bytes) -> str:
    """Decode report bytes with practical fallbacks used by CBSL exports."""

    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def looks_like_html(text: str) -> bool:
    """Content-sniff for fake HTML reports — matches working script logic."""
    sample = text[:4096]
    return bool(HTML_SNIFF_PATTERN.search(sample))


def html_report_to_text(text: str) -> str:
    """Convert HTML-wrapped fixed-width report back to plain text.

    v1.1: Matches working script logic:
      - Extracts <pre> blocks if present
      - Handles &nbsp; as real spaces (preserves column alignment)
      - Converts <hr> to form feeds
      - Strips scripts/styles before processing
    """
    # Prefer content inside <pre> blocks
    pre_blocks = re.findall(r"<pre[^>]*>(.*?)</pre>", text, flags=re.IGNORECASE | re.DOTALL)
    if pre_blocks:
        text = "\n\f\n".join(pre_blocks)

    # Drop script/style blocks
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", text, flags=re.IGNORECASE | re.DOTALL)

    # Convert line/block boundaries
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</(p|div|tr|li|h[1-6])>", "\n", text)
    text = re.sub(r"(?i)</td>\s*<td[^>]*>", " ", text)
    text = re.sub(r"(?i)<hr\s*/?>", "\f", text)

    # Strip remaining tags
    text = re.sub(r"<[^>]+>", "", text)

    # Decode entities
    text = html_lib.unescape(text)
    text = text.replace("\xa0", " ")  # Non-breaking spaces become real spaces
    return text


def read_text_report(path: Path) -> str:
    """Read a fixed-width report as text."""

    text = decode_report_bytes(path.read_bytes()).replace("\r\n", "\n").replace("\r", "\n")

    # v1.1: Check for fake HTML and convert if needed
    if looks_like_html(text):
        text = html_report_to_text(text)

    # v1.1: Clean printer control codes (from working script)
    cleaned = []
    for ch in text:
        o = ord(ch)
        if ch in ("\n", "\f", "\t") or o >= 32:
            cleaned.append(ch)
    return "".join(cleaned)


def read_html_report(path: Path) -> str:
    """Convert real HTML report content to plain text while preserving rows."""

    text = decode_report_bytes(path.read_bytes())

    # v1.1: First try the working script\'s robust HTML-to-text conversion
    if looks_like_html(text):
        converted = html_report_to_text(text)
        if converted.strip():
            return converted.replace("\r\n", "\n").replace("\r", "\n")

    # Fallback to BeautifulSoup for complex HTML
    soup = BeautifulSoup(text, "lxml")
    for element in soup(["script", "style", "noscript"]):
        element.decompose()
    pre = soup.find("pre")
    if pre:
        return html_lib.unescape(pre.get_text()).replace("\r\n", "\n").replace("\r", "\n")
    return soup.get_text("\n").replace("\r\n", "\n").replace("\r", "\n")


def is_blank_or_separator(lines: list[str]) -> bool:
    """Return True for pages that contain no meaningful report data."""

    meaningful = [line.strip() for line in lines if line.strip()]
    if not meaningful:
        return True
    return all(set(line) <= SEPARATOR_CHARS for line in meaningful)


def is_header_only(lines: list[str]) -> bool:
    """Heuristic for pages with only a title/header and separators."""

    meaningful = [line.strip() for line in lines if line.strip()]
    if len(meaningful) > 5:
        return False
    non_separator = [line for line in meaningful if not set(line) <= SEPARATOR_CHARS]
    if not non_separator:
        return True
    data_like = sum(any(char.isdigit() for char in line) and len(line) > 20 for line in non_separator)
    return len(non_separator) <= 2 and data_like == 0


# v1.1: Added from working script — detects cover pages for compact mode
def is_cover_page(lines: list[str]) -> bool:
    """Detect the mostly blank longbook title/cover page for compact output."""
    joined = "\n".join(lines)
    nonblank = [line.strip() for line in lines if line.strip()]
    # Report cover has the title + transaction type list but no transaction table.
    return ("L O N G B O O K" in joined and "TRAN ID" not in joined and len(nonblank) <= 16)


def split_pages(text: str, keep_blank_pages: bool) -> list[ReportPage]:
    """Split report text by form feed and remove empty/header-only pages."""

    raw_pages = text.split("\f")
    pages: list[ReportPage] = []
    for raw_page in raw_pages:
        lines = [line.rstrip() for line in raw_page.splitlines()]
        if keep_blank_pages or not (is_blank_or_separator(lines) or is_header_only(lines)):
            pages.append(ReportPage(lines=lines))
    return pages


def parse_report(path: Path, detect_fake_html: bool = True, keep_blank_pages: bool = False, compact: bool = False) -> ParsedReport:
    """Parse a report by content, not extension."""

    real_html = is_html_file(path) if detect_fake_html else path.suffix.lower() in {".html", ".htm"}
    try:
        text = read_html_report(path) if real_html else read_text_report(path)
    except OSError:
        logging.exception("Failed to read report %s", path)
        raise

    pages = split_pages(text, keep_blank_pages=keep_blank_pages)

    # v1.1: Remove cover pages when compact mode is enabled
    if compact:
        pages = [page for page in pages if not is_cover_page(page.lines)]

    if not pages:
        pages = [ReportPage(lines=[])] if keep_blank_pages else []

    return ParsedReport(
        source_path=path,
        title=path.stem,
        report_date=display_date(path),
        pages=pages,
        is_html=real_html,
    )
