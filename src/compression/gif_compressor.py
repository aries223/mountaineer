# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright © 2026 Aries223 (https://github.com/aries223)
import logging
import os
import subprocess
import tempfile
from typing import List, Optional, Tuple

from .base_compressor import BaseCompressor

logger = logging.getLogger(__name__)

# Fix C: allowlist of dither method strings accepted by gifsicle's --dither flag.
# 'floyd-steinberg' is the default and is emitted as bare --dither (no suffix).
# All other values are emitted as --dither=<method>.
_VALID_DITHER_METHODS = frozenset({
    'floyd-steinberg', 'ro64', 'o8', 'o16', 'o32', 'o64',
    'ordered', 'blue_noise', 'halftone',
})


class GifCompressor(BaseCompressor):
    """Compress GIF files using gifsicle.

    Both static and animated GIFs are handled natively by gifsicle.
    The compressor supports lossy and lossless modes as well as optional
    metadata stripping.
    """

    def __init__(self) -> None:
        super().__init__()

    def _get_frame_count(self, input_path: str) -> int:
        """Return the number of frames in a GIF file using gifsicle --info.

        Returns -1 if the frame count cannot be determined (e.g. gifsicle
        not found, file unreadable, or output not parseable).
        """
        try:
            result = subprocess.run(
                ['gifsicle', '--info', input_path],
                capture_output=True, text=True,
            )
            if result.returncode != 0:
                return -1
            # First non-empty line: "* filename N images" or "* filename 1 image"
            for line in result.stdout.splitlines():
                parts = line.split()
                for i, part in enumerate(parts):
                    if part in ('image', 'images') and i > 0:
                        try:
                            return int(parts[i - 1])
                        except ValueError:
                            pass
            return -1
        except Exception:
            return -1

    # ---------------------------------------------------------------------- #
    # Private helpers — each handles one logical step of compress_file().     #
    # All helpers that mutate cmd accept it as the first argument and modify  #
    # it in-place.  Helpers that can abort return False and set self.last_error
    # before returning; helpers that cannot abort return None.                #
    # ---------------------------------------------------------------------- #

    def _apply_optimization_flags(
        self,
        cmd: List[str],
        lossless: bool,
        unoptimize_enabled: bool,
        optimize_enabled: bool,
        optimize_level: int,
        optimize_keep_empty: bool,
        remove_frames_enabled: bool,
    ) -> None:
        """Append unoptimize / optimization-level flags to cmd (Steps 1b + 2).

        Step 1b — unoptimize guard for frame removal:
        Most animated GIFs use inter-frame delta encoding: each frame stores
        only the pixels that changed from the previous one.  Removing frames
        without first expanding those deltas corrupts every delta-encoded
        frame that followed a removed frame.  Inserting --unoptimize before
        the frame selectors (but before the -O re-optimisation flag) forces
        gifsicle to expand every frame to a full image before selection,
        then the -O flag re-optimises the chosen frames in the output.
        If unoptimize_enabled is already True, Step 2 will add --unoptimize
        and the -O flag is intentionally omitted (the user wants raw output).

        Step 2 — three-way mutual exclusion:
        - unoptimize_enabled: expand a previously-optimised GIF; no -O flag
          is appropriate alongside --unoptimize.
        - optimize_enabled: honour the caller's explicit optimisation level.
        - default: -O2 for lossless work; -O3 paired with --lossy.
        """
        if remove_frames_enabled and not unoptimize_enabled:
            cmd.append("--unoptimize")

        if unoptimize_enabled:
            # Expand a previously-optimised GIF; no -O flag is appropriate
            # alongside --unoptimize because the purpose is the opposite of
            # optimisation.
            cmd.append("--unoptimize")
        elif optimize_enabled:
            # Caller has explicitly chosen an optimisation level; honour it
            # instead of the automatic -O2/-O3 selection.
            # Fix G: clamp optimize_level to the valid gifsicle range (1–3)
            # at the point of use so stale or out-of-range stored values are
            # never forwarded to the subprocess.
            clamped_level = max(1, min(3, int(optimize_level)))
            # Fix A: --optimize=keep-empty must be a comma-separated suffix on
            # the same --optimize flag, not a second --optimize flag.  Passing
            # two separate --optimize flags causes gifsicle to ignore the first.
            if optimize_keep_empty:
                cmd.append(f"--optimize={clamped_level},keep-empty")
            else:
                cmd.append(f"--optimize={clamped_level}")
        else:
            # Default behaviour: -O2 is safest for lossless work; -O3 pairs
            # with --lossy and allows the frame-rewriting pass.
            cmd.append("-O2" if lossless else "-O3")

    def _apply_lossy_flag(
        self,
        cmd: List[str],
        lossless: bool,
        unoptimize_enabled: bool,
        gif_lossy_level: Optional[int],
    ) -> bool:
        """Append --lossy=N to cmd if applicable (Step 3).

        Fix B: --lossy must not be emitted when --unoptimize is active.
        gifsicle rejects the combination because unoptimize is an expansion
        step, not a compression step.
        """
        if not lossless and not unoptimize_enabled:
            if gif_lossy_level is None:
                self.last_error = "gif_lossy_level is required when lossless=False"
                logger.error(self.last_error)
                return False
            # Clamp to the valid gifsicle range before constructing the flag.
            clamped = max(0, min(200, int(gif_lossy_level)))
            cmd.append(f"--lossy={clamped}")
        return True

    def _apply_loop_delay_flags(
        self,
        cmd: List[str],
        loopcount_enabled: bool,
        loopcount_forever: bool,
        loopcount_value: int,
        delay_enabled: bool,
        delay_value: int,
    ) -> None:
        """Append loop-count and frame-delay flags to cmd (Steps 4 + 5).

        Fix H: both loopcount_value and delay_value are clamped to their
        valid gifsicle ranges so out-of-range stored values are never
        forwarded to the subprocess.
        """
        # Step 4: loop count
        if loopcount_enabled:
            if loopcount_forever:
                cmd.append("--loopcount=forever")
            else:
                # Fix H: clamp loopcount_value to the valid gifsicle range (1–65535).
                clamped_loop = max(1, min(65535, int(loopcount_value)))
                cmd.append(f"--loopcount={clamped_loop}")

        # Step 5: frame delay
        if delay_enabled:
            # Fix H: clamp delay_value to the valid gifsicle range (0–65535).
            clamped_delay = max(0, min(65535, int(delay_value)))
            cmd.append(f"--delay={clamped_delay}")

    def _apply_color_dither_flags(
        self,
        cmd: List[str],
        colors_enabled: bool,
        colors_num: int,
        dither_enabled: bool,
        dither_method: str,
    ) -> bool:
        """Append colour-reduction and dithering flags to cmd (Steps 6 + 7).

        Returns False (and sets self.last_error) if dither_method is not in
        the module-level allowlist; True otherwise.

        Fix C: validate dither_method against the module-level allowlist
        before constructing any subprocess argument.  An unrecognised value
        would be forwarded verbatim to gifsicle, which could produce
        unexpected output or be exploited to inject arguments.
        """
        # Step 6: colour reduction
        if colors_enabled:
            # Clamp to the valid gifsicle range (2–256).
            clamped_colors = max(2, min(256, colors_num))
            cmd.append(f"--colors={clamped_colors}")

        # Step 7: dithering
        if dither_enabled:
            if dither_method not in _VALID_DITHER_METHODS:
                self.last_error = f"Invalid dither_method: {dither_method!r}"
                logger.error(self.last_error)
                return False
            if dither_method == 'floyd-steinberg':
                # gifsicle uses Floyd–Steinberg by default when --dither is
                # given without a method argument, so omit the suffix to keep
                # the command clean.
                cmd.append("--dither")
            else:
                cmd.append(f"--dither={dither_method}")

        return True

    def _apply_resize_flags(
        self,
        cmd: List[str],
        resize_enabled: bool,
        resize_mode: str,
        resize_width: int,
        resize_height: int,
        scale_x: float,
        scale_y: float,
    ) -> bool:
        """Append resize or scale flags to cmd (Step 8).

        Returns False (and sets self.last_error) if resize_mode is invalid
        or scale factors are out of range; True otherwise.

        Fix D: allowlist resize_mode to prevent arbitrary strings from being
        forwarded to the subprocess argument list.

        Fix F: validate scale factors before use.  scale_x must be positive
        (a zero or negative factor is mathematically undefined for scaling).
        scale_y of 0.0 is the gifsicle convention for "uniform scale — use
        scale_x for both axes".
        """
        if not resize_enabled:
            return True

        if resize_mode not in ('resize', 'scale'):
            self.last_error = f"Invalid resize_mode: {resize_mode!r}"
            logger.error(self.last_error)
            return False

        if resize_mode == 'scale':
            if scale_x <= 0.0:
                self.last_error = f"scale_x must be > 0, got {scale_x}"
                logger.error(self.last_error)
                return False
            if scale_y < 0.0:
                self.last_error = f"scale_y must be >= 0, got {scale_y}"
                logger.error(self.last_error)
                return False
            if scale_y == 0.0:
                # Uniform scaling: a single factor applies to both axes.
                # Fix E: use :.6g to avoid floating-point noise in the
                # flag string (e.g. 0.5 stays "0.5", not "0.50000001").
                cmd.append(f"--scale={scale_x:.6g}")
            else:
                # Independent horizontal and vertical scale factors.
                cmd.append(f"--scale={scale_x:.6g}x{scale_y:.6g}")
        else:
            # --resize=WxH; gifsicle treats 0 in either dimension as
            # "fit to the other dimension while preserving aspect ratio".
            cmd.append(f"--resize={resize_width}x{resize_height}")

        return True

    def _prepare_output_destination(
        self,
        cmd: List[str],
        input_path: str,
        output_path: Optional[str],
        remove_frames_enabled: bool,
    ) -> Tuple[bool, Optional[str]]:
        """Decide and append the output destination flag to cmd (Step 10).

        gifsicle --batch treats all positional args after -- as filenames,
        so frame selectors cannot be used with --batch.  When frame removal
        is requested for an in-place operation, write to a temp file in the
        same directory as the original, then let _finalize_result atomically
        replace it on success so the operation is crash-safe.

        Returns:
            A ``(success, temp_path)`` tuple.  ``success`` is False (and
            self.last_error is set) only when a required temp file could not
            be created.  ``temp_path`` is the path of the temp file, or None
            when no temp file was needed.
        """
        temp_path: Optional[str] = None

        if remove_frames_enabled and not (output_path and output_path != input_path):
            input_dir = os.path.dirname(os.path.abspath(input_path))
            try:
                fd, temp_path = tempfile.mkstemp(
                    suffix='.gif', dir=input_dir, prefix='.mountaineer_tmp_'
                )
                os.close(fd)
            except OSError as exc:
                self.last_error = f"Could not create temp file for frame removal: {exc}"
                logger.error(self.last_error)
                return False, None
            cmd.extend(["--output", temp_path])
        elif output_path and output_path != input_path:
            cmd.extend(["--output", output_path])
        else:
            # --batch rewrites the file in-place; handles both static and
            # animated GIFs without requiring a separate temp file.
            cmd.append("--batch")

        return True, temp_path

    def _apply_frame_selection(
        self,
        cmd: List[str],
        input_path: str,
        remove_frames_enabled: bool,
        remove_frames_offset: int,
        remove_frames_n: int,
        temp_path: Optional[str],
    ) -> bool:
        """Append the input path and optional frame selectors to cmd (Steps 11–13).

        gifsicle supports only #N and #N-M selectors — no stride syntax.
        To keep every N-th frame we must enumerate the frames to keep and
        append each as a '#N' selector after a single input filename.
        gifsicle applies each selector to the most recently named input file,
        so there is no need to repeat the filename per frame.

        Absolute input paths are never confused with options, so -- is
        intentionally omitted when frame selectors follow (it would prevent
        selector recognition).  When no frame selection is needed, -- is
        prepended to defend against filenames that start with '-'.

        On error, cleans up temp_path before returning False.
        """
        if not remove_frames_enabled:
            # -- before the input path defends against filenames that start
            # with '-'; safe to use here because no frame selector follows.
            cmd.extend(['--', input_path])
            return True

        # Guard against remove_frames_n=0, which would cause range() to raise
        # ValueError — violating the compressor "never raises" contract.
        if remove_frames_n < 1:
            self.last_error = f"remove_frames_n must be >= 1, got {remove_frames_n}"
            logger.error(self.last_error)
            if temp_path is not None:
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
            return False

        frame_count = self._get_frame_count(input_path)
        if frame_count < 0:
            self.last_error = (
                "Could not determine frame count for frame removal"
            )
            logger.error(self.last_error)
            # Clean up temp file if one was created.
            if temp_path is not None:
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
            return False

        frames_to_keep = list(range(remove_frames_offset, frame_count, remove_frames_n))
        if not frames_to_keep:
            self.last_error = (
                f"No frames would remain after removal "
                f"(offset={remove_frames_offset}, stride={remove_frames_n}, "
                f"total={frame_count})"
            )
            logger.error(self.last_error)
            if temp_path is not None:
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
            return False

        # List the input path once, then append all '#N' selectors.
        # gifsicle applies each selector to the most recently named input
        # file, so there is no need to repeat the filename per frame.
        cmd.append(input_path)
        for frame_num in frames_to_keep:
            cmd.append(f'#{frame_num}')

        return True

    def _finalize_result(
        self,
        input_path: str,
        success: bool,
        temp_path: Optional[str],
    ) -> bool:
        """Atomically replace input_path with temp_path on success, or clean up on failure.

        When no temp file was used (temp_path is None) the success flag is
        returned unchanged.  When a temp file was used, a successful run
        triggers an os.replace() atomic rename; a failed run removes the
        temp file to leave the original untouched.
        """
        if temp_path is None:
            return success

        if success:
            try:
                os.replace(temp_path, input_path)
            except OSError as exc:
                self.last_error = f"Could not replace original with compressed file: {exc}"
                logger.error(self.last_error)
                return False
        else:
            try:
                os.unlink(temp_path)
            except OSError:
                pass  # best-effort cleanup; original is untouched

        return success

    def compress_file(  # noqa: PLR0912,PLR0913,PLR0915  (many branches/args by design)
        self,
        input_path: str,
        output_path: Optional[str] = None,
        lossless: bool = False,
        strip_metadata: bool = False,
        gif_lossy_level: Optional[int] = None,
        # ------------------------------------------------------------------ #
        # Resize / scale                                                       #
        # ------------------------------------------------------------------ #
        resize_enabled: bool = False,
        resize_mode: str = 'resize',    # 'resize' or 'scale'
        resize_width: int = 0,          # 0 = auto-fit that dimension
        resize_height: int = 0,
        scale_x: float = 1.0,
        scale_y: float = 0.0,           # 0.0 = uniform (same as scale_x)
        # ------------------------------------------------------------------ #
        # Colour reduction                                                     #
        # ------------------------------------------------------------------ #
        colors_enabled: bool = False,
        colors_num: int = 256,          # valid range: 2–256
        # ------------------------------------------------------------------ #
        # Dithering                                                            #
        # ------------------------------------------------------------------ #
        dither_enabled: bool = False,
        dither_method: str = 'floyd-steinberg',
        # ------------------------------------------------------------------ #
        # Frame removal                                                        #
        # ------------------------------------------------------------------ #
        remove_frames_enabled: bool = False,
        remove_frames_n: int = 2,       # keep 1 in every N frames
        remove_frames_offset: int = 0,  # 0 = keep 0,N,2N… ; 1 = keep 1,N+1,…
        # ------------------------------------------------------------------ #
        # Loop count                                                           #
        # ------------------------------------------------------------------ #
        loopcount_enabled: bool = False,
        loopcount_forever: bool = True,
        loopcount_value: int = 1,
        # ------------------------------------------------------------------ #
        # Frame delay                                                          #
        # ------------------------------------------------------------------ #
        delay_enabled: bool = False,
        delay_value: int = 10,          # hundredths of a second
        # ------------------------------------------------------------------ #
        # Optimization overrides                                               #
        # ------------------------------------------------------------------ #
        optimize_enabled: bool = False,  # when True, replaces auto -O2/-O3
        optimize_level: int = 2,         # 1, 2, or 3
        optimize_keep_empty: bool = False,
        unoptimize_enabled: bool = False,
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
            resize_enabled: When True, apply a resize or scale transform.
            resize_mode: 'resize' to use --resize=WxH; 'scale' to use
                --scale=X or --scale=XxY.
            resize_width: Target width in pixels for --resize.  0 lets
                gifsicle auto-fit that dimension.
            resize_height: Target height in pixels for --resize.  0 lets
                gifsicle auto-fit that dimension.
            scale_x: Horizontal scale factor for --scale (e.g. 0.5 = 50 %).
            scale_y: Vertical scale factor for --scale.  0.0 means uniform
                scaling — the same factor as scale_x is applied to both axes.
            colors_enabled: When True, reduce the colour table to colors_num
                entries via --colors=N.
            colors_num: Target number of colours (2–256).  Values outside
                this range are clamped before use.
            dither_enabled: When True, add a --dither flag to improve
                perceived quality after colour reduction.
            dither_method: Dithering algorithm passed to --dither=method.
                The special value 'floyd-steinberg' emits plain --dither
                (no method suffix) because gifsicle uses Floyd–Steinberg by
                default when no method is given.
            remove_frames_enabled: When True, keep only 1 in every
                remove_frames_n frames starting at remove_frames_offset.
                Implemented as a gifsicle frame-selector argument appended
                after the input path.
            remove_frames_n: Stride — keep frame at positions
                offset, offset+N, offset+2N, …
            remove_frames_offset: First frame index to keep (0-based).
            loopcount_enabled: When True, override the GIF loop count.
            loopcount_forever: When True (and loopcount_enabled), use
                --loopcount=forever.  When False, use --loopcount=N where
                N is loopcount_value.
            loopcount_value: Explicit loop count used when loopcount_forever
                is False.
            delay_enabled: When True, set a uniform inter-frame delay via
                --delay=N.
            delay_value: Delay in hundredths of a second (e.g. 10 = 0.1 s).
            optimize_enabled: When True, override the automatic -O2/-O3
                selection with an explicit --optimize=N flag.  Ignored when
                unoptimize_enabled is True.
            optimize_level: Optimisation level (1, 2, or 3) used when
                optimize_enabled is True.
            optimize_keep_empty: When True (and optimize_enabled), append
                --optimize=keep-empty so gifsicle preserves empty frames
                during the optimisation pass.
            unoptimize_enabled: When True, pass --unoptimize to expand a
                previously-optimised GIF back to a per-frame representation.
                When this flag is set, no -O flag is emitted at all.

        Returns:
            True on success, False on failure (details in self.last_error).
        """
        if not lossless and gif_lossy_level is None:
            self.last_error = (
                "gif_lossy_level must be provided for non-lossless compression"
            )
            logger.error(self.last_error)
            return False

        cmd: List[str] = ["gifsicle"]

        self._apply_optimization_flags(
            cmd, lossless, unoptimize_enabled, optimize_enabled,
            optimize_level, optimize_keep_empty, remove_frames_enabled,
        )
        if not self._apply_lossy_flag(cmd, lossless, unoptimize_enabled, gif_lossy_level):
            return False
        self._apply_loop_delay_flags(
            cmd, loopcount_enabled, loopcount_forever, loopcount_value,
            delay_enabled, delay_value,
        )

        if not self._apply_color_dither_flags(
            cmd, colors_enabled, colors_num, dither_enabled, dither_method
        ):
            return False
        if not self._apply_resize_flags(
            cmd, resize_enabled, resize_mode, resize_width, resize_height,
            scale_x, scale_y,
        ):
            return False

        if strip_metadata:
            # gifsicle metadata-stripping flags:
            #   --no-comments  removes GIF comment extensions
            #   --no-extensions removes all application/unknown extensions
            #   --no-names     removes per-frame name extensions
            cmd.extend(["--no-comments", "--no-extensions", "--no-names"])

        ok, temp_path = self._prepare_output_destination(
            cmd, input_path, output_path, remove_frames_enabled
        )
        if not ok:
            return False

        if not self._apply_frame_selection(
            cmd, input_path, remove_frames_enabled,
            remove_frames_offset, remove_frames_n, temp_path,
        ):
            return False

        return self._finalize_result(input_path, self.run_command(cmd), temp_path)
