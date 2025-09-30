import tempfile
import os

class TempFileManager:
    def __init__(self):
        self.temp_files = []

    def create_temp_file(self, suffix=''):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        self.temp_files.append(temp_file.name)
        return temp_file.name

    def cleanup(self):
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    pass  # Removed debug print statement
        self.temp_files.clear()
