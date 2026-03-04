# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright © 2026 Aries223 (https://github.com/aries223)
import logging
import os
from dataclasses import dataclass
from typing import Optional

from .base_compressor import BaseCompressor

logger = logging.getLogger(__name__)


@dataclass
class JpegOptions:
    """Configuration for JPEG-specific jpegoptim options passed to JpegCompressor.compress_file().

    Attributes:
        target_size_enabled: Emit --size when True (lossy only).
        target_size_value:   Numeric value in target_size_unit.
        target_size_unit:    'KB' or 'MB'; converted to KB for jpegoptim.
        auto_progressive:    Use --auto-mode (mutually exclusive with all_progressive).
        all_progressive:     Use --all-progressive (mutually exclusive with auto_progressive).
                             If neither auto_progressive nor all_progressive: --all-normal is applied.
    """
    target_size_enabled: bool = False
    target_size_value:   int  = 500
    target_size_unit:    str  = 'KB'
    auto_progressive:    bool = False
    all_progressive:     bool = False


class JpegCompressor(BaseCompressor):
    def __init__(self):
        super().__init__()

    def compress_file(self, input_path, output_path=None, lossless=False,
                     strip_metadata=False, jpeg_quality=None,
                     options: Optional[JpegOptions] = None):
        """Compress a JPEG file using jpegoptim.

        In lossless mode, performs a lossless repack using --optimize without
        re-encoding.  In lossy mode, uses -m<quality> to set the output quality
        (0-100).

        Progressive mode is controlled by ``options``: --auto-mode, --all-progressive,
        or --all-normal (the default when neither flag is set).  Target-size compression
        is lossy only; the flag is silently skipped with a warning in lossless mode.

        Args:
            input_path:     Path to the source JPEG file.
            output_path:    Destination path.  If None or equal to input_path,
                            jpegoptim overwrites in place.
            lossless:       When True, use --optimize (lossless repack).
            strip_metadata: When True, append --strip-all.
            jpeg_quality:   Quality level 0-100.  Required when lossless=False.
            options:        JPEG-specific options.  Defaults to JpegOptions().

        Returns:
            True on success, False on any failure (sets self.last_error).
        """
        if options is None:
            options = JpegOptions()

        if jpeg_quality is None and not lossless:
            self.last_error = "jpeg_quality must be provided for non-lossless compression"
            logger.error(self.last_error)
            return False

        if os.path.basename(input_path).startswith("-"):
            self.last_error = (
                f"Refusing to process file with leading hyphen in name: {input_path!r}"
            )
            logger.error(self.last_error)
            return False

        cmd = ["jpegoptim"]

        if lossless:
            cmd.append("--optimize")
        else:
            jpeg_quality = max(0, min(100, int(jpeg_quality)))
            cmd.extend(["-f", f"-m{jpeg_quality}"])

        # Progressive mode applies in both lossless and lossy modes.
        # Default is --all-normal when neither progressive option is set.
        if options.auto_progressive:
            cmd.append("--auto-mode")
        elif options.all_progressive:
            cmd.append("--all-progressive")
        else:
            cmd.append("--all-normal")

        # Target size is lossy only; silently skip with warning if lossless=True.
        if options.target_size_enabled:
            if lossless:
                logger.warning(
                    "JPEG target_size is ignored in lossless mode; skipping --size flag"
                )
            else:
                multiplier = {'KB': 1, 'MB': 1024}.get(options.target_size_unit, 1)
                size_kb = options.target_size_value * multiplier
                cmd.append(f"--size={size_kb}")

        if strip_metadata:
            cmd.append("--strip-all")

        if output_path and output_path != input_path:
            cmd.extend(["--dest", os.path.dirname(os.path.abspath(output_path))])

        cmd.extend(["--", input_path])

        return self.run_command(cmd)
