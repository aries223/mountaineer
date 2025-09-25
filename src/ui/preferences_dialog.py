from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QSlider, QCheckBox, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt  # Import Qt for orientation setting
from utils.preferences import Preferences

class PreferencesDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Preferences")

        # Initialize preferences
        self.preferences = Preferences()

        layout = QVBoxLayout()

        # Initialize current_preferences dictionary
        self.current_preferences = {}

        # JPEG compression level
        jpeg_layout = QHBoxLayout()
        jpeg_label = QLabel("JPEG Compression Level:")
        self.jpeg_slider = QSlider(Qt.Orientation.Horizontal)  # Set to horizontal
        self.jpeg_value_label = QLabel("80")
        jpeg_layout.addWidget(jpeg_label)
        jpeg_layout.addWidget(self.jpeg_slider)
        jpeg_layout.addWidget(self.jpeg_value_label)

        # PNG compression level
        png_layout = QHBoxLayout()
        png_label = QLabel("PNG Compression Level:")
        self.png_slider = QSlider(Qt.Orientation.Horizontal)  # Set to horizontal
        self.png_value_label = QLabel("65")
        png_layout.addWidget(png_label)
        png_layout.addWidget(self.png_slider)
        png_layout.addWidget(self.png_value_label)

        layout.addLayout(jpeg_layout)
        layout.addLayout(png_layout)

        # Lossless compression checkbox
        self.lossless_checkbox = QCheckBox("Lossless Compression")

        # Strip metadata checkbox
        self.strip_metadata_checkbox = QCheckBox("Strip Metadata")

        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_preferences)

        layout.addWidget(self.lossless_checkbox)
        layout.addWidget(self.strip_metadata_checkbox)
        layout.addWidget(save_button)

        self.setLayout(layout)

        # Connect slider signals to update value labels
        self.jpeg_slider.valueChanged.connect(self.update_jpeg_value_label)
        self.png_slider.valueChanged.connect(self.update_png_value_label)

    def _set_initial_values(self):
        """Set initial values for sliders and checkboxes"""
        prefs = Preferences()
        current_prefs = prefs.load_preferences()

        jpeg_level = current_prefs.get('jpeg_compression_level', 80)
        png_level = current_prefs.get('png_compression_level', 65)
        lossless = current_prefs.get('lossless_compression', False)
        strip_metadata = current_prefs.get('strip_metadata', False)

        self.jpeg_slider.setValue(jpeg_level)
        self.update_jpeg_value_label(jpeg_level)

        self.png_slider.setValue(png_level)
        self.update_png_value_label(png_level)

        self.lossless_checkbox.setChecked(lossless)
        self.strip_metadata_checkbox.setChecked(strip_metadata)

    def save_preferences(self):
        prefs = Preferences()

        new_prefs = {
            'jpeg_compression_level': self.jpeg_slider.value(),
            'png_compression_level': self.png_slider.value(),
            'lossless_compression': self.lossless_checkbox.isChecked(),
            'strip_metadata': self.strip_metadata_checkbox.isChecked()
        }

        prefs.save_preferences(new_prefs)

        # Save preferences dialog position and size
        self.preferences.save_prefs_dialog_settings(
            self.x(),
            self.y(),
            self.width(),
            self.height()
        )

        # Update current preferences dictionary
        self.current_preferences = new_prefs

        print("Preferences saved")
        self.accept()

    def load_preferences(self):
        self._set_initial_values()  # Use the existing method to set initial values

    def update_jpeg_value_label(self, value):
        self.jpeg_value_label.setText(str(value))
        # Update preferences with current value
        self.current_preferences['jpeg_compression_level'] = value

    def update_png_value_label(self, value):
        self.png_value_label.setText(str(value))
        # Update preferences with current value
        self.current_preferences['png_compression_level'] = value

    def closeEvent(self, event):
        """Save window position and size when closing"""
        self.preferences.save_prefs_dialog_settings(
            self.x(),
            self.y(),
            self.width(),
            self.height()
        )
        super().closeEvent(event)
