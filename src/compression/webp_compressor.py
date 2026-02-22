# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright © 2026 Aries223 (https://github.com/aries223)
import logging
import os
import tempfile
from typing import Optional

from .base_compressor import BaseCompressor

logger = logging.getLogger(__name__)


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

    def compress_file(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        lossless: bool = False,
        strip_metadata: bool = False,
        webp_compression_level: Optional[int] = None,
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

        # Guard against filenames that start with a hyphen, which cwebp would
        # misinterpret as a flag.  cwebp does not support POSIX end-of-options
        # ("--") because "-o" must follow the positional input argument and
        # cwebp would treat it as a second positional file rather than the
        # output flag.  Rejecting such filenames is the correct mitigation.
        if os.path.basename(input_path).startswith("-"):
            self.last_error = (
                f"Refusing to process file with leading hyphen in name: {input_path!r}"
            )
            return False

        cmd.extend([input_path, "-o", effective_output])

        success = self.run_command(cmd)

        if in_place:
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
