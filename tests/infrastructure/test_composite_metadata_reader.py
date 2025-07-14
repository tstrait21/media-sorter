import unittest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch
from media_sorter.infrastructure.composite_metadata_reader import CompositeMetadataReader
from tests.fakes import FakeFileSystem

class TestCompositeMetadataReader(unittest.TestCase):

    def setUp(self):
        self.fs = FakeFileSystem()
        self.reader = CompositeMetadataReader()
        self.test_dir = Path("/fake/test_files")
        self.fs.create_directory(self.test_dir)

    @patch('tinytag.TinyTag.get')
    def test_get_creation_time_from_tinytag(self, mock_tinytag_get):
        # Arrange
        file_path = self.test_dir / "video.mp4"
        self.fs.add_file(file_path)
        mock_tinytag_get.return_value.year = "2023"

        # Act
        creation_time = self.reader.get_creation_time(file_path)

        # Assert
        self.assertEqual(creation_time, datetime(2023, 1, 1))

    @patch('exifread.process_file')
    @patch('tinytag.TinyTag.get', side_effect=Exception("tinytag error"))
    def test_get_creation_time_from_exifread(self, mock_tinytag_get, mock_exifread):
        # Arrange
        file_path = self.test_dir / "image.jpg"
        self.fs.add_file(file_path)
        mock_exifread.return_value = {
            'EXIF DateTimeOriginal': '2023:10:22 10:00:00'
        }

        # Act
        with patch('builtins.open', unittest.mock.mock_open(read_data=b'test')):
            creation_time = self.reader.get_creation_time(file_path)

        # Assert
        self.assertEqual(creation_time, datetime(2023, 10, 22, 10, 0, 0))

    @patch('tinytag.TinyTag.get', side_effect=Exception("tinytag error"))
    @patch('exifread.process_file', side_effect=Exception("exifread error"))
    def test_get_creation_time_returns_none_on_error(self, mock_exifread, mock_tinytag):
        # Arrange
        file_path = self.test_dir / "no_metadata.txt"
        self.fs.add_file(file_path)

        # Act
        with patch('builtins.open', unittest.mock.mock_open(read_data=b'test')):
            creation_time = self.reader.get_creation_time(file_path)

        # Assert
        self.assertIsNone(creation_time)

if __name__ == '__main__':
    unittest.main()
