from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path


class FileSystem(ABC):
    """
    An abstract interface for file system operations.
    """

    @abstractmethod
    def list_files(self, directory: Path, extensions: list[str]) -> list[Path]:
        """Lists all files in a given directory with specified extensions."""
        pass

    @abstractmethod
    def copy_file(self, source: Path, destination: Path):
        """Copies a file from a source to a destination."""
        pass

    @abstractmethod
    def create_directory(self, directory: Path):
        """Creates a directory, including any parent directories."""
        pass

    @abstractmethod
    def file_exists(self, file_path: Path) -> bool:
        """Checks if a file exists."""
        pass

    @abstractmethod
    def get_file_size(self, file_path: Path) -> int:
        """Gets the size of a file in bytes."""
        pass


class MetadataReader(ABC):
    """
    An abstract interface for reading metadata from a file.
    """

    @abstractmethod
    def get_creation_time(self, file_path: Path) -> datetime | None:
        """Extracts the creation time from a file's metadata."""
        pass
