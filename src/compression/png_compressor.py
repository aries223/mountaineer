# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright © 2026 Aries223 (https://github.com/aries223)
import logging

from .base_compressor import BaseCompressor

logger = logging.getLogger(__name__)


class PngCompressor(BaseCompressor):
    def __init__(self):
        super().__init__()

    def compress_file(self, input_path, output_path=None, lossless=False,
                     strip_metadata=False, png_quality=None, is_rgba=False):
        """Compress a PNG file using oxipng.

        In lossless mode, uses -omax -Z --fast for maximum lossless compression.
        In normal mode, uses -o<level> where level 0 is highest compression and
        6 is fastest (lowest compression).
        """
        cmd = ["oxipng"]

        if lossless:
            cmd.extend(["-omax", "-Z", "--fast"])
        else:
            if png_quality is None:
                self.last_error = "png_quality must be provided for non-lossless compression"
                logger.error(self.last_error)
                return False
            cmd.extend([f"-o{int(png_quality)}", "-f", "0-9"])

        if strip_metadata:
            cmd.append("--strip=all")

        if is_rgba:
            cmd.append("-a")

        if output_path and output_path != input_path:
            cmd.extend(["--out", output_path])

        cmd.append(input_path)

        return self.run_command(cmd)
