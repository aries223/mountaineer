from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QSlider, QCheckBox, QPushButton, QHBoxLayout,
    QApplication,
)
from PyQt6.QtCore import Qt

from utils.preferences import Preferences


class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")

        layout = QVBoxLayout()

        self.preferences = Preferences()
        self.current_preferences = {}

        # JPEG compression level
        jpeg_layout = QHBoxLayout()
        jpeg_label = QLabel("JPEG Quality: (0=worst, 100=best)")
        self.jpeg_slider = QSlider(Qt.Orientation.Horizontal)
        self.jpeg_slider.setMinimum(0)
        self.jpeg_slider.setMaximum(100)
        self.jpeg_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.jpeg_slider.setTickInterval(10)
        self.jpeg_slider.setMinimumWidth(200)
        self.jpeg_value_label = QLabel("95")
        jpeg_layout.addWidget(jpeg_label)
        jpeg_layout.addWidget(self.jpeg_slider)
        jpeg_layout.addWidget(self.jpeg_value_label)

        # PNG compression effort
        png_layout = QHBoxLayout()
        png_label = QLabel("PNG Compression Effort: (0=least/fastest, 6=most/slowest)")
        self.png_slider = QSlider(Qt.Orientation.Horizontal)
        self.png_slider.setMinimum(0)
        self.png_slider.setMaximum(6)
        self.png_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.png_slider.setTickInterval(1)
        self.png_slider.setMinimumWidth(200)
        self.png_value_label = QLabel("1")
        png_layout.addWidget(png_label)
        png_layout.addWidget(self.png_slider)
        png_layout.addWidget(self.png_value_label)

        layout.addLayout(jpeg_layout)
        layout.addLayout(png_layout)

        self.lossless_checkbox = QCheckBox("Lossless (PNG files will take a very long time)")
        self.strip_metadata_checkbox = QCheckBox("Strip Metadata")

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_preferences)

        layout.addWidget(self.lossless_checkbox)
        layout.addWidget(self.strip_metadata_checkbox)
        layout.addWidget(save_button)

        self.setLayout(layout)

        # Connect slider value-change signals AFTER the widgets exist.
        # Note: _set_initial_values() uses blockSignals() around setValue()
        # calls so these handlers do not fire with an uninitialised
        # current_preferences dict.
        self.jpeg_slider.valueChanged.connect(self.update_jpeg_value_label)
        self.png_slider.valueChanged.connect(self.update_png_value_label)

    def _set_initial_values(self):
        """Set slider and checkbox values from saved preferences.

        blockSignals() is used around each setValue() call to prevent
        update_jpeg_value_label / update_png_value_label from firing before
        current_preferences has been populated from disk.
        """
        prefs = Preferences()
        current_prefs = prefs.load_preferences()

        jpeg_level = current_prefs.get('jpeg_compression_level', 95)
        png_level = current_prefs.get('png_compression_level', 1)
        lossless = current_prefs.get('lossless_compression', False)
        strip_metadata = current_prefs.get('strip_metadata', False)
        warn_before_overwrite = current_prefs.get('warn_before_overwrite', True)

        self.jpeg_slider.blockSignals(True)
        self.jpeg_slider.setValue(jpeg_level)
        self.jpeg_slider.blockSignals(False)
        self.jpeg_value_label.setText(str(jpeg_level))

        png_level = max(0, min(6, png_level))
        self.png_slider.blockSignals(True)
        self.png_slider.setValue(png_level)
        self.png_slider.blockSignals(False)
        self.png_value_label.setText(str(png_level))

        self.lossless_checkbox.setChecked(lossless)
        self.strip_metadata_checkbox.setChecked(strip_metadata)

        # Populate current_preferences from the loaded values so MainWindow
        # always receives a complete dict when it reads dialog.current_preferences.
        self.current_preferences = {
            'jpeg_compression_level': jpeg_level,
            'png_compression_level': png_level,
            'lossless_compression': lossless,
            'strip_metadata': strip_metadata,
            'warn_before_overwrite': warn_before_overwrite,
        }

    def save_preferences(self):
        """Save compression preferences, preserving existing window geometry settings."""
        prefs = Preferences()

        # Load existing prefs first so window geometry keys are not overwritten
        existing_prefs = prefs.load_preferences()

        # Include warn_before_overwrite from existing_prefs so the in-memory
        # state in MainWindow stays consistent with what was written to disk.
        new_values = {
            'jpeg_compression_level': self.jpeg_slider.value(),
            'png_compression_level': self.png_slider.value(),
            'lossless_compression': self.lossless_checkbox.isChecked(),
            'strip_metadata': self.strip_metadata_checkbox.isChecked(),
            'warn_before_overwrite': existing_prefs.get('warn_before_overwrite', True),
        }

        existing_prefs.update(new_values)
        prefs.save_preferences(existing_prefs)

        self.preferences.save_prefs_dialog_settings(
            self.x(), self.y(), self.width(), self.height()
        )

        self.current_preferences = new_values
        self.accept()

    def load_preferences(self):
        """Load and display current preferences."""
        self._set_initial_values()

    def update_jpeg_value_label(self, value):
        self.jpeg_value_label.setText(str(value))
        self.current_preferences['jpeg_compression_level'] = value

    def update_png_value_label(self, value):
        self.png_value_label.setText(str(value))
        self.current_preferences['png_compression_level'] = value

    def closeEvent(self, event):
        """Save window position and size when closing."""
        self.preferences.save_prefs_dialog_settings(
            self.x(), self.y(), self.width(), self.height()
        )
        super().closeEvent(event)
