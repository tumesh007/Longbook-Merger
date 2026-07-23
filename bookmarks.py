"""Bookmark helpers for ReportLab canvases."""

from __future__ import annotations

import re


def bookmark_key(label: str, index: int) -> str:
    """Create a stable ReportLab bookmark key."""

    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", label).strip("_")
    return f"report_{index}_{cleaned or 'untitled'}"
