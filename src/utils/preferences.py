import os
import json

class Preferences:
    DEFAULT_PREFERENCES = {
        'jpeg_compression_level': 80,
        'png_compression_level': 65,
        'lossless_compression': False,
        'strip_metadata': False,

        # Main window settings
        'main_window_x': None,       # Start with None to detect if user moved window
        'main_window_y': None,
        'main_window_width': 1200,   # Default main window size
        'main_window_height': 1600,

        # Preferences dialog settings
        'prefs_dialog_x': None,
        'prefs_dialog_y': None,
        'prefs_dialog_width': 500,
        'prefs_dialog_height': 300
    }

    def __init__(self):
        self.prefs_dir = os.path.expanduser("~/.mountaineer")
        self.pref_file = os.path.join(self.prefs_dir, "mountaineer-prefs")

        if not os.path.exists(self.prefs_dir):
            os.makedirs(self.prefs_dir)

        if not os.path.exists(self.pref_file):
            with open(self.pref_file, 'w') as f:
                json.dump(self.DEFAULT_PREFERENCES, f)
                print(f"Created default preferences file at {self.pref_file}")

    def load_preferences(self):
        try:
            with open(self.pref_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading preferences: {e}")
            return self.DEFAULT_PREFERENCES

    def save_preferences(self, preferences):
        try:
            with open(self.pref_file, 'w') as f:
                json.dump(preferences, f)
                print(f"Saved preferences: {preferences}")
        except Exception as e:
            print(f"Error saving preferences: {e}")

    # Methods for window settings
    def get_main_window_settings(self):
        prefs = self.load_preferences()
        print(f"Loaded main window settings: {prefs}")
        return {
            'x': prefs.get('main_window_x'),
            'y': prefs.get('main_window_y'),
            'width': prefs.get('main_window_width', 1200),
            'height': prefs.get('main_window_height', 1600)
        }

    def save_main_window_settings(self, x, y, width, height):
        prefs = self.load_preferences()

        # Only save meaningful positions (non-zero coordinates indicate user movement)
        if x > 0 and y > 0:
            print(f"Saving non-zero main window position: x={x}, y={y}")
            prefs.update({
                'main_window_x': x,
                'main_window_y': y
            })
        else:
            # Remove coordinates if they're invalid (reset to None)
            if 'main_window_x' in prefs:
                del prefs['main_window_x']
            if 'main_window_y' in prefs:
                del prefs['main_window_y']
            print("Removing main window position due to invalid coordinates")

        # Always save size
        prefs.update({
            'main_window_width': width,
            'main_window_height': height
        })

        self.save_preferences(prefs)

    def get_prefs_dialog_settings(self):
        prefs = self.load_preferences()
        return {
            'x': prefs.get('prefs_dialog_x'),
            'y': prefs.get('prefs_dialog_y'),
            'width': prefs.get('prefs_dialog_width', 500),
            'height': prefs.get('prefs_dialog_height', 300)
        }

    def save_prefs_dialog_settings(self, x, y, width, height):
        prefs = self.load_preferences()
        prefs.update({
            'prefs_dialog_x': x,
            'prefs_dialog_y': y,
            'prefs_dialog_width': width,
            'prefs_dialog_height': height
        })
        self.save_preferences(prefs)
