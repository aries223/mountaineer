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

    # Pre-create the log file with restricted permissions (0600) so it is
    # never world-readable.  We create it via os.open with O_CREAT, then
    # close the fd immediately.  FileHandler will re-open the existing file
    # by name — it does not change the permissions of an existing file, so
    # the 0600 mode is preserved.
    fd = os.open(log_file, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    os.close(fd)

    file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s"))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stderr_handler)


def main():
    _setup_logging()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
