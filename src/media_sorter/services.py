import logging
from pathlib import Path

from media_sorter.domain.media_file import MediaFile
from media_sorter.interfaces import FileSystem, MetadataReader


class MediaSorterService:
    """
    This service orchestrates the sorting of media files.
    """

    def __init__(self, file_system: FileSystem, metadata_reader: MetadataReader, path_format: str, supported_extensions: list[str]):
        self._fs = file_system
        self._reader = metadata_reader
        self._path_format = path_format
        self._supported_extensions = supported_extensions

    def execute(self, source_dir: Path, target_dir: Path):
        """
        Sorts files from the source directory to the target directory.

        :param source_dir: The directory containing unsorted media.
        :param target_dir: The directory where sorted media will be placed.
        """
        for file_path in self._fs.list_files(source_dir, self._supported_extensions):
            creation_time = self._reader.get_creation_time(file_path)
            size = self._fs.get_file_size(file_path)
            media_file = MediaFile(path=file_path, creation_time=creation_time, size=size)

            if media_file.is_sortable:
                self._sort_file(media_file, target_dir)
            else:
                self._copy_to_unsorted(media_file, target_dir)

    def _sort_file(self, media_file: MediaFile, target_dir: Path):
        """Handles sortable files."""
        if not media_file.creation_time:
            # This should not happen if is_sortable is true, but it's worth checking to be sure
            logging.error(f"Could not determine year/month for {media_file.path.name}")
            return

        dest_subdir_str = media_file.creation_time.strftime(self._path_format)
        dest_subdir = target_dir / dest_subdir_str
        self._fs.create_directory(dest_subdir)
        dest_file = dest_subdir / media_file.path.name

        if self._fs.file_exists(dest_file):
            self._handle_duplicate(media_file, dest_file)
        else:
            self._fs.copy_file(media_file.path, dest_file)
            logging.info(f"Copied {media_file.path.name} to {dest_subdir}")

    def _copy_to_unsorted(self, media_file: MediaFile, target_dir: Path):
        """Handles unsortable files by copying them to the 'unsorted' directory."""
        unsorted_subdir = target_dir / "unsorted"
        self._fs.create_directory(unsorted_subdir)
        dest_file = unsorted_subdir / media_file.path.name

        if self._fs.file_exists(dest_file):
            self._handle_duplicate(media_file, dest_file)
        else:
            self._fs.copy_file(media_file.path, dest_file)
            logging.warning(f"Could not read creation_time from {media_file.path.name}. Copied to {unsorted_subdir}")

    def _handle_duplicate(self, source_media_file: MediaFile, dest_file_path: Path):
        """
        Handles cases where a file with the same name already exists in the destination.
        Compares metadata to decide whether to replace the existing file.
        """
        dest_creation_time = self._reader.get_creation_time(dest_file_path)
        if source_media_file.creation_time != dest_creation_time:
            logging.warning(
                f"Skipping {source_media_file.path.name} as a file with the same name but different creation time "
                f"already exists in {dest_file_path.parent}"
            )
            return

        dest_file_size = self._fs.get_file_size(dest_file_path)
        if source_media_file.size > dest_file_size:
            self._fs.copy_file(source_media_file.path, dest_file_path)
            logging.info(
                f"Replaced {dest_file_path.name} with a larger version from {source_media_file.path.parent}"
            )
        else:
            logging.warning(
                f"Skipping {source_media_file.path.name} as a file with the same name and larger or equal size "
                f"already exists in {dest_file_path.parent}"
            )
