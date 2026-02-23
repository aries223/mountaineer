# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright © 2026 Aries223 (https://github.com/aries223)
import json
import logging
import os

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

    def __init__(self):
        self.prefs_dir = os.path.expanduser("~/.mountaineer")
        self.pref_file = os.path.join(self.prefs_dir, "mountaineer-prefs")

        os.makedirs(self.prefs_dir, exist_ok=True)
        os.chmod(self.prefs_dir, 0o700)

        if not os.path.exists(self.pref_file):
            fd = os.open(self.pref_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w") as f:
                json.dump(self.DEFAULT_PREFERENCES, f, indent=2)

    def load_preferences(self):
        """Load preferences from disk, falling back to defaults on error."""
        try:
            with open(self.pref_file, 'r') as f:
                loaded = json.load(f)
                return self._validate_preferences(loaded)
        except Exception as e:
            logger.warning("Error loading preferences: %s", e)
            return self.DEFAULT_PREFERENCES.copy()

    _COMPRESSION_RANGES: dict = {
        'jpeg_compression_level': (0, 100),
        'png_compression_level':  (0, 6),
        'gif_lossy_level':        (0, 200),
        'webp_compression_level': (0, 100),
    }

    def _validate_preferences(self, loaded: dict) -> dict:
        validated: dict = {}
        for k, default in self.DEFAULT_PREFERENCES.items():
            value = loaded.get(k, default)
            original = loaded.get(k)

            if isinstance(default, bool):
                if isinstance(value, str):
                    result = value.lower() in ("true", "1")
                else:
                    result = bool(value)
            elif isinstance(default, int):
                try:
                    result = int(value)
                except (TypeError, ValueError):
                    result = default
            else:
                # default is None — optional int (window position) or optional string
                if value is None:
                    result = None
                elif isinstance(value, str):
                    # Accept string values as-is (e.g. column_header_state base64 payload)
                    result = value
                else:
                    try:
                        result = int(value)
                    except (TypeError, ValueError):
                        result = None

            if k in self._COMPRESSION_RANGES:
                lo, hi = self._COMPRESSION_RANGES[k]
                result = max(lo, min(hi, result))

            if original is not None and result != original:
                logger.warning("Preference '%s': invalid value %r, using %r", k, original, result)

            validated[k] = result
        return validated

    def save_preferences(self, preferences):
        """Write preferences dict to disk."""
        try:
            fd = os.open(self.pref_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with os.fdopen(fd, "w") as f:
                json.dump(preferences, f, indent=2)
        except Exception as e:
            logger.error("Error saving preferences: %s", e)

    def get_main_window_settings(self):
        prefs = self.load_preferences()
        return {
            'x': prefs.get('main_window_x'),
            'y': prefs.get('main_window_y'),
            'width': prefs.get('main_window_width', 675),
            'height': prefs.get('main_window_height', 725),
        }

    def save_main_window_settings(self, x, y, width, height):
        prefs = self.load_preferences()

        if not (x == 0 and y == 0):
            prefs.update({'main_window_x': x, 'main_window_y': y})
        else:
            prefs.pop('main_window_x', None)
            prefs.pop('main_window_y', None)

        prefs.update({'main_window_width': width, 'main_window_height': height})
        self.save_preferences(prefs)

    def get_prefs_dialog_settings(self):
        prefs = self.load_preferences()
        return {
            'width': prefs.get('prefs_dialog_width', 510),
            'height': prefs.get('prefs_dialog_height', 400),
        }

    def save_prefs_dialog_settings(self, width, height):
        prefs = self.load_preferences()
        prefs.update({'prefs_dialog_width': width, 'prefs_dialog_height': height})
        self.save_preferences(prefs)
