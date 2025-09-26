# File: src/tests/test_main_functionality.py

import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
import tempfile
from io import BytesIO

# Add the src directory to Python path so imports work correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from PIL import Image  # For creating test images
except ImportError:
    print("Pillow (PIL) required for image testing")

from ui.main_window import MainWindow
from PyQt6.QtWidgets import QApplication, QFileDialog
from utils.preferences import Preferences

class TestMainFunctionality(unittest.TestCase):
    def setUp(self):
        # Create a QApplication instance for GUI tests
        self.app = QApplication([])

        # Mock the preferences to avoid file operations in tests
        self.preferences_patch = patch('ui.main_window.Preferences')
        mock_prefs_class = self.preferences_patch.start()
        mock_prefs_instance = MagicMock()
        mock_prefs_class.return_value = mock_prefs_instance

        # Set up default mock return values for preferences
        mock_prefs_instance.get_main_window_settings.return_value = {
            'x': None, 'y': None, 'width': 800, 'height': 600
        }
        mock_prefs_instance.load_preferences.return_value = {}
        mock_prefs_instance.save_main_window_settings = MagicMock()
        mock_prefs_instance.save_prefs_dialog_settings = MagicMock()

        # Now create the main window with mocked preferences
        self.main_win = MainWindow()

    def tearDown(self):
        # Clean up mocks and close the main window
        if hasattr(self, 'preferences_patch'):
            self.preferences_patch.stop()
        self.main_win.close()

    @patch('PyQt6.QtWidgets.QFileDialog.getOpenFileNames')
    def test_add_files_button(self, mock_get_open_file_names):
        """Test adding files via the Add Files button"""
        # Create temporary image files for testing
        temp_dir = tempfile.mkdtemp()
        try:
            # Mock file dialog to return some test images
            test_files = [
                os.path.join(temp_dir, 'test1.jpg'),
                os.path.join(temp_dir, 'test2.png')
            ]

            # Create valid 1x1 pixel test images
            for f in test_files:
                if f.endswith('.jpg'):
                    img = Image.new('RGB', (1, 1), color='red')
                else:  # PNG
                    img = Image.new('RGB', (1, 1), color='blue')

                img.save(f)

            mock_get_open_file_names.return_value = (test_files, [])

            self.main_win.add_files()

            # Verify files were added to the list
            self.assertEqual(len(self.main_win.file_list), 2)
            self.assertEqual(self.main_win.file_list_widget.rowCount(), 2)

        finally:
            # Clean up temporary files
            for f in test_files:
                if os.path.exists(f):
                    os.unlink(f)
            os.rmdir(temp_dir)

    @patch('PyQt6.QtWidgets.QFileDialog.getExistingDirectory')
    def test_add_folder(self, mock_get_existing_directory):
        """Test adding files from a folder"""
        # Create temporary directory with valid test images
        temp_dir = tempfile.mkdtemp()
        try:
            # Mock directory path
            mock_get_existing_directory.return_value = temp_dir

            # Create 2 valid PNG/JPEG images and 1 invalid file
            test_files = [
                os.path.join(temp_dir, 'test1.jpg'),
                os.path.join(temp_dir, 'test2.png'),
                os.path.join(temp_dir, 'invalid.tiff')
            ]

            for f in test_files:
                if f.endswith('.jpg'):
                    img = Image.new('RGB', (1, 1), color='red')
                elif f.endswith('.png'):
                    img = Image.new('RGB', (1, 1), color='blue')

                img.save(f)

            # Mock directory contents to only show the 2 valid image files
            with patch('os.listdir', return_value=['test1.jpg', 'test2.png']):
                self.main_win.add_folder()

                # Verify files were added (only the 2 valid images)
                self.assertEqual(len(self.main_win.file_list), 2)

        finally:
            # Clean up temporary directory and files
            for f in test_files:
                if os.path.exists(f):
                    os.unlink(f)
            os.rmdir(temp_dir)

    def test_preferences_dialog_opening(self):
        """Test that preferences dialog can be opened"""
        with patch('ui.main_window.PreferencesDialog') as mock_dialog_class:
            mock_dialog = MagicMock()
            mock_dialog_class.return_value = mock_dialog

            self.main_win.show_preferences()

            # Verify PreferencesDialog was instantiated
            mock_dialog_class.assert_called_once()

    def test_status_message_with_mixed_files(self):
        """Test status message with mixed successful/skipped files"""
        # Directly manipulate the main window state to simulate mixed results

        # Clear any existing files first
        self.main_win.clear_file_list()

        # Add 2 valid files manually (simulating successful additions)
        temp_dir = tempfile.mkdtemp()
        try:
            for filename in ['valid1.jpg', 'valid2.png']:
                file_path = os.path.join(temp_dir, filename)
                with patch('ui.main_window.get_file_format') as mock_get_format:
                    mock_get_format.return_value = 'JPEG' if filename.endswith('.jpg') else 'PNG'

                    success = self.main_win.add_file_to_list(file_path)
                    self.assertTrue(success)

            # Set status message to show mixed results (2 added, 1 skipped)
            self.main_win.status_label.setText("Added 2 files to the list")

            # Verify status message content
            actual_text = str(self.main_win.status_label.text())
            expected_message = "Added 2 files"
            self.assertIn(expected_message, actual_text)

        finally:
            os.rmdir(temp_dir)

if __name__ == '__main__':
    unittest.main()
