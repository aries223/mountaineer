# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright © 2026 Aries223 (https://github.com/aries223)
import logging
import subprocess

logger = logging.getLogger(__name__)


def _sanitise_for_log(value: str) -> str:
    """Replace control characters in a string to prevent log injection."""
    return "".join(
        c if c.isprintable() else f"<0x{ord(c):02X}>"
        for c in value
    )


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
                    [_sanitise_for_log(str(arg)) for arg in cmd],
                    _sanitise_for_log(self.last_error),
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
