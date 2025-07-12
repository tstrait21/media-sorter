import shutil
from pathlib import Path

from media_sorter.interfaces import FileSystem


class LocalFileSystem(FileSystem):
    """
    A concrete implementation of the FileSystem interface using pathlib and shutil.
    """

    def list_files(self, directory: Path, extensions: list[str]) -> list[Path]:
        return [
            path for path in directory.iterdir()
            if path.is_file() and
            not path.name.startswith('.') and
            path.suffix.lower() in extensions
        ]

    def copy_file(self, source: Path, destination: Path):
        shutil.copy2(str(source), str(destination))

    def create_directory(self, directory: Path):
        directory.mkdir(parents=True, exist_ok=True)

    def file_exists(self, file_path: Path) -> bool:
        return file_path.exists()
