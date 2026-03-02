# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright © 2026 Aries223 (https://github.com/aries223)
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QSlider, QCheckBox, QHBoxLayout,
    QStyle, QDialogButtonBox,
    QGroupBox, QSpinBox, QDoubleSpinBox, QComboBox, QRadioButton, QButtonGroup,
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
        layout.setContentsMargins(36, 28, 36, 12)

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
            'gif_resize_enabled': False,
            'gif_resize_mode': 'resize',
            'gif_resize_width': 0,
            'gif_resize_height': 0,
            'gif_scale_x': 1.0,
            'gif_scale_y': 0.0,
            'gif_colors_enabled': False,
            'gif_colors_num': 256,
            'gif_dither_enabled': False,
            'gif_dither_method': 'floyd-steinberg',
            'gif_remove_frames_enabled': False,
            'gif_remove_frames_n': 2,
            'gif_remove_frames_offset': 0,
            'gif_loopcount_enabled': False,
            'gif_loopcount_forever': True,
            'gif_loopcount_value': 1,
            'gif_delay_enabled': False,
            'gif_delay_value': 10,
            'gif_optimize_enabled': False,
            'gif_optimize_level': 2,
            'gif_optimize_keep_empty': False,
            'gif_unoptimize_enabled': False,
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
        self.jpeg_value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

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
        self.png_value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
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
        self.gif_value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
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
        self.webp_value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
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

        # WebP slider appears before GIF slider so the GIF Options group
        # sits immediately below the GIF lossy slider.
        layout.addLayout(webp_group_layout)
        layout.addLayout(gif_group_layout)
        layout.addSpacing(16)

        # GIF Options group
        gif_options_box = QGroupBox("GIF Options")
        gif_opts_layout = QVBoxLayout()
        gif_opts_layout.setSpacing(6)
        gif_options_box.setLayout(gif_opts_layout)

        # --- Row 1: Resize ---
        resize_row = QHBoxLayout()
        self.gif_resize_cb = QCheckBox("Resize")
        resize_row.addWidget(self.gif_resize_cb)

        resize_sub = QVBoxLayout()
        resize_sub.setContentsMargins(20, 0, 0, 0)

        # resize radio row
        resize_radio_row = QHBoxLayout()
        self.gif_resize_radio = QRadioButton("Resize to:")
        self.gif_resize_width_spin = QSpinBox()
        self.gif_resize_width_spin.setRange(0, 9999)
        # Fix P: tooltip explains the 0=auto convention used by gifsicle.
        self.gif_resize_width_spin.setToolTip("Target width in pixels. 0 = auto-fit (preserve aspect ratio).")
        self.gif_resize_height_spin = QSpinBox()
        self.gif_resize_height_spin.setRange(0, 9999)
        # Fix P: tooltip mirrors the width tooltip so both spinboxes are self-documenting.
        self.gif_resize_height_spin.setToolTip("Target height in pixels. 0 = auto-fit (preserve aspect ratio).")
        resize_radio_row.addWidget(self.gif_resize_radio)
        resize_radio_row.addWidget(self.gif_resize_width_spin)
        resize_radio_row.addWidget(QLabel("×"))
        resize_radio_row.addWidget(self.gif_resize_height_spin)
        resize_radio_row.addWidget(QLabel("px  (0=auto)"))
        resize_radio_row.addStretch()

        # scale radio row
        scale_radio_row = QHBoxLayout()
        self.gif_scale_radio = QRadioButton("Scale by:")
        self.gif_scale_x_spin = QDoubleSpinBox()
        self.gif_scale_x_spin.setRange(0.01, 99.0)
        self.gif_scale_x_spin.setSingleStep(0.1)
        self.gif_scale_x_spin.setDecimals(2)
        # Fix P: tooltip clarifies the percentage semantics of the scale factor.
        self.gif_scale_x_spin.setToolTip("Horizontal scale factor. Example: 0.5 = 50%.")
        self.gif_scale_y_spin = QDoubleSpinBox()
        self.gif_scale_y_spin.setRange(0.0, 99.0)
        self.gif_scale_y_spin.setSingleStep(0.1)
        self.gif_scale_y_spin.setDecimals(2)
        # Fix P: tooltip explains the 0.0=uniform convention used by gifsicle.
        self.gif_scale_y_spin.setToolTip("Vertical scale factor. 0.0 = uniform (match X factor).")
        scale_radio_row.addWidget(self.gif_scale_radio)
        scale_radio_row.addWidget(self.gif_scale_x_spin)
        scale_radio_row.addWidget(QLabel("×"))
        scale_radio_row.addWidget(self.gif_scale_y_spin)
        scale_radio_row.addWidget(QLabel("(0=uniform)"))
        scale_radio_row.addStretch()

        resize_sub.addLayout(resize_radio_row)
        resize_sub.addLayout(scale_radio_row)

        resize_row.addLayout(resize_sub)
        gif_opts_layout.addLayout(resize_row)

        self.gif_resize_mode_group = QButtonGroup(self)
        self.gif_resize_mode_group.addButton(self.gif_resize_radio, 0)
        self.gif_resize_mode_group.addButton(self.gif_scale_radio, 1)
        self.gif_resize_radio.setChecked(True)

        # --- Row 2: Colors ---
        colors_row = QHBoxLayout()
        self.gif_colors_cb = QCheckBox("Reduce Colors:")
        self.gif_colors_spin = QSpinBox()
        self.gif_colors_spin.setRange(2, 256)
        colors_row.addWidget(self.gif_colors_cb)
        colors_row.addWidget(self.gif_colors_spin)
        colors_row.addStretch()
        gif_opts_layout.addLayout(colors_row)

        # --- Row 3: Dither ---
        dither_row = QHBoxLayout()
        self.gif_dither_cb = QCheckBox("Dither:")
        self.gif_dither_combo = QComboBox()
        _dither_display = ["Floyd-Steinberg", "ro64", "o8", "o16", "o32", "o64", "Ordered", "Blue Noise", "Halftone"]
        _dither_values  = ["floyd-steinberg", "ro64", "o8", "o16", "o32", "o64", "ordered", "blue_noise", "halftone"]
        for display, val in zip(_dither_display, _dither_values):
            self.gif_dither_combo.addItem(display, val)
        dither_row.addWidget(self.gif_dither_cb)
        dither_row.addWidget(self.gif_dither_combo)
        dither_row.addStretch()
        gif_opts_layout.addLayout(dither_row)

        # --- Row 4: Remove Frames ---
        remove_row = QHBoxLayout()
        self.gif_remove_frames_cb = QCheckBox("Remove every")
        # Fix P: tooltip describes the frame-thinning effect on animated GIFs.
        self.gif_remove_frames_cb.setToolTip(
            "Keep only 1 in every N frames, discarding the rest. Reduces animated GIF file size at the cost of smoothness."
        )
        self.gif_remove_frames_n_spin = QSpinBox()
        self.gif_remove_frames_n_spin.setRange(2, 20)
        self.gif_remove_frames_combo = QComboBox()
        self.gif_remove_frames_combo.addItem("Odd frames (1, 3, 5…)", 1)
        self.gif_remove_frames_combo.addItem("Even frames (0, 2, 4…)", 0)
        remove_row.addWidget(self.gif_remove_frames_cb)
        remove_row.addWidget(self.gif_remove_frames_n_spin)
        remove_row.addWidget(QLabel("frames — keep:"))
        remove_row.addWidget(self.gif_remove_frames_combo)
        remove_row.addStretch()
        gif_opts_layout.addLayout(remove_row)

        # --- Row 5: Loop Count ---
        loopcount_row = QHBoxLayout()
        self.gif_loopcount_cb = QCheckBox("Set Loop Count:")
        self.gif_loopcount_forever_cb = QCheckBox("Forever")
        self.gif_loopcount_spin = QSpinBox()
        # Fix O: allow 0 so callers can explicitly request zero loops (play
        # once and stop).  The previous lower bound of 1 made 0 unreachable.
        self.gif_loopcount_spin.setRange(0, 65535)
        loopcount_row.addWidget(self.gif_loopcount_cb)
        loopcount_row.addWidget(self.gif_loopcount_forever_cb)
        loopcount_row.addWidget(self.gif_loopcount_spin)
        loopcount_row.addWidget(QLabel("times"))
        loopcount_row.addStretch()
        gif_opts_layout.addLayout(loopcount_row)

        # --- Row 6: Delay ---
        delay_row = QHBoxLayout()
        self.gif_delay_cb = QCheckBox("Set Delay:")
        self.gif_delay_spin = QSpinBox()
        self.gif_delay_spin.setRange(0, 65535)
        # Fix P: tooltip explains the centisecond unit and gives a practical example.
        self.gif_delay_spin.setToolTip(
            "Frame delay in hundredths of a second. Example: 10 = 0.1 s (10 fps)."
        )
        delay_row.addWidget(self.gif_delay_cb)
        delay_row.addWidget(self.gif_delay_spin)
        delay_row.addWidget(QLabel("hundredths of a second"))
        delay_row.addStretch()
        gif_opts_layout.addLayout(delay_row)

        # --- Row 7: Optimize ---
        optimize_row = QHBoxLayout()
        self.gif_optimize_cb = QCheckBox("Optimize:")
        self.gif_optimize_level_combo = QComboBox()
        self.gif_optimize_level_combo.addItem("Level 1", 1)
        self.gif_optimize_level_combo.addItem("Level 2", 2)
        self.gif_optimize_level_combo.addItem("Level 3", 3)
        self.gif_optimize_level_combo.setCurrentIndex(1)  # Level 2 default
        self.gif_optimize_keep_empty_cb = QCheckBox("Preserve Transparent Frames")
        optimize_row.addWidget(self.gif_optimize_cb)
        optimize_row.addWidget(self.gif_optimize_level_combo)
        optimize_row.addWidget(self.gif_optimize_keep_empty_cb)
        optimize_row.addStretch()
        gif_opts_layout.addLayout(optimize_row)

        # --- Row 8: UnOptimize ---
        unoptimize_row = QHBoxLayout()
        self.gif_unoptimize_cb = QCheckBox("UnOptimize")
        self.gif_unoptimize_cb.setToolTip(
            "Decompresses inter-frame optimizations. Disables the Optimize option above."
        )
        unoptimize_row.addWidget(self.gif_unoptimize_cb)
        unoptimize_row.addStretch()
        gif_opts_layout.addLayout(unoptimize_row)

        layout.addWidget(gif_options_box)

        # Signal wiring for GIF Options enable/disable
        self.gif_resize_cb.toggled.connect(self._on_gif_resize_toggled)
        self.gif_resize_radio.toggled.connect(self._on_gif_resize_mode_toggled)
        self.gif_colors_cb.toggled.connect(self.gif_colors_spin.setEnabled)
        self.gif_dither_cb.toggled.connect(self.gif_dither_combo.setEnabled)
        self.gif_remove_frames_cb.toggled.connect(self.gif_remove_frames_n_spin.setEnabled)
        self.gif_remove_frames_cb.toggled.connect(self.gif_remove_frames_combo.setEnabled)
        self.gif_loopcount_cb.toggled.connect(self._on_gif_loopcount_toggled)
        self.gif_loopcount_forever_cb.toggled.connect(self._on_gif_loopcount_forever_toggled)
        self.gif_delay_cb.toggled.connect(self.gif_delay_spin.setEnabled)
        self.gif_optimize_cb.toggled.connect(self._on_gif_optimize_toggled)
        self.gif_unoptimize_cb.toggled.connect(self._on_gif_unoptimize_toggled)

        # Initial disabled state (all sub-widgets disabled until their checkbox is checked)
        self.gif_resize_width_spin.setEnabled(False)
        self.gif_resize_height_spin.setEnabled(False)
        self.gif_scale_x_spin.setEnabled(False)
        self.gif_scale_y_spin.setEnabled(False)
        self.gif_resize_radio.setEnabled(False)
        self.gif_scale_radio.setEnabled(False)
        self.gif_colors_spin.setEnabled(False)
        self.gif_dither_combo.setEnabled(False)
        self.gif_remove_frames_n_spin.setEnabled(False)
        self.gif_remove_frames_combo.setEnabled(False)
        self.gif_loopcount_forever_cb.setEnabled(False)
        self.gif_loopcount_spin.setEnabled(False)
        self.gif_delay_spin.setEnabled(False)
        self.gif_optimize_level_combo.setEnabled(False)
        self.gif_optimize_keep_empty_cb.setEnabled(False)

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

        # --- GIF Options initial values ---
        gif_resize_enabled      = current_prefs.get('gif_resize_enabled', False)
        gif_resize_mode         = current_prefs.get('gif_resize_mode', 'resize')
        gif_resize_width        = current_prefs.get('gif_resize_width', 0)
        gif_resize_height       = current_prefs.get('gif_resize_height', 0)
        gif_scale_x             = current_prefs.get('gif_scale_x', 1.0)
        gif_scale_y             = current_prefs.get('gif_scale_y', 0.0)
        gif_colors_enabled      = current_prefs.get('gif_colors_enabled', False)
        gif_colors_num          = current_prefs.get('gif_colors_num', 256)
        gif_dither_enabled      = current_prefs.get('gif_dither_enabled', False)
        gif_dither_method       = current_prefs.get('gif_dither_method', 'floyd-steinberg')
        gif_remove_frames_enabled = current_prefs.get('gif_remove_frames_enabled', False)
        gif_remove_frames_n     = current_prefs.get('gif_remove_frames_n', 2)
        gif_remove_frames_offset = current_prefs.get('gif_remove_frames_offset', 0)
        gif_loopcount_enabled   = current_prefs.get('gif_loopcount_enabled', False)
        gif_loopcount_forever   = current_prefs.get('gif_loopcount_forever', True)
        gif_loopcount_value     = current_prefs.get('gif_loopcount_value', 1)
        gif_delay_enabled       = current_prefs.get('gif_delay_enabled', False)
        gif_delay_value         = current_prefs.get('gif_delay_value', 10)
        gif_optimize_enabled    = current_prefs.get('gif_optimize_enabled', False)
        gif_optimize_level      = current_prefs.get('gif_optimize_level', 2)
        gif_optimize_keep_empty = current_prefs.get('gif_optimize_keep_empty', False)
        gif_unoptimize_enabled  = current_prefs.get('gif_unoptimize_enabled', False)

        # Set widget values (block signals to avoid triggering enable/disable handlers)
        self.gif_resize_cb.blockSignals(True)
        self.gif_resize_cb.setChecked(gif_resize_enabled)
        self.gif_resize_cb.blockSignals(False)

        # Fix N: block signals on both radio buttons while setting the initial
        # checked state.  Without this the toggled() signal fires during
        # setChecked(), which calls _on_gif_resize_mode_toggled() before the
        # gif_resize_cb enabled-state is restored — leaving the spinboxes in
        # the wrong enabled/disabled state when the dialog opens.
        self.gif_resize_radio.blockSignals(True)
        self.gif_scale_radio.blockSignals(True)
        if gif_resize_mode == 'scale':
            self.gif_scale_radio.setChecked(True)
        else:
            self.gif_resize_radio.setChecked(True)
        self.gif_resize_radio.blockSignals(False)
        self.gif_scale_radio.blockSignals(False)

        self.gif_resize_width_spin.blockSignals(True)
        self.gif_resize_width_spin.setValue(gif_resize_width)
        self.gif_resize_width_spin.blockSignals(False)

        self.gif_resize_height_spin.blockSignals(True)
        self.gif_resize_height_spin.setValue(gif_resize_height)
        self.gif_resize_height_spin.blockSignals(False)

        self.gif_scale_x_spin.blockSignals(True)
        self.gif_scale_x_spin.setValue(gif_scale_x)
        self.gif_scale_x_spin.blockSignals(False)

        self.gif_scale_y_spin.blockSignals(True)
        self.gif_scale_y_spin.setValue(gif_scale_y)
        self.gif_scale_y_spin.blockSignals(False)

        self.gif_colors_cb.blockSignals(True)
        self.gif_colors_cb.setChecked(gif_colors_enabled)
        self.gif_colors_cb.blockSignals(False)

        self.gif_colors_spin.blockSignals(True)
        self.gif_colors_spin.setValue(gif_colors_num)
        self.gif_colors_spin.blockSignals(False)

        self.gif_dither_cb.blockSignals(True)
        self.gif_dither_cb.setChecked(gif_dither_enabled)
        self.gif_dither_cb.blockSignals(False)

        _dither_idx = self.gif_dither_combo.findData(gif_dither_method)
        self.gif_dither_combo.blockSignals(True)
        self.gif_dither_combo.setCurrentIndex(_dither_idx if _dither_idx >= 0 else 0)
        self.gif_dither_combo.blockSignals(False)

        self.gif_remove_frames_cb.blockSignals(True)
        self.gif_remove_frames_cb.setChecked(gif_remove_frames_enabled)
        self.gif_remove_frames_cb.blockSignals(False)

        self.gif_remove_frames_n_spin.blockSignals(True)
        self.gif_remove_frames_n_spin.setValue(gif_remove_frames_n)
        self.gif_remove_frames_n_spin.blockSignals(False)

        _offset_idx = self.gif_remove_frames_combo.findData(gif_remove_frames_offset)
        self.gif_remove_frames_combo.blockSignals(True)
        self.gif_remove_frames_combo.setCurrentIndex(_offset_idx if _offset_idx >= 0 else 0)
        self.gif_remove_frames_combo.blockSignals(False)

        self.gif_loopcount_cb.blockSignals(True)
        self.gif_loopcount_cb.setChecked(gif_loopcount_enabled)
        self.gif_loopcount_cb.blockSignals(False)

        self.gif_loopcount_forever_cb.blockSignals(True)
        self.gif_loopcount_forever_cb.setChecked(gif_loopcount_forever)
        self.gif_loopcount_forever_cb.blockSignals(False)

        self.gif_loopcount_spin.blockSignals(True)
        self.gif_loopcount_spin.setValue(gif_loopcount_value)
        self.gif_loopcount_spin.blockSignals(False)

        self.gif_delay_cb.blockSignals(True)
        self.gif_delay_cb.setChecked(gif_delay_enabled)
        self.gif_delay_cb.blockSignals(False)

        self.gif_delay_spin.blockSignals(True)
        self.gif_delay_spin.setValue(gif_delay_value)
        self.gif_delay_spin.blockSignals(False)

        self.gif_optimize_cb.blockSignals(True)
        self.gif_optimize_cb.setChecked(gif_optimize_enabled)
        self.gif_optimize_cb.blockSignals(False)

        _opt_level_idx = self.gif_optimize_level_combo.findData(gif_optimize_level)
        self.gif_optimize_level_combo.blockSignals(True)
        self.gif_optimize_level_combo.setCurrentIndex(_opt_level_idx if _opt_level_idx >= 0 else 1)
        self.gif_optimize_level_combo.blockSignals(False)

        self.gif_optimize_keep_empty_cb.blockSignals(True)
        self.gif_optimize_keep_empty_cb.setChecked(gif_optimize_keep_empty)
        self.gif_optimize_keep_empty_cb.blockSignals(False)

        self.gif_unoptimize_cb.blockSignals(True)
        self.gif_unoptimize_cb.setChecked(gif_unoptimize_enabled)
        self.gif_unoptimize_cb.blockSignals(False)

        # Restore enabled state based on loaded values
        self._on_gif_resize_toggled(gif_resize_enabled)
        self._on_gif_loopcount_toggled(gif_loopcount_enabled)
        if gif_loopcount_enabled:
            self._on_gif_loopcount_forever_toggled(gif_loopcount_forever)
        self.gif_colors_spin.setEnabled(gif_colors_enabled)
        self.gif_dither_combo.setEnabled(gif_dither_enabled)
        self.gif_remove_frames_n_spin.setEnabled(gif_remove_frames_enabled)
        self.gif_remove_frames_combo.setEnabled(gif_remove_frames_enabled)
        self.gif_delay_spin.setEnabled(gif_delay_enabled)
        if gif_unoptimize_enabled:
            self.gif_optimize_level_combo.setEnabled(False)
            self.gif_optimize_keep_empty_cb.setEnabled(False)
        else:
            self.gif_optimize_level_combo.setEnabled(gif_optimize_enabled)
            self.gif_optimize_keep_empty_cb.setEnabled(gif_optimize_enabled)

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
            'gif_resize_enabled': gif_resize_enabled,
            'gif_resize_mode': gif_resize_mode,
            'gif_resize_width': gif_resize_width,
            'gif_resize_height': gif_resize_height,
            'gif_scale_x': gif_scale_x,
            'gif_scale_y': gif_scale_y,
            'gif_colors_enabled': gif_colors_enabled,
            'gif_colors_num': gif_colors_num,
            'gif_dither_enabled': gif_dither_enabled,
            'gif_dither_method': gif_dither_method,
            'gif_remove_frames_enabled': gif_remove_frames_enabled,
            'gif_remove_frames_n': gif_remove_frames_n,
            'gif_remove_frames_offset': gif_remove_frames_offset,
            'gif_loopcount_enabled': gif_loopcount_enabled,
            'gif_loopcount_forever': gif_loopcount_forever,
            'gif_loopcount_value': gif_loopcount_value,
            'gif_delay_enabled': gif_delay_enabled,
            'gif_delay_value': gif_delay_value,
            'gif_optimize_enabled': gif_optimize_enabled,
            'gif_optimize_level': gif_optimize_level,
            'gif_optimize_keep_empty': gif_optimize_keep_empty,
            'gif_unoptimize_enabled': gif_unoptimize_enabled,
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
            'gif_resize_enabled': self.gif_resize_cb.isChecked(),
            'gif_resize_mode': 'scale' if self.gif_scale_radio.isChecked() else 'resize',
            'gif_resize_width': self.gif_resize_width_spin.value(),
            'gif_resize_height': self.gif_resize_height_spin.value(),
            'gif_scale_x': self.gif_scale_x_spin.value(),
            'gif_scale_y': self.gif_scale_y_spin.value(),
            'gif_colors_enabled': self.gif_colors_cb.isChecked(),
            'gif_colors_num': self.gif_colors_spin.value(),
            'gif_dither_enabled': self.gif_dither_cb.isChecked(),
            'gif_dither_method': self.gif_dither_combo.currentData(),
            'gif_remove_frames_enabled': self.gif_remove_frames_cb.isChecked(),
            'gif_remove_frames_n': self.gif_remove_frames_n_spin.value(),
            'gif_remove_frames_offset': self.gif_remove_frames_combo.currentData(),
            'gif_loopcount_enabled': self.gif_loopcount_cb.isChecked(),
            'gif_loopcount_forever': self.gif_loopcount_forever_cb.isChecked(),
            'gif_loopcount_value': self.gif_loopcount_spin.value(),
            'gif_delay_enabled': self.gif_delay_cb.isChecked(),
            'gif_delay_value': self.gif_delay_spin.value(),
            'gif_optimize_enabled': self.gif_optimize_cb.isChecked(),
            'gif_optimize_level': self.gif_optimize_level_combo.currentData(),
            'gif_optimize_keep_empty': self.gif_optimize_keep_empty_cb.isChecked(),
            'gif_unoptimize_enabled': self.gif_unoptimize_cb.isChecked(),
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

    def _on_gif_resize_toggled(self, enabled: bool) -> None:
        """Enable or disable all resize sub-widgets when the Resize checkbox is toggled.

        When enabled, the current radio button selection determines which set
        of dimension/scale spinboxes is active.  When disabled, all sub-widgets
        are unconditionally disabled.
        """
        self.gif_resize_radio.setEnabled(enabled)
        self.gif_scale_radio.setEnabled(enabled)
        if enabled:
            self._on_gif_resize_mode_toggled(self.gif_resize_radio.isChecked())
        else:
            self.gif_resize_width_spin.setEnabled(False)
            self.gif_resize_height_spin.setEnabled(False)
            self.gif_scale_x_spin.setEnabled(False)
            self.gif_scale_y_spin.setEnabled(False)

    def _on_gif_resize_mode_toggled(self, resize_checked: bool) -> None:
        """Switch active spinboxes between pixel dimensions and scale factors.

        Called whenever the "Resize to:" radio button's checked state changes.
        The ``gif_resize_radio`` ``toggled`` signal is emitted for both the
        newly-checked and the newly-unchecked button, so ``resize_checked``
        is ``True`` when "Resize to:" becomes active and ``False`` when it
        becomes inactive (i.e. "Scale by:" becomes active).
        """
        self.gif_resize_width_spin.setEnabled(resize_checked)
        self.gif_resize_height_spin.setEnabled(resize_checked)
        self.gif_scale_x_spin.setEnabled(not resize_checked)
        self.gif_scale_y_spin.setEnabled(not resize_checked)

    def _on_gif_loopcount_toggled(self, enabled: bool) -> None:
        """Enable or disable loop-count sub-widgets when the Loop Count checkbox is toggled.

        The loop count spinbox is additionally suppressed when the "Forever"
        checkbox is active, since an infinite loop has no numeric count.
        """
        self.gif_loopcount_forever_cb.setEnabled(enabled)
        self.gif_loopcount_spin.setEnabled(enabled and not self.gif_loopcount_forever_cb.isChecked())

    def _on_gif_loopcount_forever_toggled(self, forever: bool) -> None:
        """Hide the loop count spinbox when 'Forever' is checked.

        A forever loop needs no numeric value, so the spin box is disabled
        when this checkbox is active to avoid user confusion.
        """
        self.gif_loopcount_spin.setEnabled(not forever)

    def _on_gif_optimize_toggled(self, enabled: bool) -> None:
        """Enable optimize sub-widgets and mutually exclude UnOptimize.

        Optimize and UnOptimize are mutually exclusive gifsicle flags.
        Enabling Optimize programmatically unchecks UnOptimize (with signals
        blocked to avoid a re-entrant call into _on_gif_unoptimize_toggled).
        """
        self.gif_optimize_level_combo.setEnabled(enabled)
        self.gif_optimize_keep_empty_cb.setEnabled(enabled)
        if enabled:
            self.gif_unoptimize_cb.blockSignals(True)
            self.gif_unoptimize_cb.setChecked(False)
            self.gif_unoptimize_cb.blockSignals(False)

    def _on_gif_unoptimize_toggled(self, enabled: bool) -> None:
        """Disable optimize sub-widgets and mutually exclude Optimize.

        When UnOptimize is checked the optimize controls are disabled because
        gifsicle does not accept both flags simultaneously.  Enabling
        UnOptimize also programmatically unchecks Optimize (with signals
        blocked to avoid a re-entrant call into _on_gif_optimize_toggled).
        """
        # Fix M: the two setEnabled(False) calls that were duplicated inside
        # the `if enabled:` branch are removed.  The unconditional lines above
        # already set the correct state for both the enabled=True and
        # enabled=False cases via `setEnabled(not enabled)`.
        self.gif_optimize_level_combo.setEnabled(not enabled)
        self.gif_optimize_keep_empty_cb.setEnabled(not enabled)
        if enabled:
            self.gif_optimize_cb.blockSignals(True)
            self.gif_optimize_cb.setChecked(False)
            self.gif_optimize_cb.blockSignals(False)

    def done(self, result):
        """Save dialog size whenever the dialog closes, regardless of how it
        was dismissed (Save button, Cancel button, or window-manager close).

        Qt routes accept(), reject(), and closeEvent through done(), so this
        is the single correct place to persist state on close.
        """
        self.preferences.save_prefs_dialog_settings(self.width(), self.height())
        super().done(result)
