"""PySide6 user interface for LongBookMerger — v1.1.

Fixes in v1.1:
  - Updated window title to show v1.1
  - Headers/footers disabled by default (were consuming page space)
  - Compact mode now properly removes cover pages
  - Margins tightened to prevent "2 papers per sheet" overflow
"""

from __future__ import annotations

import logging
import traceback
from pathlib import Path

from PySide6.QtCore import QMimeData, QObject, Qt, QThread, Signal, Slot
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from pdf_generator import PdfOptions, generate_pdfs
from settings import AppSettings
from utils import open_file, prepared_inputs


class GenerationWorker(QObject):
    """Background worker for parsing and PDF generation."""

    progress = Signal(int, str)
    finished = Signal(list)
    failed = Signal(str, str)

    def __init__(self, inputs: list[Path], output_folder: Path, options: PdfOptions, font_dir: Path) -> None:
        super().__init__()
        self.inputs = inputs
        self.output_folder = output_folder
        self.options = options
        self.font_dir = font_dir
        self.cancel_requested = False

    @Slot()
    def run(self) -> None:
        """Generate PDFs and emit thread-safe status signals."""

        try:
            with prepared_inputs(self.inputs) as files:
                if self.cancel_requested:
                    self.failed.emit("Cancelled", "Generation was cancelled before processing started.")
                    return
                if not files:
                    raise ValueError("No supported report files were found.")

                def progress(value: int, message: str) -> None:
                    if self.cancel_requested:
                        raise InterruptedError("Generation cancelled.")
                    self.progress.emit(value, message)

                result = generate_pdfs(files, self.output_folder, self.options, progress=progress, font_dir=self.font_dir)
            self.finished.emit([str(path) for path in result.files])
        except InterruptedError as exc:
            logging.info("Generation cancelled")
            self.failed.emit("Cancelled", str(exc))
        except Exception as exc:
            details = traceback.format_exc()
            logging.error("Generation failed\n%s", details)
            self.failed.emit(str(exc), details)

    def cancel(self) -> None:
        """Request cooperative cancellation."""

        self.cancel_requested = True


