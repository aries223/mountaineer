# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright © 2026 Aries223 (https://github.com/aries223)
import logging
import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout

logger = logging.getLogger(__name__)


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Mountaineer")

        layout = QVBoxLayout()

        # Try installed path first, then fall back to the source-relative logo
        logo_candidates = [
            '/usr/share/pixmaps/mountaineer.svg',
            os.path.join(os.path.dirname(__file__), 'logo', 'mountaineer.svg'),
        ]
        logo_path = next((p for p in logo_candidates if os.path.exists(p)), None)

        if logo_path:
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            # QPixmap.isNull() is True when the file could not be loaded.
            # QPixmap does not raise exceptions on failure, so no try/except
            # is needed here.
            if not pixmap.isNull():
                logo_label.setPixmap(pixmap.scaledToHeight(300))
                layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
            else:
                logger.warning("QPixmap returned null for logo at %s", logo_path)

        about_text = """
<center><h1>Mountaineer</h1>
A high quality image compression utility<br/>
for photographers and designers.<br/>
<p><b>Version:</b> 1.2.1<br/></p>
<p>©2025-2026 aries223</p></center>
"""

        text_label = QLabel(about_text)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text_label)

        # Use a standard QLabel with setOpenExternalLinks so the system browser
        # is invoked automatically.  This also adapts the link colour to the
        # active Qt palette, avoiding a hardcoded colour that looks wrong on
        # dark themes.
        github_label = QLabel('<a href="https://mountaineer-app.com/">mountaineer-app.com</a>')
        github_label.setOpenExternalLinks(True)
        github_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(github_label)

        self.setLayout(layout)
