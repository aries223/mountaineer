import json
import logging
import os

logger = logging.getLogger(__name__)


class Preferences:
    DEFAULT_PREFERENCES = {
        'jpeg_compression_level': 95,
        'png_compression_level': 1,
        'lossless_compression': False,
        'strip_metadata': False,
        'warn_before_overwrite': True,

        # Main window settings
        'main_window_x': None,
        'main_window_y': None,
        'main_window_width': 675,
        'main_window_height': 725,

        # Preferences dialog settings
        'prefs_dialog_x': None,
        'prefs_dialog_y': None,
        'prefs_dialog_width': 510,
        'prefs_dialog_height': 215,
    }

    def __init__(self):
        self.prefs_dir = os.path.expanduser("~/.mountaineer")
        self.pref_file = os.path.join(self.prefs_dir, "mountaineer-prefs")

        os.makedirs(self.prefs_dir, exist_ok=True)

        if not os.path.exists(self.pref_file):
            with open(self.pref_file, 'w') as f:
                json.dump(self.DEFAULT_PREFERENCES, f)

    def load_preferences(self):
        """Load preferences from disk, falling back to defaults on error."""
        try:
            with open(self.pref_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning("Error loading preferences: %s", e)
            return self.DEFAULT_PREFERENCES.copy()

    def save_preferences(self, preferences):
        """Write preferences dict to disk."""
        try:
            with open(self.pref_file, 'w') as f:
                json.dump(preferences, f)
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

        if x > 0 and y > 0:
            prefs.update({'main_window_x': x, 'main_window_y': y})
        else:
            prefs.pop('main_window_x', None)
            prefs.pop('main_window_y', None)

        prefs.update({'main_window_width': width, 'main_window_height': height})
        self.save_preferences(prefs)

    def get_prefs_dialog_settings(self):
        prefs = self.load_preferences()
        return {
            'x': prefs.get('prefs_dialog_x'),
            'y': prefs.get('prefs_dialog_y'),
            'width': prefs.get('prefs_dialog_width', 510),
            'height': prefs.get('prefs_dialog_height', 215),
        }

    def save_prefs_dialog_settings(self, x, y, width, height):
        prefs = self.load_preferences()
        prefs.update({
            'prefs_dialog_x': x,
            'prefs_dialog_y': y,
            'prefs_dialog_width': width,
            'prefs_dialog_height': height,
        })
        self.save_preferences(prefs)
