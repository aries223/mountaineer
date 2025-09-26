# File: src/ui/about.py

from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QWidget
from PyQt6.QtGui import QPixmap  # Import for handling images
from PyQt6.QtCore import Qt  # Import Qt for alignment
import os

class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About Mountaineer")

        layout = QVBoxLayout()

        # Try multiple potential paths for the logo image with better error handling
        logo_path = None
        potential_paths = [
            '../src/ui/logo/mountaineer.png',  # Relative to project root
            'logo/mountaineer.png',             # Alternative relative path
            '/home/chris/VCoding/Mountaineer/src/ui/logo/mountaineer.png'  # Absolute path (update as needed)
        ]

        for path in potential_paths:
            if os.path.exists(path):
                logo_path = path
                break

        # Display logo if found with proper error handling
        if logo_path and os.path.exists(logo_path):
            try:
                logo_label = QLabel()
                pixmap = QPixmap(logo_path)
                logo_label.setPixmap(pixmap.scaledToHeight(100))  # Scale logo height to 100 pixels
                layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignCenter)  # Center align the logo
            except Exception as e:
                print(f"Error loading logo image: {e}")
        else:
            print("Logo image not found at expected paths")

        about_text = """
<center><h1>Mountaineer</h1>
A powerful image compression tool for photographers and designers.<br/>
<p><b>Version:</b> 1.0<br/></p>
<p>©Chris Rexinger 2025</p>
<br/>
<a href="https://github.com/aries223/mountaineer">GitHub</a></p></center>
"""

        text_label = QLabel(about_text)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center align the text
        layout.addWidget(text_label)

        self.setLayout(layout)
