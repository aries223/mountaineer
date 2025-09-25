import subprocess

class BaseCompressor:
    def __init__(self):
        pass

    def run_command(self, cmd):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Command failed: {' '.join(cmd)}")
                print(f"Error: {result.stderr}")
                return False
            return True
        except Exception as e:
            print(f"Exception running command: {e}")
            return False

    def compress_file(self, input_path, output_path, **kwargs):
        raise NotImplementedError
