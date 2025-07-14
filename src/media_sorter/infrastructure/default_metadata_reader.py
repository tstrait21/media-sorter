from datetime import datetime
from pathlib import Path

from media_sorter.interfaces import MetadataReader
from media_sorter.infrastructure.composite_metadata_reader import CompositeMetadataReader


class DefaultMetadataReader(MetadataReader):
    """
    A concrete implementation of the MetadataReader interface that delegates to a composite reader.
    """

    def __init__(self):
        self._composite_reader = CompositeMetadataReader()

    def get_creation_time(self, file_path: Path) -> datetime | None:
        return self._composite_reader.get_creation_time(file_path)