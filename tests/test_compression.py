# tests/test_compression.py

import unittest
from unittest.mock import patch, mock_open
import os
from compression.jpeg_compressor import JpegCompressor
from compression.png_compressor import PngCompressor

class TestJpegCompression(unittest.TestCase):
    def setUp(self):
        self.compressor = JpegCompressor()
        self.test_image_path = "test_image.jpg"

    @patch('subprocess.run')
    def test_jpeg_compression_success(self, mock_run):
        # Mock successful compression
        mock_run.return_value = type('', (), {'returncode': 0})()

        with patch('builtins.open', mock_open(readdata=b'')):
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
        mock_run.return_value = type('', (), {'returncode': 1})()

        with patch('builtins.open', mock_open(readdata=b'')):
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
        mock_result_1 = type('', (), {'returncode': 0})()
        mock_result_2 = type('', (), {'returncode': 0})()

        mock_run.side_effect = [mock_result_1, mock_result_2]

        with patch('builtins.open', mock_open(readdata=b'')):
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
        mock_run.return_value = type('', (), {'returncode': 0})()

        with patch('builtins.open', mock_open(readdata=b'')):
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
