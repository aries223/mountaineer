import logging
import os

from PIL import Image

logger = logging.getLogger(__name__)


def get_image_dimensions(file_path):
    """Return image dimensions as a 'WxH' string, or 'N/A' on error."""
    try:
        with Image.open(file_path) as img:
            return f"{img.width}x{img.height}"
    except Exception as e:
        logger.warning("Failed to get dimensions for %s: %s", file_path, e)
        return "N/A"


def get_file_size(file_path, human_readable=True):
    """Return file size as a human-readable string (e.g. '1.23 MB') or raw bytes."""
    try:
        if not os.path.isfile(file_path):
            return "0 B"

        size = os.path.getsize(file_path)
        if human_readable:
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    break
                size /= 1024.0
            return f"{size:.2f} {unit}"
        else:
            return size
    except Exception as e:
        logger.warning("Failed to get file size for %s: %s", file_path, e)
        return "0 B"


def get_file_format(file_path):
    """Return the image format string (e.g. 'JPEG', 'PNG'), or 'N/A' on error."""
    try:
        with Image.open(file_path) as img:
            return img.format.upper()
    except Exception as e:
        logger.warning("Failed to get format for %s: %s", file_path, e)
        return "N/A"
