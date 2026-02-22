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

    # Open (or create) the log file atomically at mode 0o600 so it is never
    # world-readable, even for the brief window between creation and a
    # subsequent chmod call.  os.O_APPEND ensures writes are safe across
    # re-opens.  os.fdopen wraps the raw fd as a text stream for StreamHandler.
    log_fd = os.open(log_file, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    file_handler = logging.StreamHandler(os.fdopen(log_fd, "a"))
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
        handlers=[
            file_handler,
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
