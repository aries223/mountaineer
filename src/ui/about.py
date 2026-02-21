import logging
import os

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout

logger = logging.getLogger(__name__)


class ClickableLabel(QLabel):
    def __init__(self, text, url, parent=None):
        super().__init__(text, parent)
        self.url = url
        self.setOpenExternalLinks(False)
        self.setTextFormat(Qt.TextFormat.RichText)

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

        # Try installed path first, then fall back to the source-relative logo
        logo_candidates = [
            '/usr/share/pixmaps/mountaineer.png',
            os.path.join(os.path.dirname(__file__), 'logo', 'mountaineer.png'),
        ]
        logo_path = next((p for p in logo_candidates if os.path.exists(p)), None)

        if logo_path:
            try:
                logo_label = QLabel()
                pixmap = QPixmap(logo_path)
                logo_label.setPixmap(pixmap.scaledToHeight(300))
                layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
            except Exception:
                logger.warning("Failed to load logo from %s", logo_path)

        about_text = """
<center><h1>Mountaineer</h1>
A powerful image compression tool for <br/>
photographers and designers.<br/>
<p><b>Version:</b> 1.1.0<br/></p>
<p>©aries223 2025</p></center>
"""

        text_label = QLabel(about_text)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text_label)

        github_url = QUrl("https://github.com/aries223/mountaineer")
        github_label = ClickableLabel(
            '<a href="#" style="color: #2a83d9">GitHub</a>',
            github_url,
        )
        github_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(github_label)

        self.setLayout(layout)
