import subprocess

class BaseCompressor:
    def __init__(self):
        pass

    def run_command(self, cmd):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                pass  # Removed debug print statement
                pass  # Removed debug print statement
                return False
            return True
        except Exception as e:
            pass  # Removed debug print statement
            return False

    def compress_file(self, input_path, output_path, **kwargs):
        raise NotImplementedError
