# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright © 2026 Aries223 (https://github.com/aries223)
import logging
import os

from .base_compressor import BaseCompressor

logger = logging.getLogger(__name__)


class JpegCompressor(BaseCompressor):
    def __init__(self):
        super().__init__()

    def compress_file(self, input_path, output_path=None, lossless=False,
                     strip_metadata=False, jpeg_quality=None):
        """Compress a JPEG file using jpegoptim.

        In lossless mode, performs a lossless repack using --optimize and
        --all-progressive without re-encoding. In lossy mode, uses -m<quality>
        to set the output quality (0–100).
        """
        if jpeg_quality is None and not lossless:
            self.last_error = "jpeg_quality must be provided for non-lossless compression"
            logger.error(self.last_error)
            return False

        cmd = ["jpegoptim"]

        if lossless:
            cmd.extend(["--optimize", "--all-progressive"])
        else:
            jpeg_quality = max(0, min(100, int(jpeg_quality)))
            cmd.extend(["-f", f"-m{jpeg_quality}"])

        if strip_metadata:
            cmd.append("--strip-all")

        if output_path and output_path != input_path:
            cmd.extend(["--dest", os.path.dirname(os.path.abspath(output_path))])

        cmd.extend(["--", input_path])

        return self.run_command(cmd)
