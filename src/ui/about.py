from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QWidget
from PyQt6.QtGui import QPixmap  # Import for handling images
from PyQt6.QtCore import Qt, QUrl  # Import Qt for alignment and QUrl for URLs
import os

class ClickableLabel(QLabel):
    def __init__(self, text, url, parent=None):
        super().__init__(text, parent)
        self.url = url
        self.setOpenExternalLinks(False)  # Disable automatic link handling
        self.setTextFormat(Qt.TextFormat.RichText)  # Enable rich text formatting

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            import webbrowser
            webbrowser.open(self.url.toString())
        else:
            super().mousePressEvent(event)

class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About Mountaineer")

        layout = QVBoxLayout()

        # Direct path for the logo image
        logo_path = '/usr/share/pixmaps/mountaineer.png'

        # Display logo if found with proper error handling
        if os.path.exists(logo_path):
            try:
                logo_label = QLabel()
                pixmap = QPixmap(logo_path)
                logo_label.setPixmap(pixmap.scaledToHeight(300))  # Scale logo height to 100 pixels
                layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignCenter)  # Center align the logo
            except Exception:
                pass  # Handle exception without printing debug info

        about_text = """
<center><h1>Mountaineer</h1>
A powerful image compression tool for <br/>
photographers and designers.<br/>
<p><b>Version:</b> 1.0.2<br/></p>
<p>©aries223 2025</p></center>
"""

        text_label = QLabel(about_text)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center align the text
        layout.addWidget(text_label)

        # Create a clickable GitHub label with HTML styling for link appearance
        github_url = QUrl("https://github.com/aries223/mountaineer")
        github_label = ClickableLabel(
            '<a href="#" style="color: #2a83d9">GitHub</a>',
            github_url
        )
        github_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center align the text

        layout.addWidget(github_label)

        self.setLayout(layout)
