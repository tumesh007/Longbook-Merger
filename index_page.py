"""PDF index page drawing helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IndexEntry:
    """A contents entry for a report bookmark target."""

    label: str
    page_number: int
    bookmark_key: str
