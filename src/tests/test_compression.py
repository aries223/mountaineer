# src/tests/test_compression.py

import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import sys

# Add the src directory to Python path so imports work correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from compression.base_compressor import BaseCompressor
from compression.jpeg_compressor import JpegCompressor
from compression.png_compressor import PngCompressor

# Import the specific function we want to test
from utils.file_utils import get_file_format

class TestBaseCompressor(unittest.TestCase):
    def setUp(self):
        self.compressor = BaseCompressor()

    @patch('subprocess.run')
    def test_run_command_success(self, mock_run):
        # Mock successful command execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ''
        mock_result.stderr = ''

        mock_run.return_value = mock_result

        cmd = ["echo", "test"]
        success = self.compressor.run_command(cmd)
        self.assertTrue(success)

    @patch('subprocess.run')
    def test_run_command_failure(self, mock_run):
        # Mock failed command execution
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ''
        mock_result.stderr = 'Command failed'

        mock_run.return_value = mock_result

        cmd = ["false", "command"]
        success = self.compressor.run_command(cmd)
        self.assertFalse(success)

class TestFileUtils(unittest.TestCase):
    def test_get_file_format_jpeg(self):
        # Create a simple mock that returns the expected format string
        with patch('PIL.Image.open') as mock_open:
            mock_image = MagicMock()
            mock_image.format = 'JPEG'
            mock_open.return_value.__enter__.return_value = mock_image

            # Call the function and verify it correctly processes the format
            format_str = get_file_format("test.jpg")
            self.assertEqual(format_str.upper(), "JPEG")

    def test_get_file_format_png(self):
        # Create a simple mock that returns the expected format string
        with patch('PIL.Image.open') as mock_open:
            mock_image = MagicMock()
            mock_image.format = 'PNG'
            mock_open.return_value.__enter__.return_value = mock_image

            # Call the function and verify it correctly processes the format
            format_str = get_file_format("test.png")
            self.assertEqual(format_str.upper(), "PNG")

class TestJpegCompression(unittest.TestCase):
    def setUp(self):
        self.compressor = JpegCompressor()
        self.test_image_path = "test_image.jpg"

    @patch('subprocess.run')
    def test_jpeg_compression_success(self, mock_run):
        # Mock successful compression
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ''
        mock_result.stderr = ''

        mock_run.return_value = mock_result

        with patch('builtins.open', mock_open(read_data=b'')):
            success = self.compressor.compress_file(
                self.test_image_path,
                None,
                lossless=False,
                strip_metadata=True,
                jpeg_quality=85
            )
            self.assertTrue(success)

    @patch('subprocess.run')
    def test_jpeg_compression_failure(self, mock_run):
        # Mock failed compression
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ''
        mock_result.stderr = 'Simulated error'

        mock_run.return_value = mock_result

        with patch('builtins.open', mock_open(read_data=b'')):
            success = self.compressor.compress_file(
                self.test_image_path,
                None,
                lossless=False,
                strip_metadata=True,
                jpeg_quality=85
            )
            self.assertFalse(success)

    def test_jpeg_missing_quality(self):
        with self.assertRaises(ValueError):
            JpegCompressor().compress_file(
                self.test_image_path,
                None,
                lossless=False,
                strip_metadata=True,
                jpeg_quality=None
            )

class TestPngCompression(unittest.TestCase):
    def setUp(self):
        self.compressor = PngCompressor()
        self.test_image_path = "test_image.png"

    @patch('subprocess.run')
    def test_png_lossy_compression_success(self, mock_run):
        # Mock successful compression with pngquant
        mock_result_1 = MagicMock()
        mock_result_1.returncode = 0
        mock_result_1.stdout = ''
        mock_result_1.stderr = ''

        mock_result_2 = MagicMock()
        mock_result_2.returncode = 0
        mock_result_2.stdout = ''
        mock_result_2.stderr = ''

        mock_run.side_effect = [mock_result_1, mock_result_2]

        with patch('builtins.open', mock_open(read_data=b'')):
            success = self.compressor.compress_file(
                self.test_image_path,
                None,
                lossless=False,
                strip_metadata=True,
                png_quality=65
            )
            self.assertTrue(success)

    @patch('subprocess.run')
    def test_png_lossless_compression_success(self, mock_run):
        # Mock successful compression with oxipng
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ''
        mock_result.stderr = ''

        mock_run.return_value = mock_result

        with patch('builtins.open', mock_open(read_data=b'')):
            success = self.compressor.compress_file(
                self.test_image_path,
                None,
                lossless=True,
                strip_metadata=False,
                png_quality=65
            )
            self.assertTrue(success)

    def test_png_missing_quality(self):
        with self.assertRaises(ValueError):
            PngCompressor().compress_file(
                self.test_image_path,
                None,
                lossless=True,
                strip_metadata=False,
                png_quality=None
            )

if __name__ == '__main__':
    unittest.main()
