# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright © 2026 Aries223 (https://github.com/aries223)
import json
import logging
import os

from compression.base_compressor import _sanitise_for_log

logger = logging.getLogger(__name__)


class Preferences:
    DEFAULT_PREFERENCES = {
        'jpeg_compression_level': 90,
        'png_compression_level': 1,
        'gif_lossy_level': 20,
        'webp_compression_level': 90,
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
        'prefs_dialog_height': 400,
    }

    _COMPRESSION_RANGES: dict[str, tuple[int, int]] = {
        'jpeg_compression_level': (0, 100),
        'png_compression_level':  (0, 6),
        'gif_lossy_level':        (0, 200),
        'webp_compression_level': (0, 100),
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
        value: bool | int | str | None,
        default: bool | int | str | None,
    ) -> bool | int | str | None:
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
                    logger.warning(
                        "Preference '%s': expected int for range clamp, got %r; using default",
                        _sanitise_for_log(str(k)), _sanitise_for_log(str(result)),
                    )
                    result = default

            if key_was_present and result != loaded[k]:
                logger.warning(
                    "Preference '%s': invalid value %r, using %r",
                    _sanitise_for_log(str(k)), _sanitise_for_log(str(loaded[k])), _sanitise_for_log(str(result)),
                )

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
