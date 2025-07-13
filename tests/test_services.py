import unittest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch

from media_sorter.services import MediaSorterService
from tests.fakes import FakeFileSystem, FakeMetadataReader


class TestMediaSorterService(unittest.TestCase):

    def setUp(self):
        self.fs = FakeFileSystem()
        self.reader = FakeMetadataReader()
        self.source_dir = Path("/fake/source")
        self.target_dir = Path("/fake/destination")
        self.fs.create_directory(self.source_dir)
        self.fs.create_directory(self.target_dir)
        # Default path format for most tests
        self.path_format = "%Y/%m-%B"
        self.supported_extensions = ['.jpg', '.txt']  # Simplified for testing
        self.service = MediaSorterService(self.fs, self.reader, self.path_format, self.supported_extensions)

    def test_sorts_file_with_creation_date(self):
        # Arrange
        file_path = self.source_dir / "image.jpg"
        creation_time = datetime(2023, 10, 22)
        self.fs.add_file(file_path)
        self.reader.set_creation_time(file_path, creation_time)

        # Act
        self.service.execute(self.source_dir, self.target_dir)

        # Assert
        expected_dest = self.target_dir / "2023" / "10-October" / "image.jpg"
        self.assertTrue(self.fs.file_exists(expected_dest))

    def test_sorts_file_with_custom_path_format(self):
        # Arrange
        file_path = self.source_dir / "image.jpg"
        creation_time = datetime(2023, 10, 22)
        self.fs.add_file(file_path)
        self.reader.set_creation_time(file_path, creation_time)
        
        # Use a custom path format for this test
        custom_path_format = "%Y-%m-%d"
        service = MediaSorterService(self.fs, self.reader, custom_path_format, self.supported_extensions)

        # Act
        service.execute(self.source_dir, self.target_dir)

        # Assert
        expected_dest = self.target_dir / "2023-10-22" / "image.jpg"
        self.assertTrue(self.fs.file_exists(expected_dest))

    def test_moves_file_without_creation_date_to_unsorted(self):
        # Arrange
        file_path = self.source_dir / "no_date.txt"
        self.fs.add_file(file_path)
        self.reader.set_creation_time(file_path, None)

        # Act
        self.service.execute(self.source_dir, self.target_dir)

        # Assert
        expected_dest = self.target_dir / "unsorted" / "no_date.txt"
        self.assertTrue(self.fs.file_exists(expected_dest))

    def test_ignores_unsupported_file_types(self):
        # Arrange
        unsupported_file = self.source_dir / "document.pdf"
        self.fs.add_file(unsupported_file)

        # Act
        self.service.execute(self.source_dir, self.target_dir)

        # Assert
        # Check that the file was not moved to 'unsorted' or any other directory
        self.assertEqual(len(self.fs.files), 1)
        unsorted_dir = self.target_dir / "unsorted"
        self.assertFalse(self.fs.file_exists(unsorted_dir / "document.pdf"))


    @patch('logging.info')
    def test_replaces_file_if_source_is_larger(self, mock_log_info):
        # Arrange
        file_path = self.source_dir / "duplicate.jpg"
        creation_time = datetime(2023, 10, 22)
        self.fs.add_file(file_path, content="new_larger_content")
        self.reader.set_creation_time(file_path, creation_time)

        # Pre-populate the destination
        existing_dest = self.target_dir / "2023" / "10-October" / "duplicate.jpg"
        self.fs.add_file(existing_dest, content="original")
        self.reader.set_creation_time(existing_dest, creation_time)

        # Act
        self.service.execute(self.source_dir, self.target_dir)

        # Assert
        self.assertEqual(self.fs.files[existing_dest], "new_larger_content")
        mock_log_info.assert_called_with(
            f"Replaced {existing_dest.name} with a larger version from {file_path.parent}"
        )

    @patch('logging.warning')
    def test_skips_file_if_source_is_smaller_or_equal(self, mock_log_warning):
        # Arrange
        file_path = self.source_dir / "duplicate.jpg"
        creation_time = datetime(2023, 10, 22)
        self.fs.add_file(file_path, content="small")
        self.reader.set_creation_time(file_path, creation_time)

        # Pre-populate the destination
        existing_dest = self.target_dir / "2023" / "10-October" / "duplicate.jpg"
        self.fs.add_file(existing_dest, content="original_larger")
        self.reader.set_creation_time(existing_dest, creation_time)

        # Act
        self.service.execute(self.source_dir, self.target_dir)

        # Assert
        self.assertEqual(self.fs.files[existing_dest], "original_larger")
        mock_log_warning.assert_called_with(
            f"Skipping {file_path.name} as a file with the same name and larger or equal size "
            f"already exists in {existing_dest.parent}"
        )

    @patch('logging.warning')
    def test_skips_unsorted_file_if_already_exists(self, mock_log_warning):
        # Arrange
        file_path = self.source_dir / "duplicate_unsorted.txt"
        self.fs.add_file(file_path, content="new")
        self.reader.set_creation_time(file_path, None)

        # Pre-populate the destination
        existing_dest = self.target_dir / "unsorted" / "duplicate_unsorted.txt"
        self.fs.add_file(existing_dest, content="original_larger")
        self.reader.set_creation_time(existing_dest, None)

        # Act
        self.service.execute(self.source_dir, self.target_dir)

        # Assert
        self.assertEqual(self.fs.files[existing_dest], "original_larger")
        mock_log_warning.assert_called_with(
            f"Skipping {file_path.name} as a file with the same name and larger or equal size "
            f"already exists in {existing_dest.parent}"
        )

    def test_source_directory_is_unmodified(self):
        # Arrange
        file_path = self.source_dir / "image.jpg"
        creation_time = datetime(2023, 10, 22)
        self.fs.add_file(file_path)
        self.reader.set_creation_time(file_path, creation_time)
        initial_source_contents = set(self.fs.files.keys())

        # Act
        self.service.execute(self.source_dir, self.target_dir)

        # Assert
        final_source_contents = {p for p in self.fs.files if p.parent == self.source_dir}
        initial_source_files = {p for p in initial_source_contents if p.parent == self.source_dir}
        self.assertEqual(initial_source_files, final_source_contents)


if __name__ == '__main__':
    unittest.main()
