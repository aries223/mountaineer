# File: utils/signals.py

from PyQt6.QtCore import pyqtSignal, QObject

class CompressionSignals(QObject):
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    compression_complete = pyqtSignal(str)
    compression_result_updated = pyqtSignal(int, str, float)  # New signal for compression results

signals = CompressionSignals()
