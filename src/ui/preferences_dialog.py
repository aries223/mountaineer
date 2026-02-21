from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QSlider, QCheckBox, QPushButton, QHBoxLayout,
    QApplication, QStyle,
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
        # PM_LayoutHorizontalSpacing gives the actual style-dependent gap between
        # adjacent layout items, which is what separates the label from the slider.
        _style_h_spacing = self.style().pixelMetric(QStyle.PixelMetric.PM_LayoutHorizontalSpacing)

        jpeg_group_layout = QVBoxLayout()
        jpeg_group_layout.setSpacing(2)

        jpeg_layout = QHBoxLayout()
        jpeg_label = QLabel("JPEG Quality:")
        # Measure the label's own font after construction so the advance is
        # exact; contentsMargins().left() accounts for any internal padding.
        _jpeg_left_margin = (
            jpeg_label.fontMetrics().horizontalAdvance("JPEG Quality:")
            + jpeg_label.contentsMargins().left()
            + _style_h_spacing
        )
        _jpeg_val_width = jpeg_label.fontMetrics().horizontalAdvance("100") + 4
        self.jpeg_slider = QSlider(Qt.Orientation.Horizontal)
        self.jpeg_slider.setMinimum(0)
        self.jpeg_slider.setMaximum(100)
        self.jpeg_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.jpeg_slider.setTickInterval(10)
        self.jpeg_slider.setMinimumWidth(200)
        self.jpeg_value_label = QLabel("")
        self.jpeg_value_label.setFixedWidth(_jpeg_val_width)
        jpeg_layout.addWidget(jpeg_label)
        jpeg_layout.addWidget(self.jpeg_slider)
        jpeg_layout.addWidget(self.jpeg_value_label)

        jpeg_tick_layout = QHBoxLayout()
        jpeg_tick_layout.setContentsMargins(
            _jpeg_left_margin, 0, _jpeg_val_width + _style_h_spacing, 0
        )
        jpeg_tick_layout.addWidget(QLabel("0"))
        jpeg_tick_layout.addStretch()
        jpeg_tick_layout.addWidget(QLabel("50"))
        jpeg_tick_layout.addStretch()
        jpeg_tick_layout.addWidget(QLabel("100"))

        jpeg_group_layout.addLayout(jpeg_layout)
        jpeg_group_layout.addLayout(jpeg_tick_layout)

        # PNG compression effort
        png_group_layout = QVBoxLayout()
        png_group_layout.setSpacing(2)

        png_layout = QHBoxLayout()
        png_label = QLabel("PNG Compression Effort:")
        # Same measurement strategy as the JPEG block: use the label's own
        # fontMetrics() after construction for accurate pixel widths.
        _png_left_margin = (
            png_label.fontMetrics().horizontalAdvance("PNG Compression Effort:")
            + png_label.contentsMargins().left()
            + _style_h_spacing
        )
        _png_val_width = png_label.fontMetrics().horizontalAdvance("6") + 4
        self.png_slider = QSlider(Qt.Orientation.Horizontal)
        self.png_slider.setMinimum(0)
        self.png_slider.setMaximum(6)
        self.png_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.png_slider.setTickInterval(1)
        self.png_slider.setMinimumWidth(200)
        self.png_value_label = QLabel("")
        self.png_value_label.setFixedWidth(_png_val_width)
        png_layout.addWidget(png_label)
        png_layout.addWidget(self.png_slider)
        png_layout.addWidget(self.png_value_label)

        png_tick_layout = QHBoxLayout()
        png_tick_layout.setContentsMargins(
            _png_left_margin, 0, _png_val_width + _style_h_spacing, 0
        )
        png_tick_layout.addWidget(QLabel("0"))
        png_tick_layout.addStretch()
        png_tick_layout.addWidget(QLabel("6"))

        png_group_layout.addLayout(png_layout)
        png_group_layout.addLayout(png_tick_layout)

        layout.addLayout(jpeg_group_layout)
        layout.addLayout(png_group_layout)

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
