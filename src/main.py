# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright © 2026 Aries223 (https://github.com/aries223)
import logging
import os
import sys

from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow


def _setup_logging():
    """Configure logging to write to ~/.mountaineer/mountaineer.log and stderr."""
    log_dir = os.path.expanduser("~/.mountaineer")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "mountaineer.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stderr),
        ],
    )


def main():
    _setup_logging()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
