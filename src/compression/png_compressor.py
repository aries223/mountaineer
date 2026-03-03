# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright © 2026 Aries223 (https://github.com/aries223)
import logging
from dataclasses import dataclass

from .base_compressor import BaseCompressor

logger = logging.getLogger(__name__)

_VALID_INTERLACE_TYPES = frozenset({'0', '1', 'keep'})


@dataclass
class PngOptions:
    """Configuration for PNG-specific oxipng options passed to PngCompressor.compress_file()."""

    force_8bit:        bool = False   # --scale16: reduce 16-bit channels to 8-bit
    zopfli:            bool = False   # --zopfli: use Zopfli algorithm (ignored in lossless mode)
    optimize_alpha:    bool = False   # --alpha: optimize alpha channel
    interlace_enabled: bool = False   # emit --interlace flag when True
    interlace_type:    str  = '0'     # '0'=remove, '1'=Adam7, 'keep'=preserve; validated against _VALID_INTERLACE_TYPES


class PngCompressor(BaseCompressor):
    def __init__(self):
        super().__init__()

    def _validate_quality(self, png_quality):
        """Validate and clamp png_quality to [0, 6].

        Returns the clamped integer value on success, or None on failure.
        On failure, sets self.last_error and logs the error before returning.
        """
        if png_quality is None:
            self.last_error = "png_quality must be provided for non-lossless compression"
            logger.error(self.last_error)
            return None
        try:
            return max(0, min(6, int(png_quality)))
        except (TypeError, ValueError):
            self.last_error = f"png_quality must be an integer in 0–6, got {png_quality!r}"
            logger.error(self.last_error)
            return None

    def _append_extra_flags(self, cmd, options, lossless):
        """Append optional oxipng flags to cmd based on PngOptions and lossless mode.

        Mutates cmd in place. Zopfli (--zopfli --fast) is suppressed when
        lossless=True because -Z in the lossless path already enables it.
        An invalid interlace_type is logged as a warning and the flag is skipped.
        """
        if options.force_8bit:
            cmd.append("--scale16")  # scales 16-bit channels down to 8-bit
        # Zopfli is skipped in lossless mode — -Z already enables it.
        if not lossless and options.zopfli:
            cmd.extend(["--zopfli", "--fast"])
        if options.optimize_alpha:
            cmd.append("--alpha")
        if options.interlace_enabled:
            if options.interlace_type in _VALID_INTERLACE_TYPES:
                cmd.extend(["--interlace", options.interlace_type])
            else:
                logger.warning(
                    "Invalid png_interlace_type %r; skipping --interlace flag",
                    options.interlace_type,
                )

    def compress_file(self, input_path, output_path=None, lossless=False,
                      strip_metadata=False, png_quality=None,
                      options=None):
        """Compress a PNG file using oxipng.

        In lossless mode, uses -omax -Z --fast for maximum lossless compression.
        In normal mode, uses -o<level> where level 0 is highest compression and
        6 is fastest (lowest compression).
        """
        if options is None:
            options = PngOptions()

        cmd = ["oxipng"]

        if lossless:
            cmd.extend(["-omax", "-Z", "--fast"])
        else:
            quality = self._validate_quality(png_quality)
            if quality is None:
                return False
            cmd.extend([f"-o{quality}", "-f", "0-9"])

        self._append_extra_flags(cmd, options, lossless)

        if strip_metadata:
            cmd.append("--strip=all")

        if output_path and output_path != input_path:
            cmd.extend(["--out", output_path])

        cmd.extend(["--", input_path])
        return self.run_command(cmd)
