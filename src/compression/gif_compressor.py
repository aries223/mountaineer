# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright © 2026 Aries223 (https://github.com/aries223)
import logging
from typing import Optional

from .base_compressor import BaseCompressor

logger = logging.getLogger(__name__)


class GifCompressor(BaseCompressor):
    """Compress GIF files using gifsicle.

    Both static and animated GIFs are handled natively by gifsicle.
    The compressor supports lossy and lossless modes as well as optional
    metadata stripping.
    """

    def __init__(self) -> None:
        super().__init__()

    def compress_file(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        lossless: bool = False,
        strip_metadata: bool = False,
        gif_lossy_level: Optional[int] = None,
    ) -> bool:
        """Compress a GIF file using gifsicle.

        In lossless mode the --lossy flag is omitted and the optimization level
        is lowered to -O2.  gifsicle's -O3 performs a frame-level rewriting
        pass that, even without --lossy, can introduce visible changes to
        palette and dithering; -O2 avoids that pass and is the safest
        "lossless" option gifsicle offers.  Note that neither mode produces
        output that is bit-for-bit identical to the original — -O2 without
        --lossy simply avoids any *explicit* lossy degradation.

        In lossy mode -O3 is used together with --lossy=N, which controls
        compression strength (0 = lossless quality, 200 = maximum lossy).
        Higher values produce smaller files at the cost of more visible
        artefacts.

        Animated GIFs are handled natively by gifsicle; all frames are
        processed in a single pass.

        When output_path is None or equal to input_path the file is rewritten
        in-place using gifsicle's --batch (-b) flag.  When output_path differs
        from input_path the result is written to that path instead.

        Args:
            input_path: Absolute path to the source GIF file.
            output_path: Destination path, or None to rewrite in-place.
            lossless: When True, use -O2 without --lossy to avoid explicit
                lossy degradation.  When False, use -O3 with --lossy=N.
            strip_metadata: When True, strip GIF comments, extensions, and
                named blocks via --no-comments --no-extensions --no-names.
                WARNING: --no-extensions also removes the Netscape 2.0
                application extension that encodes the loop count for animated
                GIFs.  After metadata stripping, animated GIFs will play once
                and then stop looping.
            gif_lossy_level: Lossy compression strength (0–200).  Required
                when lossless is False; ignored when lossless is True.
                Values are clamped to [0, 200] before use.

        Returns:
            True on success, False on failure (details in self.last_error).
        """
        if not lossless and gif_lossy_level is None:
            self.last_error = (
                "gif_lossy_level must be provided for non-lossless compression"
            )
            logger.error(self.last_error)
            return False

        # Use -O2 in lossless mode to avoid the frame-rewriting pass that
        # -O3 performs.  In lossy mode -O3 is appropriate because --lossy
        # already accepts quality loss as a trade-off for smaller output.
        optimization_level = "-O2" if lossless else "-O3"
        cmd = ["gifsicle", optimization_level]

        if not lossless:
            # Clamp to the valid gifsicle range before constructing the flag.
            gif_lossy_level = max(0, min(200, int(gif_lossy_level)))  # type: ignore[arg-type]
            cmd.append(f"--lossy={gif_lossy_level}")

        if strip_metadata:
            # gifsicle metadata-stripping flags:
            #   --no-comments  removes GIF comment extensions
            #   --no-extensions removes all application/unknown extensions
            #   --no-names     removes per-frame name extensions
            cmd.extend(["--no-comments", "--no-extensions", "--no-names"])

        if output_path and output_path != input_path:
            cmd.extend(["--output", output_path])
        else:
            # --batch rewrites the file in-place; handles both static and
            # animated GIFs without requiring a separate temp file.
            cmd.append("--batch")

        cmd.extend(["--", input_path])

        return self.run_command(cmd)
