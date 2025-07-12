from datetime import datetime
from pathlib import Path

from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

from media_sorter.interfaces import MetadataReader


class HachoirMetadataReader(MetadataReader):
    """
    A concrete implementation of the MetadataReader interface using the hachoir library.
    """

    def get_creation_time(self, file_path: Path) -> datetime | None:
        try:
            parser = createParser(str(file_path))
            if not parser:
                return None

            with parser:
                metadata = extractMetadata(parser)

            if metadata and metadata.has("creation_date"):
                return metadata.get("creation_date")
            return None
        except Exception:
            return None
