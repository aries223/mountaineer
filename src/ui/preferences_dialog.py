from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QSlider, QCheckBox, QHBoxLayout,
    QStyle, QDialogButtonBox,
)
from PyQt6.QtCore import Qt

from utils.preferences import Preferences


class PreferencesDialog(QDialog):
    _SLIDER_H_PADDING = 14   # px of breathing room on each side of every slider track
    _VALUE_LABEL_EXTRA = 4   # extra px beyond the widest digit string for the value label

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setWindowModality(Qt.WindowModality.WindowModal)

        layout = QVBoxLayout()

        self.preferences = Preferences()
        # Fix 6: initialise with full defaults so any signal that fires
        # during construction finds a complete dict rather than an empty one.
        self.current_preferences = {
            'jpeg_compression_level': 95,
            'png_compression_level': 1,
            'gif_lossy_level': 40,
            'webp_compression_level': 80,
            'lossless_compression': False,
            'strip_metadata': False,
            'warn_before_overwrite': True,
        }

        # JPEG compression level
        jpeg_group_layout = QVBoxLayout()
        jpeg_group_layout.setSpacing(0)

        jpeg_layout = QHBoxLayout()
        # Fix 5: store label as instance variable so showEvent can remeasure it.
        self.jpeg_label = QLabel("JPEG:")
        # Measure the label's own font after construction so the advance is
        # exact; contentsMargins().left() accounts for any internal padding.
        self.jpeg_slider = QSlider(Qt.Orientation.Horizontal)
        self.jpeg_slider.setMinimum(0)
        self.jpeg_slider.setMaximum(100)
        self.jpeg_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.jpeg_slider.setTickInterval(10)
        self.jpeg_slider.setPageStep(10)  # Fix 3: 10% of 0–100 range
        self.jpeg_slider.setMinimumWidth(200)
        self.jpeg_slider.setToolTip(
            "0=Lowest Quality (Smallest File); 100=Highest Quality (Largest File)"
        )
        _jpeg_val_width = self.jpeg_label.fontMetrics().horizontalAdvance("100") + self._VALUE_LABEL_EXTRA
        self.jpeg_value_label = QLabel("")
        self.jpeg_value_label.setFixedWidth(_jpeg_val_width)

        jpeg_layout.addWidget(self.jpeg_label)
        jpeg_layout.addSpacing(self._SLIDER_H_PADDING)
        jpeg_layout.addWidget(self.jpeg_slider)
        jpeg_layout.addSpacing(self._SLIDER_H_PADDING)
        jpeg_layout.addWidget(self.jpeg_value_label)

        # Fix 5: store tick layout as instance variable for remeasurement in showEvent.
        self.jpeg_tick_layout = QHBoxLayout()
        self.jpeg_tick_layout.addWidget(QLabel("0"))
        self.jpeg_tick_layout.addStretch()
        self.jpeg_tick_layout.addWidget(QLabel("50"))
        self.jpeg_tick_layout.addStretch()
        self.jpeg_tick_layout.addWidget(QLabel("100"))

        jpeg_group_layout.addLayout(jpeg_layout)
        jpeg_group_layout.addLayout(self.jpeg_tick_layout)

        # PNG compression effort
        png_group_layout = QVBoxLayout()
        png_group_layout.setSpacing(0)

        png_layout = QHBoxLayout()
        # Fix 5: store label as instance variable so showEvent can remeasure it.
        self.png_label = QLabel("PNG:")
        # Same measurement strategy as the JPEG block: use the label's own
        # fontMetrics() after construction for accurate pixel widths.
        self.png_slider = QSlider(Qt.Orientation.Horizontal)
        self.png_slider.setMinimum(0)
        self.png_slider.setMaximum(6)
        self.png_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.png_slider.setTickInterval(1)
        self.png_slider.setPageStep(1)  # Fix 3: full range is only 6
        self.png_slider.setMinimumWidth(200)
        self.png_slider.setToolTip(
            "0=Highest Quality (Fastest, Largest File); 6=Lowest Quality (Slowest, Smallest File)"
        )
        _png_val_width = self.png_label.fontMetrics().horizontalAdvance("6") + self._VALUE_LABEL_EXTRA
        self.png_value_label = QLabel("")
        self.png_value_label.setFixedWidth(_png_val_width)
        png_layout.addWidget(self.png_label)
        png_layout.addSpacing(self._SLIDER_H_PADDING)
        png_layout.addWidget(self.png_slider)
        png_layout.addSpacing(self._SLIDER_H_PADDING)
        png_layout.addWidget(self.png_value_label)

        # Fix 5: store tick layout as instance variable for remeasurement in showEvent.
        self.png_tick_layout = QHBoxLayout()
        self.png_tick_layout.addWidget(QLabel("0"))
        self.png_tick_layout.addStretch()
        self.png_tick_layout.addWidget(QLabel("3"))
        self.png_tick_layout.addStretch()
        self.png_tick_layout.addWidget(QLabel("6"))

        png_group_layout.addLayout(png_layout)
        png_group_layout.addLayout(self.png_tick_layout)

        layout.addLayout(jpeg_group_layout)
        layout.addLayout(png_group_layout)

        # GIF lossy level
        gif_group_layout = QVBoxLayout()
        gif_group_layout.setSpacing(0)

        gif_layout = QHBoxLayout()
        # Fix 5: store label as instance variable so showEvent can remeasure it.
        self.gif_label = QLabel("GIF:")
        self.gif_slider = QSlider(Qt.Orientation.Horizontal)
        self.gif_slider.setMinimum(0)
        self.gif_slider.setMaximum(200)
        self.gif_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.gif_slider.setTickInterval(20)
        self.gif_slider.setPageStep(20)  # Fix 3: matches tick interval, 10% of 0–200
        self.gif_slider.setMinimumWidth(200)
        self.gif_slider.setToolTip(
            "0=Lossless; 200=Lowest Quality (Smallest File)"
        )
        _gif_val_width = self.gif_label.fontMetrics().horizontalAdvance("200") + self._VALUE_LABEL_EXTRA
        self.gif_value_label = QLabel("")
        self.gif_value_label.setFixedWidth(_gif_val_width)
        gif_layout.addWidget(self.gif_label)
        gif_layout.addSpacing(self._SLIDER_H_PADDING)
        gif_layout.addWidget(self.gif_slider)
        gif_layout.addSpacing(self._SLIDER_H_PADDING)
        gif_layout.addWidget(self.gif_value_label)

        # Fix 5: store tick layout as instance variable for remeasurement in showEvent.
        self.gif_tick_layout = QHBoxLayout()
        self.gif_tick_layout.addWidget(QLabel("0"))
        self.gif_tick_layout.addStretch()
        self.gif_tick_layout.addWidget(QLabel("100"))
        self.gif_tick_layout.addStretch()
        self.gif_tick_layout.addWidget(QLabel("200"))

        gif_group_layout.addLayout(gif_layout)
        gif_group_layout.addLayout(self.gif_tick_layout)

        # WebP quality
        webp_group_layout = QVBoxLayout()
        webp_group_layout.setSpacing(0)

        webp_layout = QHBoxLayout()
        # Fix 5: store label as instance variable so showEvent can remeasure it.
        self.webp_label = QLabel("WebP:")
        self.webp_slider = QSlider(Qt.Orientation.Horizontal)
        self.webp_slider.setMinimum(0)
        self.webp_slider.setMaximum(100)
        self.webp_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.webp_slider.setTickInterval(10)
        self.webp_slider.setPageStep(10)  # Fix 3: 10% of 0–100 range
        self.webp_slider.setMinimumWidth(200)
        self.webp_slider.setToolTip(
            "0=Lowest Quality (Smallest File); 100=Highest Quality (Largest File)"
        )
        _webp_val_width = self.webp_label.fontMetrics().horizontalAdvance("100") + self._VALUE_LABEL_EXTRA
        self.webp_value_label = QLabel("")
        self.webp_value_label.setFixedWidth(_webp_val_width)
        webp_layout.addWidget(self.webp_label)
        webp_layout.addSpacing(self._SLIDER_H_PADDING)
        webp_layout.addWidget(self.webp_slider)
        webp_layout.addSpacing(self._SLIDER_H_PADDING)
        webp_layout.addWidget(self.webp_value_label)

        # Fix 5: store tick layout as instance variable for remeasurement in showEvent.
        self.webp_tick_layout = QHBoxLayout()
        self.webp_tick_layout.addWidget(QLabel("0"))
        self.webp_tick_layout.addStretch()
        self.webp_tick_layout.addWidget(QLabel("50"))
        self.webp_tick_layout.addStretch()
        self.webp_tick_layout.addWidget(QLabel("100"))

        webp_group_layout.addLayout(webp_layout)
        webp_group_layout.addLayout(self.webp_tick_layout)

        layout.addLayout(gif_group_layout)
        layout.addLayout(webp_group_layout)

        self.lossless_checkbox = QCheckBox("Lossless (PNG files will take a very long time)")
        self.lossless_checkbox.setToolTip(
            "JPEG: repack without re-encoding (no quality loss, minimal size gain).\n"
            "PNG: maximum-effort lossless compression (slowest, best ratio).\n"
            "GIF/WebP: uses lossless mode."
        )
        self.strip_metadata_checkbox = QCheckBox("Strip Metadata")
        self.strip_metadata_checkbox.setToolTip(
            "Remove EXIF, IPTC, and XMP metadata from files. "
            "Saves a small amount of space and removes camera and location data."
        )
        # Fix 2: add warn_before_overwrite checkbox so the dialog owns this value.
        self.warn_overwrite_checkbox = QCheckBox("Warn before overwriting files")
        self.warn_overwrite_checkbox.setToolTip(
            "Show a confirmation prompt before compressing files in place."
        )

        layout.addWidget(self.lossless_checkbox)
        layout.addWidget(self.strip_metadata_checkbox)
        layout.addWidget(self.warn_overwrite_checkbox)

        # Fix 1: replace the standalone Save button with a standard Save/Cancel
        # button box so the dialog follows platform dialog conventions and the
        # user can dismiss without persisting changes.
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.button(QDialogButtonBox.StandardButton.Save).clicked.connect(self.save_preferences)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Give all format labels the same width so the slider tracks left-align.
        # This block must appear after all four labels are constructed.
        # Stored as an instance variable so _apply_tick_margins() can use the
        # allocated width rather than the raw text advance of each label string.
        self._label_width = max(
            self.jpeg_label.fontMetrics().horizontalAdvance("JPEG:"),
            self.png_label.fontMetrics().horizontalAdvance("PNG:"),
            self.gif_label.fontMetrics().horizontalAdvance("GIF:"),
            self.webp_label.fontMetrics().horizontalAdvance("WebP:"),
        ) + 4  # small rounding margin
        self.jpeg_label.setFixedWidth(self._label_width)
        self.png_label.setFixedWidth(self._label_width)
        self.gif_label.setFixedWidth(self._label_width)
        self.webp_label.setFixedWidth(self._label_width)

        self.setLayout(layout)
        self._apply_tick_margins()

        # Connect slider value-change signals AFTER the widgets exist.
        # Note: _set_initial_values() uses blockSignals() around setValue()
        # calls so these handlers do not fire with an uninitialised
        # current_preferences dict.
        self.jpeg_slider.valueChanged.connect(self.update_jpeg_value_label)
        self.png_slider.valueChanged.connect(self.update_png_value_label)
        self.gif_slider.valueChanged.connect(self.update_gif_value_label)
        self.webp_slider.valueChanged.connect(self.update_webp_value_label)

        # Populate widgets from saved preferences now that all signals are
        # wired.  Doing this here means callers do not need a separate
        # load_preferences() call after construction.
        self._set_initial_values()

    # ------------------------------------------------------------------
    # Fix 5: tick-margin helper and showEvent override
    # ------------------------------------------------------------------

    def _apply_tick_margins(self) -> None:
        """Recalculate and reapply the tick-label content margins for all four
        sliders.

        Doing this in both ``__init__`` and ``showEvent`` ensures the margins
        are correct at initial render and are re-resolved after the widget is
        fully realised on screen (which matters on HiDPI/Wayland where font
        metrics may change once the window is placed on its target screen).
        """
        style_h_spacing = self.style().pixelMetric(QStyle.PixelMetric.PM_LayoutHorizontalSpacing)
        pad = self._SLIDER_H_PADDING

        # JPEG
        jpeg_lm = self._label_width + self.jpeg_label.contentsMargins().left() + style_h_spacing
        jpeg_rm = self.jpeg_label.fontMetrics().horizontalAdvance("100") + self._VALUE_LABEL_EXTRA + style_h_spacing + pad
        self.jpeg_tick_layout.setContentsMargins(jpeg_lm + pad, 0, jpeg_rm, 0)

        # PNG
        png_lm = self._label_width + self.png_label.contentsMargins().left() + style_h_spacing
        png_rm = self.png_label.fontMetrics().horizontalAdvance("6") + self._VALUE_LABEL_EXTRA + style_h_spacing + pad
        self.png_tick_layout.setContentsMargins(png_lm + pad, 0, png_rm, 0)

        # GIF
        gif_lm = self._label_width + self.gif_label.contentsMargins().left() + style_h_spacing
        gif_rm = self.gif_label.fontMetrics().horizontalAdvance("200") + self._VALUE_LABEL_EXTRA + style_h_spacing + pad
        self.gif_tick_layout.setContentsMargins(gif_lm + pad, 0, gif_rm, 0)

        # WebP
        webp_lm = self._label_width + self.webp_label.contentsMargins().left() + style_h_spacing
        webp_rm = self.webp_label.fontMetrics().horizontalAdvance("100") + self._VALUE_LABEL_EXTRA + style_h_spacing + pad
        self.webp_tick_layout.setContentsMargins(webp_lm + pad, 0, webp_rm, 0)

    def showEvent(self, event) -> None:
        """Reapply tick-label margins once the widget is fully realised.

        On HiDPI or Wayland displays the font scale (and therefore
        fontMetrics()) may differ before and after the window is placed on
        its target screen.  Re-running _apply_tick_margins() here ensures the
        tick labels are always aligned correctly.
        """
        super().showEvent(event)
        self._apply_tick_margins()

    # ------------------------------------------------------------------

    def _set_initial_values(self):
        """Set slider and checkbox values from saved preferences.

        blockSignals() is used around each setValue() call to prevent
        update_jpeg_value_label / update_png_value_label from firing before
        current_preferences has been populated from disk.
        """
        current_prefs = self.preferences.load_preferences()

        jpeg_level = current_prefs.get('jpeg_compression_level', 95)
        png_level = current_prefs.get('png_compression_level', 1)
        gif_level = current_prefs.get('gif_lossy_level', 40)
        webp_level = current_prefs.get('webp_compression_level', 80)
        lossless = current_prefs.get('lossless_compression', False)
        strip_metadata = current_prefs.get('strip_metadata', False)
        warn_before_overwrite = current_prefs.get('warn_before_overwrite', True)

        jpeg_level = max(0, min(100, jpeg_level))
        self.jpeg_slider.blockSignals(True)
        self.jpeg_slider.setValue(jpeg_level)
        self.jpeg_slider.blockSignals(False)
        self.jpeg_value_label.setText(str(jpeg_level))

        png_level = max(0, min(6, png_level))
        self.png_slider.blockSignals(True)
        self.png_slider.setValue(png_level)
        self.png_slider.blockSignals(False)
        self.png_value_label.setText(str(png_level))

        gif_level = max(0, min(200, gif_level))
        self.gif_slider.blockSignals(True)
        self.gif_slider.setValue(gif_level)
        self.gif_slider.blockSignals(False)
        self.gif_value_label.setText(str(gif_level))

        webp_level = max(0, min(100, webp_level))
        self.webp_slider.blockSignals(True)
        self.webp_slider.setValue(webp_level)
        self.webp_slider.blockSignals(False)
        self.webp_value_label.setText(str(webp_level))

        self.lossless_checkbox.setChecked(lossless)
        self.strip_metadata_checkbox.setChecked(strip_metadata)
        # Fix 2: initialise warn_before_overwrite checkbox from saved prefs.
        self.warn_overwrite_checkbox.setChecked(warn_before_overwrite)

        # Populate current_preferences from the loaded values so MainWindow
        # always receives a complete dict when it reads dialog.current_preferences.
        self.current_preferences = {
            'jpeg_compression_level': jpeg_level,
            'png_compression_level': png_level,
            'gif_lossy_level': gif_level,
            'webp_compression_level': webp_level,
            'lossless_compression': lossless,
            'strip_metadata': strip_metadata,
            'warn_before_overwrite': warn_before_overwrite,
        }

    def save_preferences(self):
        """Persist current widget values to disk without overwriting unrelated preference keys."""
        # Load existing prefs first so window geometry keys are not overwritten
        existing_prefs = self.preferences.load_preferences()

        # Fix 2: read warn_before_overwrite from the checkbox rather than
        # passing the stale on-disk value through unchanged.
        new_values = {
            'jpeg_compression_level': self.jpeg_slider.value(),
            'png_compression_level': self.png_slider.value(),
            'gif_lossy_level': self.gif_slider.value(),
            'webp_compression_level': self.webp_slider.value(),
            'lossless_compression': self.lossless_checkbox.isChecked(),
            'strip_metadata': self.strip_metadata_checkbox.isChecked(),
            'warn_before_overwrite': self.warn_overwrite_checkbox.isChecked(),
        }

        existing_prefs.update(new_values)
        self.preferences.save_preferences(existing_prefs)

        self.current_preferences = new_values
        self.accept()

    def update_jpeg_value_label(self, value):
        self.jpeg_value_label.setText(str(value))
        self.current_preferences['jpeg_compression_level'] = value

    def update_png_value_label(self, value):
        self.png_value_label.setText(str(value))
        self.current_preferences['png_compression_level'] = value

    def update_gif_value_label(self, value):
        self.gif_value_label.setText(str(value))
        self.current_preferences['gif_lossy_level'] = value

    def update_webp_value_label(self, value):
        self.webp_value_label.setText(str(value))
        self.current_preferences['webp_compression_level'] = value

    def closeEvent(self, event):
        """Save window position and size when closing.

        Geometry is saved on both Accept and Cancel so the user's preferred
        window size is remembered even when dismissing without saving changes.
        The Wayland origin guard lives in save_prefs_dialog_settings().
        """
        self.preferences.save_prefs_dialog_settings(
            self.x(), self.y(), self.width(), self.height()
        )
        super().closeEvent(event)
