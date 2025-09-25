import os
from PIL import Image

def get_image_dimensions(file_path):
    try:
        with Image.open(file_path) as img:
            return f"{img.width}x{img.height}"
    except Exception as e:
        print(f"Error getting dimensions: {e}")
        return "N/A"

def get_file_size(file_path, human_readable=True):
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
        print(f"Error getting file size for {file_path}: {e}")
        return "0 B"

def get_file_format(file_path):
    try:
        with Image.open(file_path) as img:
            return img.format.upper()
    except Exception as e:
        print(f"Error getting format: {e}")
        return "N/A"
