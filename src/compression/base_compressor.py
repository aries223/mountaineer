import logging
import subprocess

logger = logging.getLogger(__name__)


class BaseCompressor:
    def __init__(self):
        self.last_error = None

    def run_command(self, cmd):
        """Run a subprocess command, returning True on success.

        On failure, stores a human-readable reason in self.last_error and
        returns False. Distinguishes between a missing tool (FileNotFoundError)
        and a non-zero exit code so callers can show the right message.
        """
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.last_error = (
                    result.stderr.strip()
                    or f"Command exited with code {result.returncode}"
                )
                logger.warning(
                    "Command failed (code %d): %s\nstderr: %s",
                    result.returncode,
                    cmd,
                    self.last_error,
                )
                return False
            return True
        except FileNotFoundError:
            tool_name = cmd[0] if cmd else "unknown"
            self.last_error = (
                f"Tool not found: {tool_name}. Please install it and try again."
            )
            logger.error(self.last_error)
            return False
        except Exception as e:
            self.last_error = str(e)
            logger.exception("Unexpected error running command: %s", cmd)
            return False

    def compress_file(self, input_path, output_path, **kwargs):
        raise NotImplementedError
