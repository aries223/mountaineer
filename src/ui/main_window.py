from PyQt6.QtWidgets import (
    QMainWindow, QMenuBar, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QProgressBar, QSizePolicy,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMenu
)
from PyQt6.QtCore import Qt  # Add QSize import
from PyQt6.QtWidgets import QApplication  # Import QApplication for processEvents
from compression.jpeg_compressor import JpegCompressor
from compression.png_compressor import PngCompressor
from utils.preferences import Preferences
from utils.file_utils import get_image_dimensions, get_file_size, get_file_format
import os, time, threading
from utils.signals import signals  # Import the custom signals

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mountaineer")

        # Initialize preferences and load settings
        self.preferences = Preferences()
        window_settings = self.preferences.get_main_window_settings()

        print(f"Loaded main window settings: {window_settings}")

        # Set initial window size and position based on saved preferences or defaults
        self.resize(window_settings['width'], window_settings['height'])

        # Only set position if we have valid coordinates (non-None)
        x = window_settings.get('x')
        y = window_settings.get('y')

        if x is not None and y is not None:
            print(f"Setting main window position to saved coordinates: x={x}, y={y}")
            self.move(x, y)

            # Initialize other components
            self.current_preferences = self.preferences.load_preferences()
            self.file_list = []

        # Create menu bar
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Create button bar
        self.button_bar = QWidget()
        self.button_bar_layout = QHBoxLayout()
        self.button_bar.setLayout(self.button_bar_layout)

        add_files_button = QPushButton("Add Files")
        clear_list_button = QPushButton("Clear File List")
        preferences_button = QPushButton("Preferences")

        add_files_button.clicked.connect(self.add_files)
        clear_list_button.clicked.connect(self.clear_file_list)
        preferences_button.clicked.connect(self.show_preferences)

        self.button_bar_layout.addWidget(add_files_button)
        self.button_bar_layout.addWidget(clear_list_button)
        self.button_bar_layout.addWidget(preferences_button)

        # File list widget (as table) with drag-and-drop support
        self.file_list_widget = QTableWidget()
        self.file_list_widget.setColumnCount(6)
        headers = ["File Name", "Format", "Dimensions", "Size", "Compressed", "Saved"]
        self.file_list_widget.setHorizontalHeaderLabels(headers)

        # Set column widths - File Name expands, others are interactive
        header = self.file_list_widget.horizontalHeader()
        for i in range(self.file_list_widget.columnCount()):
            if i == 0:  # File Name column should expand
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            else:  # Other columns are interactive width
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)

        # Enable drag-and-drop for the file list widget
        self.file_list_widget.setAcceptDrops(True)
        self.file_list_widget.viewport().setAcceptDrops(True)
        self.file_list_widget.setDragDropMode(QTableWidget.DragDropMode.InternalMove)

        # Add context menu for file removal
        self.file_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list_widget.customContextMenuRequested.connect(self.show_context_menu)

        # Info widget
        self.info_widget = QLabel("0 files")
        self.info_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Control widget
        self.control_widget = QWidget()
        control_layout = QHBoxLayout()

        compress_button = QPushButton("Compress Images")
        quit_button = QPushButton("Quit")

        compress_button.clicked.connect(self.compress_images)
        quit_button.clicked.connect(self.close)

        control_layout.addWidget(compress_button)
        control_layout.addWidget(quit_button)
        self.control_widget.setLayout(control_layout)

        # Status bar
        status_bar_widget = QWidget()
        status_bar_layout = QHBoxLayout()

        self.status_label = QLabel("Ready", self)

        # Progress bar - make it 50% of main window width and set maximum height
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setMaximumHeight(int(self.height() * 0.02))  # Set to 2% of window height

        status_bar_layout.addWidget(self.status_label, 50)  # Status takes 50%
        status_bar_layout.addWidget(self.progress_bar, 50)  # Progress bar takes 50%

        status_bar_widget.setLayout(status_bar_layout)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.button_bar)
        main_layout.addWidget(self.file_list_widget, 1)  # File list takes full width
        main_layout.addWidget(self.info_widget)
        main_layout.addWidget(self.control_widget)
        main_layout.addWidget(status_bar_widget)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Connect signals to slots for thread-safe UI updates
        signals.progress_updated.connect(self._update_progress)
        signals.status_updated.connect(self._safe_update_status)
        signals.compression_complete.connect(self._safe_update_status)

    def closeEvent(self, event):
        """Save main window position and size when closing"""
        print(f"Saving main window position: x={self.x()}, y={self.y()}, width={self.width()}, height={self.height()}")
        self.preferences.save_main_window_settings(
            self.x(),
            self.y(),
            self.width(),
            self.height()
        )
        super().closeEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            # Accept files and directories
            urls = [url.toLocalFile() for url in event.mimeData().urls()]
            accepted = any(
                os.path.isfile(url) or
                (os.path.isdir(url) and any(os.path.isfile(os.path.join(url, f)) for f in os.listdir(url)))
                for url in urls)
            if accepted:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        urls = [url.toLocalFile() for url in event.mimeData().urls()]
        processed_files = 0
        skipped_files = 0
        total_urls = len(urls)

        for url in urls:
            try:
                if os.path.isfile(url):
                    success, is_skipped = self._try_add_file_to_list(url)
                    if success:
                        processed_files += 1
                    else:
                        skipped_files += is_skipped
                elif os.path.isdir(url):
                    # Process directory contents
                    dir_files_processed = 0
                    dir_skipped_files = 0

                    for file_name in os.listdir(url):
                        file_path = os.path.join(url, file_name)
                        if os.path.isfile(file_path):
                            success, is_skipped = self._try_add_file_to_list(file_path)
                            if success:
                                dir_files_processed += 1
                            else:
                                dir_skipped_files += is_skipped

                    print(f"Processed {dir_files_processed} files from directory: {url} (skipped {dir_skipped_files})")
                    processed_files += dir_files_processed
                    skipped_files += dir_skipped_files
                else:
                    print(f"Skipping invalid path: {url}")
                    skipped_files += 1

            except Exception as e:
                print(f"Error processing dropped item {url}: {e}")
                skipped_files += 1
                continue

        # Update progress information based on actual successful additions and skips
        if processed_files > 0 or skipped_files > 0:
            message = f"{processed_files} files added to the list"
            if skipped_files > 0:
                message += f", {skipped_files} incompatible files skipped"

            self.status_label.setText(message)
        else:
            self.status_label.setText("No valid files found in drop")

        event.acceptProposedAction()

    def _is_supported_image(self, file_path):
        """Check if a file is a supported image format"""
        try:
            format_str = get_file_format(file_path)
            return format_str in ["JPEG", "PNG"]
        except Exception as e:
            print(f"Error checking file format: {e}")
            return False

    def _try_add_file_to_list(self, file_path):
        """Try to add a file to the list and return success status"""
        if not os.path.isfile(file_path):
            print(f"Invalid file path: {file_path}")
            return False, True  # Skipped due to invalid path

        try:
            format_str = get_file_format(file_path)
            if format_str not in ["JPEG", "PNG"]:
                print(f"Unsupported format: {format_str} for file: {file_path}")
                return False, True  # Skipped due to unsupported format

            # File is valid, proceed with adding
            success = self.add_file_to_list(file_path)
            return success, False  # Successfully processed

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            import traceback
            traceback.print_exc()
            return False, True  # Skipped due to error

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Add Files", "", "Image Files (*.jpg *.jpeg *.png);;All Files (*)"
        )
        if files:
            added_count = 0
            skipped_count = 0

            for file_path in files:
                success, is_skipped = self._try_add_file_to_list(file_path)
                if success:
                    added_count += 1
                else:
                    skipped_count += is_skipped

            if added_count > 0 or skipped_count > 0:
                message = f"Added {added_count} files to the list"
                if skipped_count > 0:
                    message += f", {skipped_count} incompatible files skipped"

                self.status_label.setText(message)

    def add_file_to_list(self, file_path):
        """Actual implementation of adding a valid file to the list"""
        print(f"Adding file to list: {file_path}")

        try:
            # Get file information
            format_str = get_file_format(file_path)
            dimensions = get_image_dimensions(file_path)
            size = get_file_size(file_path)

            # Add to list
            row_count = self.file_list_widget.rowCount()
            self.file_list_widget.insertRow(row_count)

            # File Name column (left-aligned)
            file_name_item = QTableWidgetItem(os.path.basename(file_path))
            file_name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.file_list_widget.setItem(row_count, 0, file_name_item)

            # Other columns (right-aligned)
            format_item = QTableWidgetItem(format_str)
            format_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.file_list_widget.setItem(row_count, 1, format_item)

            dimensions_item = QTableWidgetItem(dimensions)
            dimensions_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.file_list_widget.setItem(row_count, 2, dimensions_item)

            size_item = QTableWidgetItem(size)
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.file_list_widget.setItem(row_count, 3, size_item)

            # Empty compressed and saved columns initially (right-aligned)
            compressed_item = QTableWidgetItem("")
            compressed_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.file_list_widget.setItem(row_count, 4, compressed_item)

            saved_item = QTableWidgetItem("")
            saved_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.file_list_widget.setItem(row_count, 5, saved_item)

            # Store file path in item data for later use
            file_name_item.setData(Qt.ItemDataRole.UserRole, file_path)

            # Add to internal list
            self.file_list.append(file_path)

            print(f"Added file {file_path} to list")

            # Update info widget and reset progress bar
            self.update_info_widget()
            self.reset_progress_bar()

            return True

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def clear_file_list(self):
        # Clean up any cached temporary files
        if hasattr(self, '_temp_preview_file') and os.path.exists(getattr(self, '_temp_preview_file', '')):
            os.unlink(getattr(self, '_temp_preview_file', ''))

        self.file_list_widget.setRowCount(0)
        self.file_list = []
        if hasattr(self, '_current_preview_file'):
            del self._current_preview_file
        if hasattr(self, '_temp_preview_file'):
            del self._temp_preview_file

        # Update info widget and reset progress bar AND status label
        self.update_info_widget()
        self.reset_progress_bar()
        self.status_label.setText("Ready")  # Reset status bar text

    def update_info_widget(self):
        try:
            if len(self.file_list) == 0:
                self.info_widget.setText("0 files")
                return

            self.info_widget.setText(f"{len(self.file_list)} files")

        except Exception as e:
            print(f"Error updating info widget: {e}")
            import traceback
            traceback.print_exc()
            self.info_widget.setText("Error calculating file count")

    def show_preferences(self):
        from ui.preferences_dialog import PreferencesDialog
        dialog = PreferencesDialog()

        # Load preferences dialog settings
        window_settings = self.preferences.get_prefs_dialog_settings()

        print(f"Loaded prefs dialog settings: {window_settings}")

        # Set default size but allow resizing
        dialog.resize(window_settings['width'], window_settings['height'])
        if window_settings['x'] is not None and window_settings['y'] is not None:
            dialog.move(window_settings['x'], window_settings['y'])

        dialog.load_preferences()

        if dialog.exec():
            # Reload preferences after saving AND update current preferences immediately
            self.current_preferences = dialog.current_preferences

    def compress_images(self):
        if not self.file_list:
            signals.status_updated.emit("Error: No files selected")
            return

        total_files = len(self.file_list)
        signals.status_updated.emit(f"Starting compression of {total_files} files...")

        # Reset progress bar before starting compression
        self.progress_bar.setValue(0)

        # Start compression in a separate thread
        compression_thread = threading.Thread(
            target=self._run_compression,
            args=(self.file_list.copy(), total_files)
        )
        compression_thread.start()

    def _update_progress(self, progress):
        """Update progress bar safely from main thread"""
        self.progress_bar.setValue(progress)

    def _safe_update_status(self, message):
        """Update status label in a thread-safe manner"""
        if not self.isVisible():
            return  # Application is closing

        try:
            self.status_label.setText(message)
            QApplication.processEvents()  # Process pending events to update UI immediately
        except RuntimeError:
            # This can happen if the widget is being deleted
            pass

    def _run_compression(self, file_list, total_files):
        """Run compression operations in a separate thread"""
        start_time = time.time()  # Track start time
        completed_files = 0

        for index, file_path in enumerate(file_list):
            try:
                format_str = get_file_format(file_path)
                filename = os.path.basename(file_path)

                if format_str == "JPEG":
                    compressor = JpegCompressor()
                    output_path = None

                    success = compressor.compress_file(
                        file_path,
                        output_path,
                        lossless=self.current_preferences['lossless_compression'],
                        strip_metadata=self.current_preferences['strip_metadata'],
                        jpeg_quality=self.current_preferences['jpeg_compression_level']
                    )

                elif format_str == "PNG":
                    compressor = PngCompressor()
                    output_path = None

                    success = compressor.compress_file(
                        file_path,
                        output_path,
                        lossless=self.current_preferences['lossless_compression'],
                        strip_metadata=self.current_preferences['strip_metadata'],
                        png_quality=self.current_preferences['png_compression_level']
                    )
                else:
                    print(f"Unsupported format: {format_str}")
                    signals.status_updated.emit(f"Warning: {filename} skipped due to unsupported format")
                    continue

                if success:
                    # Update compressed size in UI
                    try:
                        original_size = float(self.file_list_widget.item(index, 3).text().split()[0])
                        compressed_size = get_file_size(file_path)
                        compressed_size_value = float(compressed_size.split()[0])
                        compression_saving = ((original_size - compressed_size_value) / original_size) * 100

                    except Exception as e:
                        print(f"Error updating UI for compressed file: {e}")
                else:
                    signals.status_updated.emit(f"Failed to compress: {filename} - Check if file exists")

                completed_files += 1
                progress = int((completed_files / total_files) * 100)

                # Emit signal instead of direct UI update
                signals.progress_updated.emit(progress)
                time.sleep(0.01)  # Small delay to prevent overwhelming the UI

            except Exception as e:
                print(f"Error compressing {file_path}: {e}")
                signals.status_updated.emit(f"Error processing: {filename}")

        end_time = time.time()
        elapsed_time = end_time - start_time
        average_speed = completed_files / elapsed_time if elapsed_time > 0 else 0

        success_message = f"All images compressed successfully. " if completed_files == total_files else "Some files failed to compress. "
        performance_message = f"Compressed in {elapsed_time:.2f} seconds (avg: {average_speed:.2f} files/sec)"

        signals.compression_complete.emit(success_message + performance_message)
        self.progress_bar.setValue(100)

    def show_context_menu(self, position):
        """Show context menu for file removal"""
        if not self.file_list_widget.selectedItems():
            return  # No selection, do nothing

        # Get the selected row
        item = self.file_list_widget.itemAt(position)
        if item and item.column() == 0:  # Only allow removal from File Name column
            row = item.row()

            menu = QMenu(self)
            remove_action = menu.addAction("Remove File")

            action = menu.exec(self.file_list_widget.viewport().mapToGlobal(position))

            if action == remove_action:
                self.remove_file_from_list(row)

    def remove_file_from_list(self, row):
        """Remove file from list and update UI"""
        if 0 <= row < len(self.file_list):
            # Remove from internal list first
            removed_file = self.file_list.pop(row)
            print(f"Removed file: {removed_file}")

            # Remove from widget
            self.file_list_widget.removeRow(row)

            # Update info widget and reset progress bar
            self.update_info_widget()
            self.reset_progress_bar()

    def reset_progress_bar(self):
        """Reset the progress bar to 0%"""
        self.progress_bar.setValue(0)
