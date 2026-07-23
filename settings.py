"""QSettings wrapper for persistent UI preferences."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings, QSize


class AppSettings:
    """Small typed wrapper around QSettings."""

    def __init__(self) -> None:
        self.settings = QSettings("PNBTools", "LongBookMerger")

    def value_bool(self, key: str, default: bool) -> bool:
        """Read a boolean setting."""

        value = self.settings.value(key, default)
        if isinstance(value, bool):
            return value
        return str(value).lower() in {"1", "true", "yes", "on"}

    def set_bool(self, key: str, value: bool) -> None:
        """Write a boolean setting."""

        self.settings.setValue(key, value)

    def output_folder(self) -> Path:
        """Return remembered output folder or the current home directory."""

        return Path(str(self.settings.value("output_folder", str(Path.home()))))

    def set_output_folder(self, path: Path) -> None:
        """Remember output folder."""

        self.settings.setValue("output_folder", str(path))

    def window_size(self) -> QSize:
        """Return remembered window size."""

        value = self.settings.value("window_size", QSize(980, 720))
        return value if isinstance(value, QSize) else QSize(980, 720)

    def set_window_size(self, size: QSize) -> None:
        """Remember window size."""

        self.settings.setValue("window_size", size)
