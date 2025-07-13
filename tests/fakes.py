from datetime import datetime
from pathlib import Path
from typing import Dict

from media_sorter.interfaces import FileSystem, MetadataReader


class FakeFileSystem(FileSystem):
    """A fake in-memory file system for testing."""
    def __init__(self):
        self.files: Dict[Path, str] = {}
        self.directories: set[Path] = set()

    def list_files(self, directory: Path, extensions: list[str]) -> list[Path]:
        return [
            p for p in self.files
            if p.parent == directory and p.suffix.lower() in extensions
        ]

    def copy_file(self, source: Path, destination: Path):
        if source in self.files:
            self.files[destination] = self.files[source]

    def create_directory(self, directory: Path):
        self.directories.add(directory)

    def file_exists(self, file_path: Path) -> bool:
        return file_path in self.files

    def get_file_size(self, file_path: Path) -> int:
        return len(self.files.get(file_path, b""))

    # Helper methods for tests
    def add_file(self, path: Path, content: str = ""):
        self.files[path] = content
        self.directories.add(path.parent)


class FakeMetadataReader(MetadataReader):
    """A fake metadata reader for testing."""
    def __init__(self):
        self.creation_times: Dict[Path, datetime | None] = {}

    def get_creation_time(self, file_path: Path) -> datetime | None:
        return self.creation_times.get(file_path)

    # Helper method for tests
    def set_creation_time(self, path: Path, time: datetime | None):
        self.creation_times[path] = time