class DropListWidget(QListWidget):
    """List widget that accepts files, folders, and ZIP archives."""

    paths_dropped = Signal(list)

    def __init__(self) -> None:
        super().__init__()
        self.setAcceptDrops(True)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if self._has_paths(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragEnterEvent) -> None:
        if self._has_paths(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        paths = [Path(url.toLocalFile()) for url in urls if url.isLocalFile()]
        if paths:
            self.paths_dropped.emit(paths)
            event.acceptProposedAction()

    @staticmethod
    def _has_paths(mime_data: QMimeData) -> bool:
        return any(url.isLocalFile() for url in mime_data.urls())


class MainWindow(QMainWindow):
    """Main desktop window."""

    def __init__(self, app_dir: Path) -> None:
        super().__init__()
        self.app_dir = app_dir
        self.settings = AppSettings()
        self.worker_thread: QThread | None = None
        self.worker: GenerationWorker | None = None
        self.input_paths: list[Path] = []
        self.show_after_generation = True

        self.setWindowTitle("LongBookMerger v1.1")  # v1.1: Updated title
        icon_path = app_dir.parent / "assets" / "icon.svg"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        self.resize(self.settings.window_size())
        self.setAcceptDrops(True)
        self._build_ui()
        self._load_settings()

    def _build_ui(self) -> None:
        central = QWidget()
        outer = QVBoxLayout(central)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        title = QLabel("LongBookMerger v1.1")  # v1.1: Updated title
        title.setObjectName("TitleLabel")
        outer.addWidget(title)

        # v1.1: Added version info subtitle
        subtitle = QLabel("Fixed: 2-papers-per-sheet overflow | Compact cover-page removal")
        subtitle.setStyleSheet("color: #666; font-size: 11px;")
        outer.addWidget(subtitle)

        input_group = QGroupBox("Input")
        input_layout = QVBoxLayout(input_group)
        button_row = QHBoxLayout()
        self.add_files_button = QPushButton("Browse Files")
        self.add_folder_button = QPushButton("Browse Folder")
        self.clear_button = QPushButton("Clear")
        for button in (self.add_files_button, self.add_folder_button, self.clear_button):
            button.setMinimumHeight(40)
            button_row.addWidget(button)
        input_layout.addLayout(button_row)
        self.input_list = DropListWidget()
        self.input_list.setMinimumHeight(110)
        self.input_list.setToolTip("Drop reports, folders, or ZIP files here.")
        input_layout.addWidget(self.input_list)
        outer.addWidget(input_group)

        output_group = QGroupBox("Output Folder")
        output_layout = QHBoxLayout(output_group)
        self.output_edit = QLineEdit()
        self.output_button = QPushButton("Browse")
        self.output_button.setMinimumHeight(36)
        output_layout.addWidget(self.output_edit, 1)
        output_layout.addWidget(self.output_button)
        outer.addWidget(output_group)

        options_group = QGroupBox("Options")
        options_layout = QGridLayout(options_group)
        self.detect_fake_html = QCheckBox("Detect fake HTML")
        self.remove_blank_pages = QCheckBox("Remove blank pages")
        self.generate_full = QCheckBox("Generate Full PDF")
        self.generate_compact = QCheckBox("Generate Compact PDF")
        self.generate_index = QCheckBox("Generate Index")
        self.generate_bookmarks = QCheckBox("Generate Bookmarks")
        self.auto_font_size = QCheckBox("Auto Font Size")
        self.keep_cover_pages = QCheckBox("Keep Cover Pages")
        self.show_pdf = QCheckBox("Show PDF after generation")
        self.generate_booklet = QCheckBox("Generate Booklet PDF")
        self.print_title = QCheckBox("Print report title")
        self.print_filename = QCheckBox("Print filename")
        self.print_date = QCheckBox("Print date")
        self.footer_page_numbers = QCheckBox("Page X of Y")
        self.footer_timestamp = QCheckBox("Generation timestamp")

        checkboxes = [
            self.detect_fake_html,
            self.remove_blank_pages,
            self.generate_full,
            self.generate_compact,
            self.generate_index,
            self.generate_bookmarks,
            self.auto_font_size,
            self.keep_cover_pages,
            self.show_pdf,
            self.generate_booklet,
            self.print_title,
            self.print_filename,
            self.print_date,
            self.footer_page_numbers,
            self.footer_timestamp,
        ]
        for index, checkbox in enumerate(checkboxes):
            options_layout.addWidget(checkbox, index // 3, index % 3)
        outer.addWidget(options_group)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        outer.addWidget(self.progress)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(120)
        self.log.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        outer.addWidget(self.log, 1)

        action_row = QHBoxLayout()
        action_row.addStretch(1)
        self.generate_button = QPushButton("Generate")
        self.cancel_button = QPushButton("Cancel")
        self.generate_button.setMinimumSize(160, 46)
        self.cancel_button.setMinimumSize(120, 46)
        self.cancel_button.setEnabled(False)
        action_row.addWidget(self.generate_button)
        action_row.addWidget(self.cancel_button)
        outer.addLayout(action_row)

        self.setCentralWidget(central)

        self.add_files_button.clicked.connect(self.browse_files)
        self.add_folder_button.clicked.connect(self.browse_folder)
        self.clear_button.clicked.connect(self.clear_inputs)
        self.output_button.clicked.connect(self.browse_output)
        self.generate_button.clicked.connect(self.start_generation)
        self.cancel_button.clicked.connect(self.cancel_generation)
        self.input_list.paths_dropped.connect(self.add_inputs)

        self.setStyleSheet(
            """
            QMainWindow { background: #f5f6f8; }
            #TitleLabel { font-size: 26px; font-weight: 700; color: #20242a; }
            QGroupBox { font-weight: 600; border: 1px solid #c9ced6; border-radius: 6px; margin-top: 8px; padding-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
            QPushButton { font-size: 14px; padding: 8px 14px; border-radius: 6px; background: #2458a6; color: white; }
            QPushButton:disabled { background: #98a4b6; }
            QPushButton:hover:!disabled { background: #1c477f; }
            QLineEdit, QListWidget, QPlainTextEdit { background: white; border: 1px solid #c9ced6; border-radius: 6px; padding: 6px; }
            QCheckBox { spacing: 8px; min-height: 26px; }
            """
        )

    def _load_settings(self) -> None:
        # v1.1: Headers/footers disabled by default to fix page overflow
        defaults = {
            self.detect_fake_html: True,
            self.remove_blank_pages: True,
            self.generate_full: True,
            self.generate_compact: True,
            self.generate_index: True,
            self.generate_bookmarks: True,
            self.auto_font_size: True,
            self.keep_cover_pages: False,
            self.show_pdf: True,
            self.generate_booklet: False,
            self.print_title: False,          # v1.1: disabled by default
            self.print_filename: False,       # v1.1: disabled by default
            self.print_date: False,           # v1.1: disabled by default
            self.footer_page_numbers: False,  # v1.1: disabled by default
            self.footer_timestamp: False,     # v1.1: disabled by default
        }
        for checkbox, default in defaults.items():
            checkbox.setChecked(self.settings.value_bool(checkbox.objectName() or checkbox.text(), default))
        self.output_edit.setText(str(self.settings.output_folder()))

    def _save_settings(self) -> None:
        self.settings.set_window_size(self.size())
        self.settings.set_output_folder(Path(self.output_edit.text()).expanduser())
        for checkbox in self.findChildren(QCheckBox):
            self.settings.set_bool(checkbox.objectName() or checkbox.text(), checkbox.isChecked())

    def add_inputs(self, paths: list[Path]) -> None:
        existing = {str(path) for path in self.input_paths}
        for path in paths:
            resolved = path.expanduser()
            if str(resolved) not in existing:
                self.input_paths.append(resolved)
                self.input_list.addItem(str(resolved))
                existing.add(str(resolved))
        self.append_log(f"Added {len(paths)} input item(s).")

    @Slot()
    def browse_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Long Book reports or ZIP files",
            str(Path.home()),
            "Reports and ZIP files (*.rpt *.txt *.html *.htm *.zip);;All files (*)",
        )
        self.add_inputs([Path(path) for path in paths])

    @Slot()
    def browse_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select report folder", str(Path.home()))
        if folder:
            self.add_inputs([Path(folder)])

    @Slot()
    def browse_output(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select output folder", self.output_edit.text())
        if folder:
            self.output_edit.setText(folder)

    @Slot()
    def clear_inputs(self) -> None:
        self.input_paths.clear()
        self.input_list.clear()
        self.append_log("Input list cleared.")

    def build_options(self) -> PdfOptions:
        """Build PDF options from UI state."""

        return PdfOptions(
            detect_fake_html=self.detect_fake_html.isChecked(),
            remove_blank_pages=self.remove_blank_pages.isChecked(),
            generate_full_pdf=self.generate_full.isChecked(),
            generate_compact_pdf=self.generate_compact.isChecked(),
            generate_index_pdf=self.generate_index.isChecked(),
            generate_bookmarks=self.generate_bookmarks.isChecked(),
            auto_font_size=self.auto_font_size.isChecked(),
            keep_cover_pages=self.keep_cover_pages.isChecked(),
            generate_booklet_pdf=self.generate_booklet.isChecked(),
            print_report_title=self.print_title.isChecked(),
            print_filename=self.print_filename.isChecked(),
            print_date=self.print_date.isChecked(),
            footer_page_numbers=self.footer_page_numbers.isChecked(),
            footer_timestamp=self.footer_timestamp.isChecked(),
        )

    @Slot()
    def start_generation(self) -> None:
        if not self.input_paths:
            QMessageBox.warning(self, "No input", "Add at least one report, folder, or ZIP file.")
            return
        output_folder = Path(self.output_edit.text()).expanduser()
        if not output_folder:
            QMessageBox.warning(self, "No output folder", "Choose an output folder.")
            return

        self._save_settings()
        self.progress.setValue(0)
        self.set_busy(True)
        self.append_log("Starting generation v1.1...")
        self.worker_thread = QThread(self)
        self.worker = GenerationWorker(self.input_paths, output_folder, self.build_options(), self.app_dir.parent / "fonts")
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.failed.connect(self.on_failed)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.failed.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    @Slot()
    def cancel_generation(self) -> None:
        if self.worker:
            self.worker.cancel()
            self.append_log("Cancellation requested.")

    @Slot(int, str)
    def on_progress(self, value: int, message: str) -> None:
        self.progress.setValue(value)
        self.append_log(message)

    @Slot(list)
    def on_finished(self, files: list[str]) -> None:
        self.set_busy(False)
        self.progress.setValue(100)
        self.append_log("Generated files:")
        for file_path in files:
            self.append_log(f"  {file_path}")
        if self.show_pdf.isChecked() and files:
            open_file(Path(files[-1]))
        QMessageBox.information(self, "Generation complete", f"Created {len(files)} PDF file(s) with v1.1 fixes.")

    @Slot(str, str)
    def on_failed(self, message: str, details: str) -> None:
        self.set_busy(False)
        self.append_log(message)
        logging.error(details)
        QMessageBox.critical(self, "LongBookMerger v1.1", f"{message}\n\nFull details were written to LongBookMerger.log.")

    def set_busy(self, busy: bool) -> None:
        self.generate_button.setEnabled(not busy)
        self.cancel_button.setEnabled(busy)
        self.add_files_button.setEnabled(not busy)
        self.add_folder_button.setEnabled(not busy)
        self.clear_button.setEnabled(not busy)

    def append_log(self, message: str) -> None:
        self.log.appendPlainText(message)
        logging.info(message)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if DropListWidget._has_paths(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        paths = [Path(url.toLocalFile()) for url in event.mimeData().urls() if url.isLocalFile()]
        if paths:
            self.add_inputs(paths)
            event.acceptProposedAction()

    def closeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self._save_settings()
        super().closeEvent(event)


def run_app(app_dir: Path) -> int:
    """Run the Qt application."""

    app = QApplication([])
    app.setApplicationName("LongBookMerger")
    app.setApplicationVersion("1.1")  # v1.1: Set version
    app.setOrganizationName("PNBTools")
    window = MainWindow(app_dir)
    window.show()
    return app.exec()
