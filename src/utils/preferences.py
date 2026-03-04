# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright © 2026 Aries223 (https://github.com/aries223)
import json
import logging
import os

from compression.base_compressor import _sanitise_for_log

logger = logging.getLogger(__name__)

# Fix J: allowlists for string preference keys whose values must be drawn from
# a finite set.  These are used by Preferences._validate_preferences() and kept
# here at module level so the same constants can be imported by other modules
# that need to validate these values independently (e.g. gif_compressor.py
# defines its own parallel frozenset for the same dither methods).
_DITHER_METHODS = frozenset({
    'floyd-steinberg', 'ro64', 'o8', 'o16', 'o32', 'o64',
    'ordered', 'blue_noise', 'halftone',
})
_RESIZE_MODES = frozenset({'resize', 'scale'})


class Preferences:
    DEFAULT_PREFERENCES = {
        'jpeg_compression_level': 90,
        'jpeg_target_size_enabled': False,
        'jpeg_target_size_value':   500,
        'jpeg_target_size_unit':    'KB',
        'jpeg_auto_progressive':    False,
        'jpeg_all_progressive':     False,
        'png_compression_level': 1,
        'gif_lossy_level': 20,
        'gif_resize_enabled': False,
        'gif_resize_mode': 'resize',
        'gif_resize_width': 0,
        'gif_resize_height': 0,
        'gif_scale_x': 1.0,
        'gif_scale_y': 0.0,
        'gif_colors_enabled': False,
        'gif_colors_num': 256,
        'gif_dither_enabled': False,
        'gif_dither_method': 'floyd-steinberg',
        'gif_remove_frames_enabled': False,
        'gif_remove_frames_n': 2,
        'gif_remove_frames_offset': 0,
        'gif_loopcount_enabled': False,
        'gif_loopcount_forever': True,
        'gif_loopcount_value': 1,
        'gif_delay_enabled': False,
        'gif_delay_value': 10,
        'gif_optimize_enabled': False,
        'gif_optimize_level': 2,
        'gif_optimize_keep_empty': False,
        'gif_unoptimize_enabled': False,
        'png_force_8bit':        False,
        'png_zopfli':            False,
        'png_optimize_alpha':    False,
        'png_interlace_enabled': False,
        'png_interlace_type':    '0',
        'webp_compression_level': 90,
        'webp_crop_enabled':        False,
        'webp_crop_x':              0,
        'webp_crop_y':              0,
        'webp_crop_width':          0,
        'webp_crop_height':         0,
        'webp_resize_enabled':      False,
        'webp_resize_width':        0,
        'webp_resize_height':       0,
        'webp_resize_mode':         'always',
        'webp_target_size_enabled': False,
        'webp_target_size_value':   100,
        'webp_target_size_unit':    'KB',
        'webp_passes_enabled':      False,
        'webp_passes':              6,
        'webp_auto_filter':         False,
        'webp_jpeg_like':           False,
        'lossless_compression': False,
        'strip_metadata': True,
        'warn_before_overwrite': True,

        # Main window settings
        'main_window_x': None,
        'main_window_y': None,
        'main_window_width': 875,
        'main_window_height': 1145,
        'column_header_state': "AAAA/wAAAAAAAAABAAAAAQAAAAYBAAAAAAAAAAAAAAAAAAAAAAAAA1sAAAAGAAEBAQAAAAAAAAAAAAAAAGQAAAAoAAAAhAAAAAAAAAAGAAABVQAAAAEAAAAAAAAAVAAAAAEAAAAAAAAAgQAAAAEAAAAAAAAAQgAAAAEAAAAAAAAAggAAAAEAAAAAAAAAbQAAAAEAAAAAAAAD6AAAAABkAAAAAAAAAAAAAAAAAAAAAQ==",

        # Preferences dialog settings
        'prefs_dialog_width': 510,
        'prefs_dialog_height': 750,
    }

    _COMPRESSION_RANGES: dict[str, tuple[int, int]] = {
        'jpeg_compression_level':   (0, 100),
        'jpeg_target_size_value':   (1, 999999),
        'png_compression_level':    (0, 6),
        'gif_lossy_level':          (0, 200),
        'gif_colors_num':           (2, 256),
        'gif_remove_frames_n':      (2, 20),
        # Fix K: gif_remove_frames_offset is always 0 (even frames) or 1 (odd
        # frames); clamp to that range so a corrupted prefs file cannot supply
        # an out-of-range value to the gifsicle frame-selector argument.
        'gif_remove_frames_offset': (0, 1),
        'gif_delay_value':          (0, 65535),
        # Fix O (part 2): lower bound is 0 so callers can explicitly request
        # zero loops.  Previously this was 1, which made 0 unreachable.
        'gif_loopcount_value':      (0, 65535),
        'gif_optimize_level':       (1, 3),
        'webp_compression_level':   (0, 100),
        'webp_crop_x':            (0, 65535),
        'webp_crop_y':            (0, 65535),
        'webp_crop_width':        (0, 65535),
        'webp_crop_height':       (0, 65535),
        'webp_resize_width':      (0, 65535),
        'webp_resize_height':     (0, 65535),
        'webp_target_size_value': (1, 999999),
        'webp_passes':            (1, 10),
    }

    # Fix J: mapping from preference key → allowlist frozenset.  Any key listed
    # here whose stored value is not a member of its frozenset will be replaced
    # by its DEFAULT_PREFERENCES default and a warning will be logged.
    _STRING_ALLOWLISTS: dict[str, frozenset] = {
        'gif_dither_method':  _DITHER_METHODS,
        'gif_resize_mode':    _RESIZE_MODES,
        'png_interlace_type': frozenset({'0', '1', 'keep'}),
        'webp_resize_mode':      frozenset({'down_only', 'up_only', 'always'}),
        'webp_target_size_unit': frozenset({'KB', 'MB'}),
        'jpeg_target_size_unit': frozenset({'KB', 'MB'}),
    }

    def __init__(self):
        self.prefs_dir = os.path.expanduser("~/.mountaineer")
        self.pref_file = os.path.join(self.prefs_dir, "mountaineer-prefs")

        os.makedirs(self.prefs_dir, exist_ok=True)
        try:
            os.chmod(self.prefs_dir, 0o700)
        except OSError as exc:
            # On shared or read-only filesystems the chmod may be refused.
            # Log the warning but allow construction to continue — the app
            # can still read and write preferences even without the mode fix.
            logger.warning("Could not set permissions on preferences directory: %s", exc)

        if not os.path.exists(self.pref_file):
            fd = os.open(self.pref_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w") as f:
                json.dump(self.DEFAULT_PREFERENCES, f, indent=2)

    def load_preferences(self) -> dict:
        """Load preferences from disk, falling back to defaults on error."""
        try:
            with open(self.pref_file, 'r') as f:
                loaded = json.load(f)
                return self._validate_preferences(loaded)
        except Exception as e:
            logger.warning("Error loading preferences: %s", e)
            return self.DEFAULT_PREFERENCES.copy()

    def _coerce_value(
        self,
        value: bool | int | float | str | None,
        default: bool | int | float | str | None,
    ) -> bool | int | float | str | None:
        """Coerce a raw preference value to the type implied by its default.

        The type of ``default`` is the sole arbiter of coercion strategy:

        - ``bool``  — string literals "true"/"1" become ``True``; anything else
                      is passed through ``bool()``.
        - ``int``   — ``int()`` conversion; falls back to ``default`` on failure.
        - ``str``   — ``str()`` conversion; falls back to ``default`` if
                      ``value`` is ``None``.  This covers string-defaulted keys
                      such as ``column_header_state``.
        - ``None``  — the key is optional (e.g. ``main_window_x``/
                      ``main_window_y``).  ``None`` passes through; integers
                      pass through after an ``int()`` round-trip.  The string
                      passthrough is a defensive fallback; no current key
                      exercises it (``column_header_state`` has a ``str``
                      default and is handled by the ``str`` branch above).

        Args:
            value:   Raw value from the JSON file (may already equal ``default``
                     if the key was absent from the file).
            default: The corresponding value from ``DEFAULT_PREFERENCES``.

        Returns:
            The coerced value, guaranteed to be type-compatible with ``default``.
        """
        if isinstance(default, bool):
            if isinstance(value, str):
                return value.lower() in ("true", "1")
            return bool(value)

        if isinstance(default, int):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        if isinstance(default, float):
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        if isinstance(default, str):
            return str(value) if value is not None else default

        # default is None — optional int (window position) or optional string
        if value is None:
            return None
        if isinstance(value, str):
            # Defensive fallback: a non-standard string value was stored under a
            # None-defaulted key (optional window coordinates).  Pass it through
            # rather than silently dropping it; the int() branch below handles the
            # expected case.
            return value
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _validate_preferences(self, loaded: dict) -> dict:
        """Validate and coerce a raw preferences dict loaded from disk.

        Each key in ``DEFAULT_PREFERENCES`` is checked in turn.  Missing keys
        receive their default value.  Values that are present but invalid are
        coerced; if coercion changes the value a warning is logged.
        Compression-level keys are additionally clamped to their declared range.

        Args:
            loaded: The raw ``dict`` produced by ``json.load()``.

        Returns:
            A fully-validated preferences dict with the same keys as
            ``DEFAULT_PREFERENCES``.
        """
        validated: dict = {}
        for k, default in self.DEFAULT_PREFERENCES.items():
            key_was_present = k in loaded
            value = loaded.get(k, default)

            result = self._coerce_value(value, default)

            if k in self._COMPRESSION_RANGES:
                lo, hi = self._COMPRESSION_RANGES[k]
                if isinstance(result, int):
                    result = max(lo, min(hi, result))
                else:
                    logger.warning("Preference '%s': expected int for range clamp, got %r; using default", _sanitise_for_log(str(k)), _sanitise_for_log(str(result)))  # NOSONAR
                    result = default

            # Fix J: validate string-valued keys against their allowlists.
            # A stale or externally-edited prefs file could store an
            # unrecognised string that would be forwarded to gifsicle as an
            # argument value; rejecting it here and substituting the safe
            # default prevents that from reaching the subprocess layer.
            if k in self._STRING_ALLOWLISTS:
                if result not in self._STRING_ALLOWLISTS[k]:
                    logger.warning("Preference '%s': invalid value, using default", _sanitise_for_log(str(k)))
                    result = default

            if key_was_present and result != loaded[k]:
                logger.warning("Preference '%s': invalid value %r, using %r", _sanitise_for_log(str(k)), _sanitise_for_log(str(loaded[k])), _sanitise_for_log(str(result)))  # NOSONAR

            validated[k] = result
        return validated

    def save_preferences(self, preferences: dict) -> None:
        """Write the complete preferences dict to disk in-place via O_TRUNC.

        Callers are responsible for using the read-modify-write pattern to
        preserve keys they do not explicitly set.  Writing a partial dict will
        silently erase unmentioned keys.

        Args:
            preferences: The full preferences dict to persist.
        """
        try:
            fd = os.open(self.pref_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w") as f:
                json.dump(preferences, f, indent=2)
        except Exception as e:
            logger.error("Error saving preferences: %s", e)

    def get_main_window_settings(self) -> dict:
        """Return saved main-window geometry, falling back to DEFAULT_PREFERENCES.

        Returns:
            A dict with keys ``x``, ``y`` (``None`` if never saved), ``width``,
            and ``height``.
        """
        prefs = self.load_preferences()
        # load_preferences() guarantees every DEFAULT_PREFERENCES key is present
        # in the returned dict (via _validate_preferences), so direct access is safe.
        return {
            'x': prefs['main_window_x'],
            'y': prefs['main_window_y'],
            'width': prefs['main_window_width'],
            'height': prefs['main_window_height'],
        }

    def save_main_window_settings(self, x: int, y: int, width: int, height: int) -> None:
        """Persist main-window geometry using the read-modify-write pattern.

        Position (``x``, ``y``) is skipped when both are zero to avoid
        recording the Wayland compositor's synthetic origin during startup.
        In that case any previously saved position keys are removed so the
        window centres on next launch.

        Args:
            x:      Horizontal screen position in pixels.
            y:      Vertical screen position in pixels.
            width:  Window width in pixels.
            height: Window height in pixels.
        """
        prefs = self.load_preferences()

        if not (x == 0 and y == 0):
            prefs.update({'main_window_x': x, 'main_window_y': y})
        else:
            prefs.pop('main_window_x', None)
            prefs.pop('main_window_y', None)

        prefs.update({'main_window_width': width, 'main_window_height': height})
        self.save_preferences(prefs)

    def get_prefs_dialog_settings(self) -> dict:
        """Return saved preferences-dialog size, falling back to DEFAULT_PREFERENCES.

        Returns:
            A dict with keys ``width`` and ``height``.
        """
        prefs = self.load_preferences()
        # load_preferences() guarantees every DEFAULT_PREFERENCES key is present
        # in the returned dict (via _validate_preferences), so direct access is safe.
        return {
            'width': prefs['prefs_dialog_width'],
            'height': prefs['prefs_dialog_height'],
        }

    def save_prefs_dialog_settings(self, width: int, height: int) -> None:
        """Persist preferences-dialog size using the read-modify-write pattern.

        Only width and height are stored; the dialog has no saved position.

        Args:
            width:  Dialog width in pixels.
            height: Dialog height in pixels.
        """
        prefs = self.load_preferences()
        prefs.update({'prefs_dialog_width': width, 'prefs_dialog_height': height})
        self.save_preferences(prefs)
