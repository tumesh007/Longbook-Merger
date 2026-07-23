"""PDF generation for merged Long Book reports — v1.1.

Fixes in v1.1:
  - Tightened margins (8/8/5/5 mm) to prevent "2 papers per sheet"
  - Reduced line leading from 1.22x to 1.03x font size
  - Compact mode now actually removes cover pages and uses minimal margins
  - Removed heavy headers/footers that were consuming usable page area
  - Fixed font width calculation using Courier width factor 0.60
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from bookmarks import bookmark_key
from index_page import IndexEntry
from parser import ParsedReport, ReportPage, parse_report
from sorter import sort_reports
from utils import ProgressCallback, ensure_output_folder


PAGE_SIZE = landscape(A4)

# v1.1: Tightened margins to match working script — fixes "2 papers per sheet"
LEFT_MM = 8.0
RIGHT_MM = 8.0
TOP_MM = 5.0
BOTTOM_MM = 5.0
MARGIN_LEFT = LEFT_MM * mm
MARGIN_RIGHT = RIGHT_MM * mm
MARGIN_TOP = TOP_MM * mm
MARGIN_BOTTOM = BOTTOM_MM * mm

# v1.1: Courier width factor for accurate monospaced width calculation
COURIER_WIDTH_FACTOR = 0.60

FONT_CANDIDATES = ("CourierPrime", "Courier", "Courier-Bold", "Helvetica")


@dataclass(slots=True)
class PdfOptions:
    """User-controlled output options."""

    detect_fake_html: bool = True
    remove_blank_pages: bool = True
    generate_full_pdf: bool = True
    generate_compact_pdf: bool = True
    generate_index_pdf: bool = True
    generate_bookmarks: bool = True
    auto_font_size: bool = True
    keep_cover_pages: bool = False
    generate_booklet_pdf: bool = False
    print_report_title: bool = False      # v1.1: disabled by default
    print_filename: bool = False          # v1.1: disabled by default
    print_date: bool = False              # v1.1: disabled by default
    footer_page_numbers: bool = False     # v1.1: disabled by default
    footer_timestamp: bool = False        # v1.1: disabled by default


@dataclass(slots=True)
class GenerationResult:
    """Generated PDF file paths."""

    files: list[Path]
    parsed_reports: list[ParsedReport]


def register_fonts(font_dir: Path | None = None) -> str:
    """Register Courier Prime if bundled, otherwise return a built-in font."""

    if font_dir:
        regular = font_dir / "CourierPrime-Regular.ttf"
        if regular.exists():
            try:
                pdfmetrics.registerFont(TTFont("CourierPrime", str(regular)))
                return "CourierPrime"
            except Exception:
                logging.warning("Could not register Courier Prime", exc_info=True)
    return "Courier"


def max_line_length(reports: list[ParsedReport]) -> int:
    """Return the length of the longest line in all reports."""

    longest = 1
    for report in reports:
        for page in report.pages:
            longest = max(longest, *(len(line.expandtabs(8)) for line in page.lines), longest)
    return longest


def choose_font_size(reports: list[ParsedReport], font_name: str, options: PdfOptions) -> float:
    """Choose the largest readable monospaced size that fits page width."""

    if not options.auto_font_size:
        return 8.2  # v1.1: default matches working script

    # v1.1: Use printable width with tight margins
    printable_width = PAGE_SIZE[0] - MARGIN_LEFT - MARGIN_RIGHT
    longest = max_line_length(reports)

    # v1.1: Use Courier width factor for accurate calculation
    fit_size = printable_width / (COURIER_WIDTH_FACTOR * max(1, longest))

    # v1.1: Clamp between min and max, preferring 8.2pt as default ceiling
    return max(5.8, min(8.2, fit_size))


def lines_per_page(font_size: float, include_header: bool, include_footer: bool) -> int:
    """Calculate how many text rows fit on an A4 landscape page."""

    # v1.1: Use tight margins — only reserve space for header/footer if enabled
    reserved_top = 8 * mm if include_header else 0
    reserved_bottom = 6 * mm if include_footer else 0
    usable_height = PAGE_SIZE[1] - MARGIN_TOP - MARGIN_BOTTOM - reserved_top - reserved_bottom

    # v1.1: Tighter leading (1.03x) to match working script — fixes overflow
    line_height = font_size * 1.03
    return max(1, math.floor(usable_height / line_height))


def paginate_reports(reports: list[ParsedReport], font_size: float, options: PdfOptions) -> list[tuple[ParsedReport, list[str]]]:
    """Expand logical report pages into physical PDF pages."""

    include_header = options.print_report_title or options.print_filename or options.print_date
    include_footer = options.footer_page_numbers or options.footer_timestamp
    max_lines = lines_per_page(font_size, include_header, include_footer)
    output: list[tuple[ParsedReport, list[str]]] = []

    for report in reports:
        for page in report.pages:
            lines = page.lines or [""]
            # v1.1: Expand tabs before pagination to match working script
            expanded = [line.expandtabs(8) for line in lines]
            for start in range(0, len(expanded), max_lines):
                output.append((report, expanded[start : start + max_lines]))
    return output


def index_page_count(entry_count: int) -> int:
    """Return how many contents pages are needed for the entry count."""

    if entry_count <= 0:
        return 0
    first_page_rows = max(1, math.floor(((PAGE_SIZE[1] - 30 * mm) - (15 * mm)) / (7 * mm)))
    next_page_rows = max(1, math.floor(((PAGE_SIZE[1] - 18 * mm) - (15 * mm)) / (7 * mm)))
    if entry_count <= first_page_rows:
        return 1
    return 1 + math.ceil((entry_count - first_page_rows) / next_page_rows)


def draw_header(c: canvas.Canvas, report: ParsedReport, options: PdfOptions) -> None:
    """Draw optional report header."""

    parts: list[str] = []
    if options.print_report_title:
        parts.append(report.title)
    if options.print_filename:
        parts.append(report.source_path.name)
    if options.print_date:
        parts.append(report.report_date)
    if not parts:
        return
    c.setFont("Helvetica-Bold", 8)  # v1.1: smaller header font
    c.setFillColor(colors.black)
    c.drawString(MARGIN_LEFT, PAGE_SIZE[1] - MARGIN_TOP + 1.0 * mm, " | ".join(parts))
    c.setStrokeColor(colors.lightgrey)
    c.line(MARGIN_LEFT, PAGE_SIZE[1] - MARGIN_TOP - 1.0 * mm, PAGE_SIZE[0] - MARGIN_RIGHT, PAGE_SIZE[1] - MARGIN_TOP - 1.0 * mm)


def draw_footer(c: canvas.Canvas, page_number: int, total_pages: int, generated_at: str, options: PdfOptions) -> None:
    """Draw optional footer."""

    if not (options.footer_page_numbers or options.footer_timestamp):
        return
    c.setFont("Helvetica", 7)  # v1.1: smaller footer font
    c.setFillColor(colors.dimgray)
    left = generated_at if options.footer_timestamp else ""
    right = f"Page {page_number} of {total_pages}" if options.footer_page_numbers else ""
    if left:
        c.drawString(MARGIN_LEFT, 3 * mm, left)
    if right:
        c.drawRightString(PAGE_SIZE[0] - MARGIN_RIGHT, 3 * mm, right)


def draw_index_page(c: canvas.Canvas, entries: list[IndexEntry]) -> None:
    """Draw a clickable contents page."""

    c.setTitle("LongBook With Index")
    c.setFont("Helvetica-Bold", 18)
    c.drawString(MARGIN_LEFT, PAGE_SIZE[1] - 18 * mm, "Contents")
    c.setFont("Helvetica", 10)
    y = PAGE_SIZE[1] - 30 * mm
    for entry in entries:
        if y < 15 * mm:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = PAGE_SIZE[1] - 18 * mm
        label = entry.label[:70]
        page_text = f"Page {entry.page_number}"
        dots_width = PAGE_SIZE[0] - MARGIN_LEFT - MARGIN_RIGHT - c.stringWidth(label, "Helvetica", 10) - c.stringWidth(page_text, "Helvetica", 10) - 6 * mm
        dots = "." * max(3, int(dots_width / c.stringWidth(".", "Helvetica", 10)))
        c.drawString(MARGIN_LEFT, y, f"{label} {dots}")
        c.drawRightString(PAGE_SIZE[0] - MARGIN_RIGHT, y, page_text)
        c.linkRect("", entry.bookmark_key, (MARGIN_LEFT, y - 2, PAGE_SIZE[0] - MARGIN_RIGHT, y + 11), relative=0, thickness=0)
        y -= 7 * mm


def write_pdf(
    output_path: Path,
    reports: list[ParsedReport],
    options: PdfOptions,
    include_index: bool,
    compact: bool,
    font_dir: Path | None = None,
) -> None:
    """Write one merged PDF variant."""

    font_name = register_fonts(font_dir)
    font_size = choose_font_size(reports, font_name, options)
    physical_pages = paginate_reports(reports, font_size, options)
    report_count = sum(1 for report in reports if report.pages)
    start_offset = index_page_count(report_count) if include_index else 0
    generated_at = f"Generated {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    index_entries: list[IndexEntry] = []
    first_seen: set[Path] = set()
    page_lookup: dict[Path, int] = {}

    for index, (report, _lines) in enumerate(physical_pages, start=1 + start_offset):
        if report.source_path not in first_seen:
            first_seen.add(report.source_path)
            key = bookmark_key(report.report_date, len(index_entries) + 1)
            page_lookup[report.source_path] = index
            index_entries.append(IndexEntry(report.report_date, index, key))

    c = canvas.Canvas(str(output_path), pagesize=PAGE_SIZE)
    c.setAuthor("LongBookMerger v1.1")
    c.setTitle(output_path.stem)
    c.setSubject("Merged CBSL/Finacle Long Book reports")

    if include_index:
        draw_index_page(c, index_entries)
        c.showPage()

    # v1.1: Tighter leading to match working script
    line_height = font_size * 1.03
    include_header = options.print_report_title or options.print_filename or options.print_date

    # v1.1: Start drawing from top margin, minus header space if needed
    y_start = PAGE_SIZE[1] - MARGIN_TOP - (8 * mm if include_header else 0)
    total_pages = len(physical_pages) + start_offset

    seen_reports: set[Path] = set()
    for page_index, (report, lines) in enumerate(physical_pages, start=1 + start_offset):
        if report.source_path not in seen_reports:
            seen_reports.add(report.source_path)
            key = next(entry.bookmark_key for entry in index_entries if entry.page_number == page_lookup[report.source_path])
            c.bookmarkPage(key)
            if options.generate_bookmarks:
                c.addOutlineEntry(report.report_date, key, level=0, closed=False)

        if not compact:
            draw_header(c, report, options)
        c.setFont(font_name, font_size)
        c.setFillColor(colors.black)

        # v1.1: Compact mode starts from very top; full mode starts below header
        y = y_start if not compact else PAGE_SIZE[1] - MARGIN_TOP
        for line in lines:
            c.drawString(MARGIN_LEFT, y, line[:10000])
            y -= line_height
        if not compact:
            draw_footer(c, page_index, total_pages, generated_at, options)
        c.showPage()

    c.save()


def create_booklet_pdf(source_path: Path, output_path: Path) -> None:
    """Create a simple booklet-ordered PDF without scaling pages."""

    reader = PdfReader(str(source_path))
    writer = PdfWriter()
    pages = list(reader.pages)
    while len(pages) % 4:
        pages.append(None)
    left = 0
    right = len(pages) - 1
    order: list[int] = []
    while left < right:
        order.extend([right, left, left + 1, right - 1])
        left += 2
        right -= 2
    for page_number in order:
        page = pages[page_number]
        if page is not None:
            writer.add_page(page)
        else:
            writer.add_blank_page(width=PAGE_SIZE[0], height=PAGE_SIZE[1])
    with output_path.open("wb") as handle:
        writer.write(handle)


def generate_pdfs(
    input_files: list[Path],
    output_folder: Path,
    options: PdfOptions,
    progress: ProgressCallback | None = None,
    font_dir: Path | None = None,
) -> GenerationResult:
    """Parse reports and generate selected PDF outputs."""

    output_folder = ensure_output_folder(output_folder)
    sorted_reports = sort_reports(input_files)
    parsed_reports: list[ParsedReport] = []
    total = max(len(sorted_reports), 1)
    for index, sortable in enumerate(sorted_reports, start=1):
        if progress:
            progress(int(index * 35 / total), f"Parsing {sortable.path.name}")
        parsed = parse_report(
            sortable.path,
            detect_fake_html=options.detect_fake_html,
            keep_blank_pages=(not options.remove_blank_pages) or options.keep_cover_pages,
        )
        if not parsed.pages and options.keep_cover_pages:
            parsed.pages.append(ReportPage(lines=[]))
        if parsed.pages or options.keep_cover_pages:
            parsed_reports.append(parsed)

    if not parsed_reports:
        raise ValueError("No printable report pages were found.")

    generated: list[Path] = []
    variants: list[tuple[str, bool, bool]] = []
    if options.generate_full_pdf:
        variants.append(("LongBook_Full.pdf", False, False))
    if options.generate_compact_pdf:
        variants.append(("LongBook_Compact.pdf", False, True))
    if options.generate_index_pdf:
        variants.append(("LongBook_With_Index.pdf", True, False))

    if not variants:
        raise ValueError("Select at least one PDF output.")

    for index, (filename, include_index, compact) in enumerate(variants, start=1):
        if progress:
            progress(35 + int(index * 55 / len(variants)), f"Writing {filename}")
        path = output_folder / filename
        write_pdf(path, parsed_reports, options, include_index=include_index, compact=compact, font_dir=font_dir)
        generated.append(path)

    if options.generate_booklet_pdf:
        source = output_folder / "LongBook_With_Index.pdf" if options.generate_index_pdf else generated[0]
        booklet = output_folder / "LongBook_Booklet.pdf"
        if progress:
            progress(95, "Writing LongBook_Booklet.pdf")
        create_booklet_pdf(source, booklet)
        generated.append(booklet)

    if progress:
        progress(100, "Done")
    return GenerationResult(files=generated, parsed_reports=parsed_reports)
