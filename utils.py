"""Shared helpers for LongBookMerger."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
import zipfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator

from appdirs import user_log_dir


APP_NAME = "LongBookMerger"
SUPPORTED_EXTENSIONS = {".rpt", ".txt", ".html", ".htm", ""}


@dataclass(frozen=True)
class PreparedInput:
    """Expanded input file and the temporary directory that owns it, if any."""

    files: list[Path]
    temp_dir: Path | None = None


def setup_logging() -> Path:
    """Configure application logging and return the log file path."""

    log_dir = Path(user_log_dir(APP_NAME))
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{APP_NAME}.log"
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s",
    )
    return log_file


def log_exception(message: str) -> str:
    """Log and return a formatted traceback string."""

    details = traceback.format_exc()
    logging.error("%s\n%s", message, details)
    return details


def is_supported_report(path: Path) -> bool:
    """Return True when a file extension is accepted by the application."""

    return path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS


def collect_report_files(input_paths: list[Path]) -> PreparedInput:
    """Collect supported report files from files, folders, and ZIP archives."""

    temp_root = Path(tempfile.mkdtemp(prefix="longbookmerger_"))
    temp_used = False
    files: list[Path] = []

    for raw_path in input_paths:
        path = raw_path.expanduser().resolve()
        if path.is_dir():
            files.extend(p for p in path.rglob("*") if is_supported_report(p))
        elif path.is_file() and zipfile.is_zipfile(path):
            extract_dir = temp_root / path.stem
            extract_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(path) as archive:
                archive.extractall(extract_dir)
            temp_used = True
            files.extend(p for p in extract_dir.rglob("*") if is_supported_report(p))
        elif is_supported_report(path):
            files.append(path)

    unique_files = sorted(set(files), key=lambda item: str(item).lower())
    if temp_used:
        return PreparedInput(files=unique_files, temp_dir=temp_root)

    shutil.rmtree(temp_root, ignore_errors=True)
    return PreparedInput(files=unique_files)


@contextmanager
def prepared_inputs(input_paths: list[Path]) -> Iterator[list[Path]]:
    """Yield collected input files and delete extraction directories afterwards."""

    prepared = collect_report_files(input_paths)
    try:
        yield prepared.files
    finally:
        if prepared.temp_dir:
            shutil.rmtree(prepared.temp_dir, ignore_errors=True)


def open_file(path: Path) -> None:
    """Open a generated file with the desktop default application."""

    try:
        if sys.platform.startswith("linux"):
            subprocess.Popen(["xdg-open", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            os.startfile(path)  # type: ignore[attr-defined]
    except Exception:
        logging.warning("Could not open generated file: %s", path, exc_info=True)


def ensure_output_folder(path: Path) -> Path:
    """Create and return an output folder."""

    path.mkdir(parents=True, exist_ok=True)
    return path


ProgressCallback = Callable[[int, str], None]
