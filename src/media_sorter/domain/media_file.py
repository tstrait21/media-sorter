from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class MediaFile:
    """
    A pure domain entity representing a media file.
    It contains the file's path and, once determined, its creation time.
    """
    path: Path
    creation_time: datetime | None = None

    @property
    def is_sortable(self) -> bool:
        return self.creation_time is not None
