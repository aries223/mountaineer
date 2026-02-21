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

        In lossless mode the --lossy flag is omitted entirely so that no
        quality is sacrificed.  In lossy mode --lossy=N controls compression
        strength (0 = lossless quality, 200 = maximum lossy).  Higher values
        produce smaller files at the cost of more visible artefacts.

        Animated GIFs are handled natively by gifsicle; all frames are
        processed in a single pass.

        When output_path is None or equal to input_path the file is rewritten
        in-place using gifsicle's --batch (-b) flag.  When output_path differs
        from input_path the result is written to that path instead.

        Args:
            input_path: Absolute path to the source GIF file.
            output_path: Destination path, or None to rewrite in-place.
            lossless: When True, skip the --lossy flag entirely.
            strip_metadata: When True, strip GIF comments, extensions, and
                named blocks via --no-comments --no-extensions --no-names.
            gif_lossy_level: Lossy compression strength (0–200).  Required
                when lossless is False; ignored when lossless is True.

        Returns:
            True on success, False on failure (details in self.last_error).
        """
        if not lossless and gif_lossy_level is None:
            self.last_error = (
                "gif_lossy_level must be provided for non-lossless compression"
            )
            logger.error(self.last_error)
            return False

        cmd = ["gifsicle", "-O3"]

        if not lossless:
            cmd.append(f"--lossy={int(gif_lossy_level)}")  # type: ignore[arg-type]

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

        cmd.append(input_path)

        return self.run_command(cmd)
