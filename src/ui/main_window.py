# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright © 2026 Aries223 (https://github.com/aries223)
import logging
import os
import shutil
import threading
import time

from PyQt6.QtCore import QByteArray, Qt, QTimer, QUrl
from PyQt6.QtGui import QColor, QDesktopServices, QFontMetrics, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QFileDialog, QHBoxLayout, QHeaderView,
    QLabel, QMainWindow, QMenu, QMenuBar, QMessageBox, QProgressBar,
    QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from compression.base_compressor import _sanitise_for_log
from compression.gif_compressor import GifCompressor
from compression.jpeg_compressor import JpegCompressor
from compression.png_compressor import PngCompressor
from compression.webp_compressor import WebpCompressor
from utils.file_utils import get_file_format, get_file_size, get_image_dimensions
from utils.preferences import Preferences
from utils.signals import signals

logger = logging.getLogger(__name__)

# External CLI tools that must be present for compression to be available.
# Stored as a module-level constant so _check_tool_availability and
# _set_compression_running always refer to the same canonical set.
_REQUIRED_TOOLS = ("jpegoptim", "oxipng", "gifsicle", "cwebp")

# Foreground colour applied to "Saved" cells when compression increased file
# size. Slightly lighter than pure red so it remains readable on dark themes.
_NEGATIVE_SAVINGS_COLOR = QColor(220, 50, 50)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mountaineer")

        self.preferences = Preferences()
        window_settings = self.preferences.get_main_window_settings()

        self.resize(window_settings['width'], window_settings['height'])
        # Enforce a sensible minimum so the UI is never unusable.
        self.setMinimumSize(650, 400)
        if window_settings['x'] is not None and window_settings['y'] is not None:
            x, y = window_settings['x'], window_settings['y']
            screen = QApplication.primaryScreen()
            if screen and screen.availableGeometry().contains(x, y):
                self.move(x, y)

        self.current_preferences = self.preferences.load_preferences()
        self.file_list = []

        # ── Menu bar ──────────────────────────────────────────────────────────
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # File menu
        file_menu = self.menu_bar.addMenu("File")
        self.add_files_action = file_menu.addAction("Add Files...")
        self.add_files_action.setShortcut(QKeySequence("Ctrl+O"))
        self.add_folder_action = file_menu.addAction("Add Folder...")
        self.add_folder_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))

        self.add_files_action.triggered.connect(self.add_files)
        self.add_folder_action.triggered.connect(self.add_folder)
        exit_action.triggered.connect(self.close)

        # Edit menu
        self.edit_menu = self.menu_bar.addMenu("Edit")
        self.remove_action = self.edit_menu.addAction("Remove")
        self.clear_action = self.edit_menu.addAction("Clear")
        select_all_action = self.edit_menu.addAction("Select All")
        select_all_action.setShortcut(QKeySequence("Ctrl+A"))
        self.preferences_action = self.edit_menu.addAction("Preferences...")
        self.preferences_action.setShortcut(QKeySequence("Ctrl+,"))

        self.remove_action.triggered.connect(self.remove_selected_files)
        self.clear_action.triggered.connect(self.clear_file_list)
        select_all_action.triggered.connect(self.select_all_files)
        self.preferences_action.triggered.connect(self.show_preferences)

        # View menu
        view_menu = self.menu_bar.addMenu("View")
        statusbar_action = view_menu.addAction("Toggle Status Bar")
        statusbar_action.triggered.connect(self.toggle_status_bar)

        # Help menu
        help_menu = self.menu_bar.addMenu("Help")
        documentation_action = help_menu.addAction("Documentation")
        help_menu.addSeparator()
        about_action = help_menu.addAction("About Mountaineer")
        documentation_action.triggered.connect(self.open_documentation)
        about_action.triggered.connect(self.show_about_dialog)

        # ── Button bar ────────────────────────────────────────────────────────
        self.button_bar = QWidget()
        self.button_bar_layout = QHBoxLayout()
        self.button_bar.setLayout(self.button_bar_layout)
        self.button_bar_layout.setContentsMargins(0, 0, 0, 0)

        self.add_files_button = QPushButton("Add Files")
        self.clear_list_button = QPushButton("Clear File List")
        self.preferences_button = QPushButton("Preferences")

        self.add_files_button.clicked.connect(self.add_files)
        self.clear_list_button.clicked.connect(self.clear_file_list)
        self.preferences_button.clicked.connect(self.show_preferences)

        self._set_button_width_with_padding(self.add_files_button, 40)
        self._set_button_width_with_padding(self.clear_list_button, 40)
        self._set_button_width_with_padding(self.preferences_button, 40)

        self.button_bar_layout.addWidget(self.add_files_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.button_bar_layout.addSpacing(8)
        self.button_bar_layout.addWidget(self.clear_list_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.button_bar_layout.addStretch()
        self.button_bar_layout.addWidget(self.preferences_button, alignment=Qt.AlignmentFlag.AlignLeft)

        # ── File list table ───────────────────────────────────────────────────
        self.file_list_widget = QTableWidget()
        self.file_list_widget.setColumnCount(6)
        headers = ["File Name", "Format", "Dimensions", "Size", "Compressed", "Saved"]
        self.file_list_widget.setHorizontalHeaderLabels(headers)
        self.file_list_widget.setSortingEnabled(True)

        header = self.file_list_widget.horizontalHeader()
        # setStretchLastSection(True) pins the right edge of the Saved column to
        # the right edge of the table viewport so the header row always spans the
        # full table width.  Leaving it at the Qt default of True would also work
        # here, but the explicit call documents the intent and prevents a future
        # maintainer from accidentally setting it to False, which would leave a
        # blank gap on the right.
        header.setStretchLastSection(True)
        # Global safety-net minimum; per-column minimums are enforced in
        # _on_column_resized based on the header label text width.
        header.setMinimumSectionSize(40)
        for i in range(self.file_list_widget.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)

        # Compute per-column minimum widths from the header font metrics so that
        # no column can ever be dragged narrower than its own label text.
        _HEADER_H_PADDING = 24  # 12 px each side
        _header_font_metrics = QFontMetrics(header.font())
        _header_labels = ["File Name", "Format", "Dimensions", "Size", "Compressed", "Saved"]
        self._column_min_widths = [
            _header_font_metrics.horizontalAdvance(label) + _HEADER_H_PADDING
            for label in _header_labels
        ]

        # Initial widths for columns 0–4; column 5 (Saved) auto-fills the rest
        # via setStretchLastSection.  File Name is given the most space to
        # comfortably display long filenames.
        header.resizeSection(0, 260)  # File Name
        header.resizeSection(1, 65)   # Format
        header.resizeSection(2, 100)  # Dimensions
        header.resizeSection(3, 60)   # Size
        header.resizeSection(4, 92)   # Compressed
        # Column 5 (Saved) is not assigned here; setStretchLastSection handles it.

        # Reentrancy guard for _on_column_resized.  Also held True during
        # restoreState() to suppress the flood of sectionResized signals Qt
        # fires internally while applying the blob.
        self._enforcing_column_size = False
        header.sectionResized.connect(self._on_column_resized)

        # Restore previously saved column widths if present.
        saved_state = self.current_preferences.get('column_header_state')
        if saved_state:
            self._enforcing_column_size = True
            try:
                header.restoreState(QByteArray.fromBase64(saved_state.encode()))
            finally:
                self._enforcing_column_size = False

            # restoreState overwrites the resize modes stored in the blob.
            # Re-assert the required modes so a stale or corrupt blob cannot
            # leave the header in an unexpected state.
            for i in range(self.file_list_widget.columnCount()):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
            header.setStretchLastSection(True)

            # Clamp any restored width that is below its per-column minimum
            # (handles a hand-edited or version-mismatched prefs file).
            for i in range(self.file_list_widget.columnCount() - 1):  # exclude stretch col
                current = header.sectionSize(i)
                if current < self._column_min_widths[i]:
                    header.resizeSection(i, self._column_min_widths[i])

        self.file_list_widget.setAcceptDrops(True)
        self.file_list_widget.viewport().setAcceptDrops(True)
        # DropOnly prevents the table's built-in InternalMove drag mode from
        # conflicting with the window-level dropEvent handler.
        self.file_list_widget.setDragDropMode(QTableWidget.DragDropMode.DropOnly)

        self.file_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list_widget.customContextMenuRequested.connect(self.show_context_menu)

        # Delete key removes selected rows (scoped to the table widget)
        delete_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Delete), self.file_list_widget)
        delete_shortcut.activated.connect(self.remove_selected_files)

        # ── Info label ────────────────────────────────────────────────────────
        self.info_widget = QLabel("0 files")
        self.info_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # ── Control widget ────────────────────────────────────────────────────
        self.control_widget = QWidget()
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)

        self.compress_button = QPushButton("Compress Images")
        quit_button = QPushButton("Quit")

        self.compress_button.clicked.connect(self.compress_images)
        quit_button.clicked.connect(self.close)

        self._set_button_style(self.compress_button)
        self._set_button_style(quit_button)

        control_layout.addWidget(self.compress_button, alignment=Qt.AlignmentFlag.AlignLeft)
        control_layout.addStretch()
        control_layout.addWidget(quit_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.control_widget.setLayout(control_layout)

        # ── Status bar ────────────────────────────────────────────────────────
        status_bar_widget = QWidget()
        status_bar_layout = QHBoxLayout()

        self.status_label = QLabel("Ready", self)
        self.status_bar_visible = True

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)

        status_bar_layout.addWidget(self.status_label, 60)
        status_bar_layout.addWidget(self.progress_bar, 40)

        self.status_bar_widget = status_bar_widget
        status_bar_widget.setLayout(status_bar_layout)

        # ── Main layout ───────────────────────────────────────────────────────
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.menu_bar)
        main_layout.addWidget(self.button_bar)
        main_layout.addWidget(self.file_list_widget, stretch=1)
        main_layout.addWidget(self.info_widget)
        main_layout.addWidget(self.control_widget)

        if self.status_bar_visible:
            main_layout.addWidget(status_bar_widget)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # ── Signal connections ────────────────────────────────────────────────
        signals.progress_updated.connect(self._update_progress)
        signals.status_updated.connect(self._safe_update_status)
        signals.compression_complete.connect(self._on_compression_complete)
        signals.compression_result_updated.connect(self._update_compression_result)

        self.file_list_widget.selectionModel().selectionChanged.connect(
            self._update_remove_menu_text
        )

        # Defer the tool-availability check until after the window has been
        # shown so that the QMessageBox has a fully visible parent behind it.
        QTimer.singleShot(0, self._check_tool_availability)

    # ── Tool availability ─────────────────────────────────────────────────────

    def _check_tool_availability(self):
        """Check that all required tools are installed; disable Compress if any are missing."""
        missing = [
            t for t in _REQUIRED_TOOLS
            if not shutil.which(t)
        ]
        if missing:
            tool_list = " and ".join(missing)
            install_hints = "\n".join(
                f"  \u2022 {t}: sudo dnf install {t}  (or equivalent for your distro)"
                for t in missing
            )
            QMessageBox.warning(
                self,
                "Missing Tools",
                f"The following required tool(s) are not installed:\n\n{tool_list}\n\n"
                f"Install them before compressing:\n{install_hints}",
            )
            self.compress_button.setEnabled(False)

    def _set_compression_running(self, running):
        """Enable or disable controls that must not be used during compression."""
        enabled = not running
        self.add_files_button.setEnabled(enabled)
        self.clear_list_button.setEnabled(enabled)
        self.preferences_button.setEnabled(enabled)
        self.add_files_action.setEnabled(enabled)
        self.add_folder_action.setEnabled(enabled)
        self.remove_action.setEnabled(enabled)
        self.clear_action.setEnabled(enabled)
        self.preferences_action.setEnabled(enabled)
        # Disable table sorting so row indices remain stable during compression
        self.file_list_widget.setSortingEnabled(enabled)
        if enabled:
            # Re-enable Compress only when every required tool is present.
            if all(shutil.which(t) for t in _REQUIRED_TOOLS):
                self.compress_button.setEnabled(True)
        else:
            self.compress_button.setEnabled(False)

    # ── Button / layout helpers ────────────────────────────────────────────────

    def _set_button_style(self, button):
        """Set consistent style for control-row buttons."""
        font_metrics = QFontMetrics(QApplication.font())
        text_width = font_metrics.horizontalAdvance(button.text())
        total_width = max(text_width + 40, 120)
        button.setMinimumWidth(total_width)
        button.setMaximumWidth(total_width)

    def _set_button_width_with_padding(self, button, padding):
        """Set button width based on text width plus padding on each side."""
        font_metrics = QFontMetrics(QApplication.font())
        text_width = font_metrics.horizontalAdvance(button.text())
        total_width = max(text_width + padding * 2, 120)
        button.setMinimumWidth(total_width)
        button.setMaximumWidth(total_width)

    def _on_column_resized(self, logical_index, old_size, new_size):
        """Enforce per-column minimum widths and prevent columns from pushing
        Saved (the stretch column) off the right edge of the viewport.

        Called via the sectionResized signal.  The _enforcing_column_size flag
        prevents the resizeSection call inside this handler from re-entering.
        Column 5 (Saved) is the stretch column and is owned by Qt — never
        attempt to resize it here.
        """
        if self._enforcing_column_size:
            return
        # The stretch column (col 5) is managed by Qt; never attempt to resize it.
        if logical_index >= 5:
            return

        header = self.file_list_widget.horizontalHeader()
        col_min = self._column_min_widths[logical_index]

        # Lower bound: column must be at least as wide as its header label text.
        clamped = max(new_size, col_min)

        # Upper bound: prevent this column from growing so wide that the
        # auto-stretched Saved column (col 5) drops below its own minimum.
        viewport_width = self.file_list_widget.viewport().width()
        other_fixed = sum(
            header.sectionSize(i) for i in range(5) if i != logical_index
        )
        saved_min = self._column_min_widths[5]
        max_allowed = viewport_width - other_fixed - saved_min
        clamped = min(clamped, max(col_min, max_allowed))

        if clamped != new_size:
            self._enforcing_column_size = True
            try:
                header.resizeSection(logical_index, clamped)
            finally:
                self._enforcing_column_size = False

    # ── Window events ──────────────────────────────────────────────────────────

    def closeEvent(self, event):
        """Save main window geometry and column layout when closing."""
        prefs = self.preferences.load_preferences()

        x, y, w, h = self.x(), self.y(), self.width(), self.height()
        # Only update the stored position if it looks like a real screen
        # location.  On some Wayland compositors QWidget.x()/y() always returns
        # 0; saving (0, 0) would move the window to the screen corner on the
        # next launch instead of letting the compositor place it naturally.
        screen = QApplication.primaryScreen()
        if screen and not (x == 0 and y == 0) and screen.availableGeometry().contains(x, y):
            prefs['main_window_x'] = x
            prefs['main_window_y'] = y
        prefs['main_window_width'] = w
        prefs['main_window_height'] = h

        header_state = self.file_list_widget.horizontalHeader().saveState()
        prefs['column_header_state'] = header_state.toBase64().data().decode()

        self.preferences.save_preferences(prefs)
        super().closeEvent(event)

    # ── Drag-and-drop ──────────────────────────────────────────────────────────

    def dragEnterEvent(self, event):
        """Accept drag events that contain URLs."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handle drop events, recursing into dropped directories."""
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        urls = [url.toLocalFile() for url in event.mimeData().urls()]
        processed_files = 0
        skipped_files = 0

        self.file_list_widget.setSortingEnabled(False)
        for url in urls:
            added, skipped = self._process_dropped_url(url)
            processed_files += added
            skipped_files += skipped
        self.file_list_widget.setSortingEnabled(True)

        if processed_files > 0 or skipped_files > 0:
            message = f"{processed_files} files added to the list"
            if skipped_files > 0:
                message += f", {skipped_files} incompatible files skipped"
            self.status_label.setText(message)
        else:
            self.status_label.setText("No valid files found in drop")

        event.acceptProposedAction()

    def _process_dropped_url(self, url: str) -> tuple:
        """Process a single dropped URL and return ``(processed_count, skipped_count)``.

        Handles the three cases — regular file, directory, and everything else —
        and wraps the entire operation in a broad exception guard so that one
        bad path cannot abort the rest of the drop.

        Args:
            url: Local filesystem path decoded from the dropped URL.

        Returns:
            A ``(processed_count, skipped_count)`` tuple reflecting the files
            accepted and rejected for this URL.
        """
        try:
            if os.path.isfile(url):
                success, is_skipped = self._try_add_file_to_list(url)
                if success:
                    return 1, 0
                return 0, is_skipped
            if os.path.isdir(url):
                return self._process_dropped_dir(url)
            # Path exists but is neither a regular file nor a directory (e.g. a
            # device node or a broken symlink resolved to nothing).
            return 0, 1
        except Exception as e:
            logger.warning(
                "Error processing dropped URL %s: %s", _sanitise_for_log(url), e
            )
            return 0, 1

    def _process_dropped_dir(self, dir_path: str) -> tuple:
        """Walk *dir_path* recursively and add every supported image file found.

        Args:
            dir_path: Absolute path to the directory to traverse.

        Returns:
            A ``(processed_count, skipped_count)`` tuple reflecting the files
            accepted and rejected during the walk.
        """
        processed_files = 0
        skipped_files = 0
        for root, _dirs, files in os.walk(dir_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                success, is_skipped = self._try_add_file_to_list(file_path)
                if success:
                    processed_files += 1
                else:
                    skipped_files += is_skipped
        return processed_files, skipped_files

    # ── File list helpers ──────────────────────────────────────────────────────

    def _is_supported_image(self, file_path):
        """Return True if the file is a supported image format (JPEG, PNG, GIF, or WEBP)."""
        try:
            return get_file_format(file_path) in ("JPEG", "PNG", "GIF", "WEBP")
        except Exception as e:
            logger.warning("Could not determine format for %s: %s", _sanitise_for_log(file_path), e)
            return False

    def _try_add_file_to_list(self, file_path):
        """Try to add a file to the list.

        Resolves the image format once here and passes it through to
        add_file_to_list to avoid a redundant Pillow open call.

        Returns a (success, is_skipped) tuple where is_skipped is 1 when the
        file is rejected (wrong format or invalid path) and 0 on success.
        """
        if os.path.islink(file_path):
            logger.warning("Skipping symlink: %s", _sanitise_for_log(file_path))
            return False, 1

        # Reject filenames that start with a hyphen.  Such names can be
        # misinterpreted as CLI flags by external tools (e.g. cwebp) that do
        # not support POSIX end-of-options ("--") in the required position.
        # This upstream guard ensures no compressor ever receives such a path.
        if os.path.basename(file_path).startswith("-"):
            logger.warning(
                "Skipping file with leading hyphen in name: %s",
                _sanitise_for_log(file_path),
            )
            return False, 1

        if not os.path.isfile(file_path):
            return False, 1

        try:
            format_str = get_file_format(file_path)
            if format_str not in ("JPEG", "PNG", "GIF", "WEBP"):
                return False, 1

            success = self.add_file_to_list(file_path, format_str=format_str)
            return success, 0
        except Exception:
            logger.exception("Error adding file %s", _sanitise_for_log(file_path))
            return False, 1

    def add_files(self):
        """Open a file dialog and add selected image files to the list."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Add Files", "", "Image Files (*.jpg *.jpeg *.png *.gif *.webp);;All Files (*)"
        )
        if files:
            added_count = 0
            skipped_count = 0

            self.file_list_widget.setSortingEnabled(False)
            for file_path in files:
                success, is_skipped = self._try_add_file_to_list(file_path)
                if success:
                    added_count += 1
                else:
                    skipped_count += is_skipped
            self.file_list_widget.setSortingEnabled(True)

            message = f"Added {added_count} files to the list"
            if skipped_count > 0:
                message += f", {skipped_count} incompatible files skipped"
            self.status_label.setText(message)

    def add_folder(self):
        """Open a folder dialog and recursively add supported images to the list."""
        folder_path = QFileDialog.getExistingDirectory(
            self, "Add Folder", "", QFileDialog.Option.ShowDirsOnly
        )
        if folder_path:
            added_count = 0
            skipped_count = 0

            self.file_list_widget.setSortingEnabled(False)
            for root, dirs, files in os.walk(folder_path):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    success, is_skipped = self._try_add_file_to_list(file_path)
                    if success:
                        added_count += 1
                    else:
                        skipped_count += is_skipped
            self.file_list_widget.setSortingEnabled(True)

            message = f"Added {added_count} files from folder to the list"
            if skipped_count > 0:
                message += f", {skipped_count} incompatible files skipped"
            self.status_label.setText(message)

    def add_file_to_list(self, file_path, format_str=None):
        """Add a validated image file to the table widget and internal list.

        Args:
            file_path: Absolute path to the image file.
            format_str: Pre-resolved format string ('JPEG', 'PNG', 'GIF', or
                'WEBP'). When provided the Pillow format-detection call is
                skipped, avoiding a redundant file open.  When None the format
                is resolved here.
        """
        try:
            if format_str is None:
                format_str = get_file_format(file_path)
            dimensions = get_image_dimensions(file_path)
            size = get_file_size(file_path)

            row_count = self.file_list_widget.rowCount()
            self.file_list_widget.insertRow(row_count)

            file_name_item = QTableWidgetItem(os.path.basename(file_path))
            file_name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            # Store the full path so we can look up files after sorting
            file_name_item.setData(Qt.ItemDataRole.UserRole, file_path)
            self.file_list_widget.setItem(row_count, 0, file_name_item)

            for col, text in enumerate((format_str, dimensions, size, "", ""), start=1):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.file_list_widget.setItem(row_count, col, item)

            self.file_list.append(file_path)

            self.update_info_widget()
            self.reset_progress_bar()

            return True

        except Exception:
            logger.exception("Failed to add file to list: %s", _sanitise_for_log(file_path))
            return False

    def clear_file_list(self):
        """Clear all files from the table and internal list."""
        self.file_list_widget.setRowCount(0)
        self.file_list = []
        self.update_info_widget()
        self.reset_progress_bar()
        self.status_label.setText("Ready")

    def update_info_widget(self):
        """Update the file count label."""
        try:
            count = len(self.file_list)
            self.info_widget.setText(f"{count} file{'s' if count != 1 else ''}")
        except Exception:
            logger.exception("Error updating info widget")
            self.info_widget.setText("Error calculating file count")

    def show_preferences(self):
        """Show the Preferences dialog."""
        from ui.preferences_dialog import PreferencesDialog
        dialog = PreferencesDialog(self)

        window_settings = self.preferences.get_prefs_dialog_settings()
        dialog.resize(window_settings['width'], window_settings['height'])
        # Always open centered over the main window.
        main_geo = self.geometry()
        dialog.move(
            main_geo.x() + (main_geo.width() - dialog.width()) // 2,
            main_geo.y() + (main_geo.height() - dialog.height()) // 2,
        )

        if dialog.exec():
            self.current_preferences = dialog.current_preferences

    # ── Compression ────────────────────────────────────────────────────────────

    def compress_images(self):
        """Start background compression of all files in the list."""
        if not self.file_list:
            signals.status_updated.emit("Error: No files selected")
            return

        # Optional one-time overwrite warning with a verb-labelled action
        # button so the destructive intent is unambiguous.
        if self.current_preferences.get('warn_before_overwrite', True):
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Overwrite Warning")
            msg.setText(
                "Files will be compressed and overwritten in place.\n"
                "This cannot be undone."
            )
            dont_show = QCheckBox("Don't show again")
            msg.setCheckBox(dont_show)
            compress_btn = msg.addButton("Compress", QMessageBox.ButtonRole.AcceptRole)
            cancel_btn = msg.addButton(QMessageBox.StandardButton.Cancel)
            msg.setDefaultButton(cancel_btn)
            msg.setEscapeButton(cancel_btn)

            msg.exec()
            if msg.clickedButton() != compress_btn:
                return

            if dont_show.isChecked():
                prefs = self.preferences.load_preferences()
                prefs['warn_before_overwrite'] = False
                self.preferences.save_preferences(prefs)
                self.current_preferences['warn_before_overwrite'] = False

        total_files = len(self.file_list)
        signals.status_updated.emit(f"Starting compression of {total_files} files...")
        self.progress_bar.setValue(0)

        # Build the snapshot by iterating the table's current visual row order
        # and reading each path from UserRole.  This is correct regardless of
        # how the user has sorted the table, because visual row i corresponds
        # to the row-i item — not necessarily file_list[i].
        snapshot = []
        for i in range(self.file_list_widget.rowCount()):
            path_item = self.file_list_widget.item(i, 0)
            size_item = self.file_list_widget.item(i, 3)
            if path_item:
                snapshot.append({
                    'path': path_item.data(Qt.ItemDataRole.UserRole),
                    'original_size_text': size_item.text() if size_item else "0 B",
                    'row_index': i,
                })

        self._set_compression_running(True)

        compression_thread = threading.Thread(
            target=self._run_compression,
            args=(snapshot, total_files),
            daemon=True,
        )
        compression_thread.start()

    def _update_progress(self, progress):
        """Update progress bar safely from the main thread."""
        self.progress_bar.setValue(progress)

    def _safe_update_status(self, message):
        """Update status label in a thread-safe manner via signal."""
        if not self.isVisible():
            return
        try:
            self.status_label.setText(message)
        except RuntimeError:
            pass

    def _on_compression_complete(self, message):
        """Handle the compression_complete signal: update status and re-enable controls."""
        self._safe_update_status(message)
        self._set_compression_running(False)

    def _compress_file_by_format(
        self,
        file_path: str,
        format_str: str,
        prefs: dict,
    ) -> tuple:
        """Instantiate the correct compressor and run it for *file_path*.

        Dispatches on *format_str* (as returned by ``get_file_format``) to the
        appropriate ``XxxCompressor`` subclass, forwarding the relevant
        preference keys.  When the format is not recognised the method logs a
        warning, emits a status signal, and returns ``(None, False)`` so the
        caller can increment its failure counter without any further branching.

        Args:
            file_path: Absolute path to the image file to compress.
            format_str: Upper-case format token, e.g. ``"JPEG"``, ``"PNG"``.
            prefs: Snapshot of the current user preferences dict.

        Returns:
            A ``(compressor, success)`` tuple where *compressor* is the
            ``BaseCompressor`` instance used (or ``None`` for unsupported
            formats) and *success* is the ``bool`` returned by
            ``compress_file()``.
        """
        filename = os.path.basename(file_path)

        if format_str == "JPEG":
            compressor = JpegCompressor()
            success = compressor.compress_file(
                file_path,
                None,
                lossless=prefs['lossless_compression'],
                strip_metadata=prefs['strip_metadata'],
                jpeg_quality=prefs['jpeg_compression_level'],
            )
        elif format_str == "PNG":
            compressor = PngCompressor()
            success = compressor.compress_file(
                file_path,
                None,
                lossless=prefs['lossless_compression'],
                strip_metadata=prefs['strip_metadata'],
                png_quality=prefs['png_compression_level'],
            )
        elif format_str == "GIF":
            compressor = GifCompressor()
            success = compressor.compress_file(
                file_path, None,
                lossless=prefs['lossless_compression'],
                strip_metadata=prefs['strip_metadata'],
                # Fix L: default matches DEFAULT_PREFERENCES (20), not the
                # stale placeholder value of 40 that was here before.
                gif_lossy_level=prefs.get('gif_lossy_level', 20),
                resize_enabled=prefs.get('gif_resize_enabled', False),
                resize_mode=prefs.get('gif_resize_mode', 'resize'),
                resize_width=prefs.get('gif_resize_width', 0),
                resize_height=prefs.get('gif_resize_height', 0),
                scale_x=prefs.get('gif_scale_x', 1.0),
                scale_y=prefs.get('gif_scale_y', 0.0),
                colors_enabled=prefs.get('gif_colors_enabled', False),
                colors_num=prefs.get('gif_colors_num', 256),
                dither_enabled=prefs.get('gif_dither_enabled', False),
                dither_method=prefs.get('gif_dither_method', 'floyd-steinberg'),
                remove_frames_enabled=prefs.get('gif_remove_frames_enabled', False),
                remove_frames_n=prefs.get('gif_remove_frames_n', 2),
                remove_frames_offset=prefs.get('gif_remove_frames_offset', 0),
                loopcount_enabled=prefs.get('gif_loopcount_enabled', False),
                loopcount_forever=prefs.get('gif_loopcount_forever', True),
                loopcount_value=prefs.get('gif_loopcount_value', 1),
                delay_enabled=prefs.get('gif_delay_enabled', False),
                delay_value=prefs.get('gif_delay_value', 10),
                optimize_enabled=prefs.get('gif_optimize_enabled', False),
                optimize_level=prefs.get('gif_optimize_level', 2),
                optimize_keep_empty=prefs.get('gif_optimize_keep_empty', False),
                unoptimize_enabled=prefs.get('gif_unoptimize_enabled', False),
            )
        elif format_str == "WEBP":
            compressor = WebpCompressor()
            success = compressor.compress_file(
                file_path,
                None,
                lossless=prefs['lossless_compression'],
                strip_metadata=prefs['strip_metadata'],
                webp_compression_level=prefs.get('webp_compression_level', 80),
            )
        else:
            logger.warning(
                "Skipped %s: unsupported format %s",
                _sanitise_for_log(file_path),
                _sanitise_for_log(format_str),
            )
            signals.status_updated.emit(
                f"Warning: {filename} skipped (unsupported format)"
            )
            return None, False

        return compressor, success

    def _emit_compression_result(
        self,
        file_path: str,
        original_size_text: str,
        row_index: int,
        compressor,
        success: bool,
    ) -> bool:
        """Emit the appropriate signal after a single-file compression attempt.

        On success the method calculates the savings percentage, then emits
        ``compression_result_updated``.  On failure it reads
        ``compressor.last_error`` and emits ``status_updated``.

        The savings calculation is wrapped in its own ``try/except`` so that a
        filesystem or parsing error does not prevent the success counter from
        being incremented — matching the original behaviour where
        ``success_count += 1`` ran unconditionally after the inner block.

        Args:
            file_path: Absolute path to the (now-compressed) image file.
            original_size_text: Human-readable size string captured before
                compression, e.g. ``"1.23 MB"``.
            row_index: Zero-based table row to update via signal.
            compressor: The ``BaseCompressor`` instance that ran; must not be
                ``None`` (callers should guard against the unsupported-format
                case before calling this method).
            success: Return value of ``compressor.compress_file()``.

        Returns:
            ``True`` when compression succeeded (success counter should be
            incremented by the caller), ``False`` otherwise (failure counter).
        """
        filename = os.path.basename(file_path)

        if success:
            try:
                original_size_mb = self._convert_to_mb(original_size_text)
                compressed_size = get_file_size(file_path)
                compressed_size_mb = self._convert_to_mb(compressed_size)

                saving_pct = (
                    (original_size_mb - compressed_size_mb) / original_size_mb * 100
                    if original_size_mb > 0
                    else 0.0
                )

                signals.compression_result_updated.emit(
                    row_index, compressed_size, saving_pct
                )
            except Exception:
                logger.exception(
                    "Error calculating savings for %s", _sanitise_for_log(filename)
                )
            return True
        else:
            error_msg = compressor.last_error or "unknown error"
            logger.error(
                "Compression failed for %s: %s",
                _sanitise_for_log(filename),
                _sanitise_for_log(error_msg),
            )
            signals.status_updated.emit(f"Failed: {filename} \u2014 {error_msg}")
            return False

    def _run_compression(self, snapshot: list, total_files: int) -> None:
        """Compress files in a worker thread.

        Reads exclusively from the pre-built snapshot — never from live UI
        widgets. Emits signals for every UI update so all widget changes
        happen on the main thread.

        Complexity is kept low by delegating format dispatch to
        ``_compress_file_by_format`` and result reporting to
        ``_emit_compression_result``.
        """
        prefs = dict(self.current_preferences)
        start_time = time.time()
        success_count = 0
        fail_count = 0

        for processed, file_info in enumerate(snapshot):
            file_path = file_info['path']
            original_size_text = file_info['original_size_text']
            row_index = file_info['row_index']
            filename = os.path.basename(file_path)

            try:
                if not os.path.isfile(file_path):
                    logger.warning(
                        "Skipped: %s no longer exists", _sanitise_for_log(file_path)
                    )
                    signals.status_updated.emit(f"Skipped: {filename} no longer exists")
                    fail_count += 1
                else:
                    format_str = get_file_format(file_path)
                    compressor, success = self._compress_file_by_format(
                        file_path, format_str, prefs
                    )

                    if compressor is None:
                        # Unsupported format — _compress_file_by_format already
                        # logged the warning and emitted the status signal.
                        fail_count += 1
                    elif self._emit_compression_result(
                        file_path, original_size_text, row_index, compressor, success
                    ):
                        success_count += 1
                    else:
                        fail_count += 1

            except Exception:
                logger.exception(
                    "Unexpected error processing %s", _sanitise_for_log(filename)
                )
                signals.status_updated.emit(f"Error processing: {filename}")
                fail_count += 1

            progress = int(((processed + 1) / total_files) * 100)
            signals.progress_updated.emit(progress)

        elapsed = time.time() - start_time
        avg_speed = total_files / elapsed if elapsed > 0 else 0

        if fail_count == 0:
            result_msg = f"All {success_count} files compressed successfully."
        else:
            result_msg = (
                f"{success_count}/{total_files} files compressed. {fail_count} failed."
                " Check the log for details."
            )

        signals.compression_complete.emit(
            f"{result_msg} {elapsed:.2f}s (avg: {avg_speed:.2f} files/sec)"
        )

    def _convert_to_mb(self, size_str):
        """Convert a human-readable size string (e.g. '1.23 MB') to float MB."""
        try:
            if not size_str or size_str == "N/A":
                return 0
            parts = size_str.split()
            value = float(parts[0])
            if 'KB' in size_str:
                return value / 1024
            elif 'MB' in size_str:
                return value
            elif 'GB' in size_str:
                return value * 1024
            else:
                return value / (1024 * 1024)
        except Exception:
            logger.warning("Could not parse size string '%s'", size_str)
            return 0

    def _update_compression_result(self, row_index, compressed_size, saving_percentage):
        """Update the table row with compression results for a single file."""
        if 0 <= row_index < self.file_list_widget.rowCount():
            compressed_item = QTableWidgetItem(f"{compressed_size}")
            compressed_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.file_list_widget.setItem(row_index, 4, compressed_item)

            saved_item = QTableWidgetItem(f"{saving_percentage:.2f}%")
            saved_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if saving_percentage < 0:
                saved_item.setForeground(_NEGATIVE_SAVINGS_COLOR)
            self.file_list_widget.setItem(row_index, 5, saved_item)

    # ── File selection / removal ───────────────────────────────────────────────

    def remove_selected_files(self):
        """Remove all selected rows from the file list.

        Rows are processed in reverse visual order so that removing a lower
        row does not shift the indices of higher rows.  The internal file_list
        is updated by path identity (read from UserRole) so it stays correct
        even when the table has been sorted.
        """
        selected_rows = sorted(
            {item.row() for item in self.file_list_widget.selectedItems()},
            reverse=True,
        )
        if not selected_rows:
            return
        for row in selected_rows:
            path_item = self.file_list_widget.item(row, 0)
            if path_item:
                path = path_item.data(Qt.ItemDataRole.UserRole)
                if path in self.file_list:
                    self.file_list.remove(path)
            self.file_list_widget.removeRow(row)

        self.update_info_widget()
        self.reset_progress_bar()

    def _update_remove_menu_text(self):
        """Update the 'Remove' menu entry text based on current selection."""
        selected_rows = {item.row() for item in self.file_list_widget.selectedItems()}
        n = len(selected_rows)
        if n == 0:
            self.remove_action.setText("Remove")
        elif n == 1:
            self.remove_action.setText("Remove File")
        else:
            self.remove_action.setText(f"Remove {n} Files")

    def select_all_files(self):
        """Select all rows in the file list."""
        self.file_list_widget.selectAll()

    def toggle_status_bar(self):
        """Toggle visibility of the status bar container widget."""
        self.status_bar_visible = not self.status_bar_visible
        # Hide/show the whole container so the layout reclaims the space.
        self.status_bar_widget.setVisible(self.status_bar_visible)

    def open_documentation(self) -> None:
        """Open the Mountaineer documentation in the default system browser."""
        url = QUrl("https://github.com/aries223/mountaineer/blob/main/Documentation/Documentation.md")
        QDesktopServices.openUrl(url)

    def show_about_dialog(self):
        """Show the About Mountaineer dialog."""
        from ui.about import AboutDialog
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    def show_context_menu(self, position):
        """Show a right-click context menu for removing files."""
        selected_rows = {item.row() for item in self.file_list_widget.selectedItems()}
        if not selected_rows:
            return

        menu = QMenu(self)
        label = "Remove Selected Files" if len(selected_rows) > 1 else "Remove File"
        remove_action = menu.addAction(label)

        action = menu.exec(self.file_list_widget.viewport().mapToGlobal(position))
        if action == remove_action:
            self.remove_selected_files()

    def remove_file_from_list(self, row):
        """Remove a single file by its current visual row index.

        The internal file_list is updated by path identity (read from
        UserRole) so it stays correct even when the table has been sorted.
        """
        if 0 <= row < self.file_list_widget.rowCount():
            path_item = self.file_list_widget.item(row, 0)
            if path_item:
                path = path_item.data(Qt.ItemDataRole.UserRole)
                if path in self.file_list:
                    self.file_list.remove(path)
            self.file_list_widget.removeRow(row)
            self.update_info_widget()
            self.reset_progress_bar()

    def reset_progress_bar(self):
        """Reset the progress bar to 0%."""
        self.progress_bar.setValue(0)
