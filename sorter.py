"""Filename date detection and chronological sorting."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


DATE_PATTERNS = (
    re.compile(r"(?P<d>\d{2})[-_.](?P<m>\d{2})[-_.](?P<y>\d{4})"),
    re.compile(r"(?P<y>\d{4})(?P<m>\d{2})(?P<d>\d{2})"),
    re.compile(r"(?P<d>\d{2})(?P<m>\d{2})(?P<y>\d{4})"),
)


@dataclass(frozen=True)
class SortableReport:
    """A file with an optional date extracted from its filename."""

    path: Path
    detected_date: date | None


def detect_date_from_filename(path: Path) -> date | None:
    """Detect dates such as 17-05-2026, 17052026, or 20260517."""

    name = path.stem
    for pattern in DATE_PATTERNS:
        for match in pattern.finditer(name):
            try:
                return datetime(
                    int(match.group("y")),
                    int(match.group("m")),
                    int(match.group("d")),
                ).date()
            except ValueError:
                continue
    return None


def display_date(path: Path) -> str:
    """Return a user-facing report date or the filename stem."""

    detected = detect_date_from_filename(path)
    return detected.strftime("%d-%m-%Y") if detected else path.stem


def sort_reports(paths: list[Path]) -> list[SortableReport]:
    """Sort reports chronologically, then by filename for stable output."""

    reports = [SortableReport(path=path, detected_date=detect_date_from_filename(path)) for path in paths]
    return sorted(
        reports,
        key=lambda report: (
            report.detected_date is None,
            report.detected_date or date.max,
            report.path.name.lower(),
        ),
    )
