# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright © 2026 Aries223 (https://github.com/aries223)
import logging
import os
import tempfile
from dataclasses import dataclass
from typing import Optional

from .base_compressor import BaseCompressor

logger = logging.getLogger(__name__)

_UNIT_MULTIPLIERS = {'KB': 1024, 'MB': 1048576}
_VALID_RESIZE_MODES = frozenset({'down_only', 'up_only', 'always'})


@dataclass
class WebpOptions:
    """Configuration for WebP-specific cwebp options passed to WebpCompressor.compress_file()."""
    crop_enabled:        bool = False
    crop_x:              int  = 0
    crop_y:              int  = 0
    crop_width:          int  = 0
    crop_height:         int  = 0
    resize_enabled:      bool = False
    resize_width:        int  = 0
    resize_height:       int  = 0
    resize_mode:         str  = 'always'
    target_size_enabled: bool = False
    target_size_value:   int  = 100
    target_size_unit:    str  = 'KB'
    passes_enabled:      bool = False   # only applied when target_size_enabled is also True
    passes:              int  = 6
    auto_filter:         bool = False
    jpeg_like:           bool = False


class WebpCompressor(BaseCompressor):
    """Compress WebP files using cwebp.

    cwebp cannot read from and write to the same path, so in-place
    compression is handled by writing to a temporary file in the same
    directory and then atomically replacing the original via os.replace().
    Placing the temp file in the same directory guarantees that both paths
    are on the same filesystem, making os.replace() a true atomic rename.
    """

    def __init__(self) -> None:
        super().__init__()

    def _atomic_replace(self, tmp_path: str, input_path: str, success: bool) -> bool:
        """Finalise an in-place compression attempt using a temporary file.

        On success, atomically replaces *input_path* with *tmp_path* via
        ``os.replace()``.  Both paths must live on the same filesystem (ensured
        by the caller) so the rename is guaranteed to be atomic.

        On failure, removes *tmp_path* so no orphaned temporary files remain.

        Args:
            tmp_path: Absolute path to the temporary file written by cwebp.
            input_path: Absolute path to the original file to be replaced.
            success: Whether the cwebp subprocess completed without error.

        Returns:
            True when the replacement succeeds, False on any filesystem error
            or when *success* is False (details written to ``self.last_error``).
        """
        if success:
            try:
                os.replace(tmp_path, input_path)
            except Exception as exc:
                self.last_error = f"Failed to replace original file: {exc}"
                logger.error(self.last_error)
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                return False
        else:
            # Clean up the temp file on failure so no orphaned files remain.
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

        return success

    def _append_options_flags(self, cmd: list, options: WebpOptions) -> None:
        """Append cwebp flags derived from *options* to *cmd* in place.

        Flag order: crop → resize → target size → passes → auto filter → jpeg_like.
        Crop is applied before resize per cwebp semantics.
        """
        if options.crop_enabled:
            if options.crop_width == 0 or options.crop_height == 0:
                logger.warning(
                    "WebP crop skipped: crop_width and crop_height must both be > 0"
                )
            else:
                cmd.extend([
                    "-crop",
                    str(options.crop_x),
                    str(options.crop_y),
                    str(options.crop_width),
                    str(options.crop_height),
                ])

        if options.resize_enabled:
            if options.resize_width == 0 and options.resize_height == 0:
                logger.warning(
                    "WebP resize skipped: at least one of resize_width or resize_height must be > 0"
                )
            else:
                resize_mode = options.resize_mode
                if resize_mode not in _VALID_RESIZE_MODES:
                    logger.warning(
                        "WebP resize_mode %r is invalid; falling back to 'always'",
                        resize_mode,
                    )
                    resize_mode = 'always'
                cmd.extend(["-resize", str(options.resize_width), str(options.resize_height)])
                if resize_mode == 'down_only':
                    cmd.append("-resize_down")
                elif resize_mode == 'up_only':
                    cmd.append("-resize_up")

        if options.target_size_enabled:
            if options.target_size_unit not in _UNIT_MULTIPLIERS:
                logger.warning(
                    "WebP target_size_unit %r is invalid; falling back to 'KB'",
                    options.target_size_unit,
                )
                unit = 'KB'
            else:
                unit = options.target_size_unit
            target_bytes = options.target_size_value * _UNIT_MULTIPLIERS[unit]
            cmd.extend(["-size", str(target_bytes)])

            if options.passes_enabled:
                cmd.extend(["-pass", str(options.passes)])

        if options.auto_filter:
            cmd.append("-af")

        if options.jpeg_like:
            cmd.append("-jpeg_like")

    def compress_file(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        lossless: bool = False,
        strip_metadata: bool = False,
        webp_compression_level: Optional[int] = None,
        options: Optional[WebpOptions] = None,
    ) -> bool:
        """Compress a WebP file using cwebp.

        When output_path is None or equals input_path (in-place mode), the
        compressed data is written to a temporary file in the same directory,
        then the original is atomically replaced with os.replace().

        cwebp flags used:
            -lossless       Enable lossless encoding mode.
            -q N            Quality factor (0–100; higher means better quality
                            and larger file size).  Ignored in lossless mode by
                            cwebp, but still passed for consistency.
            -metadata none  Strip all embedded metadata (Exif, ICC, XMP).

        Args:
            input_path: Absolute path to the source WebP file.
            output_path: Destination path, or None to rewrite in-place.
            lossless: When True, pass -lossless to cwebp.
            strip_metadata: When True, pass -metadata none to strip all
                embedded metadata blocks.
            webp_compression_level: Quality factor (0–100).  Required when
                lossless is False; used even in lossless mode for the -q flag.

        Returns:
            True on success, False on failure (details in self.last_error).
        """
        if not lossless and webp_compression_level is None:
            self.last_error = (
                "webp_compression_level must be provided for non-lossless compression"
            )
            logger.error(self.last_error)
            return False

        in_place = output_path is None or output_path == input_path

        # Guard against filenames that start with a hyphen, which cwebp would
        # misinterpret as a flag.  cwebp does not support POSIX end-of-options
        # ("--") because "-o" must follow the positional input argument and
        # cwebp would treat it as a second positional file rather than the
        # output flag.  Rejecting such filenames is the correct mitigation.
        # This check must come before the temp-file creation block so that no
        # orphaned temp file is left on disk when the path is rejected.
        if os.path.basename(input_path).startswith("-"):
            self.last_error = (
                f"Refusing to process file with leading hyphen in name: {input_path!r}"
            )
            logger.error(self.last_error)
            return False

        if in_place:
            # Create the temp file in the same directory as the source so that
            # os.replace() is guaranteed to be an atomic same-filesystem rename.
            try:
                tmp_fd, tmp_path = tempfile.mkstemp(
                    suffix=".webp",
                    dir=os.path.dirname(os.path.abspath(input_path)),
                )
                os.close(tmp_fd)
            except OSError as exc:
                self.last_error = f"Could not create temporary file: {exc}"
                logger.error(self.last_error)
                return False
            effective_output = tmp_path
        else:
            effective_output = output_path  # type: ignore[assignment]

        cmd = ["cwebp"]

        if lossless:
            cmd.append("-lossless")

        # Use provided quality level; fall back to 80 when lossless=True and
        # no level was supplied so the -q flag is always present.  Clamp to
        # [0, 100] — the valid range accepted by cwebp — before use.
        quality = int(webp_compression_level if webp_compression_level is not None else 80)
        webp_compression_level = max(0, min(100, quality))
        cmd.extend(["-q", str(webp_compression_level)])

        if strip_metadata:
            cmd.extend(["-metadata", "none"])

        if options is None:
            options = WebpOptions()
        self._append_options_flags(cmd, options)

        cmd.extend([input_path, "-o", effective_output])

        success = self.run_command(cmd)

        if in_place:
            return self._atomic_replace(tmp_path, input_path, success)

        return success
