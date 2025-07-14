from datetime import datetime
from pathlib import Path
import exifread
import tinytag
from media_sorter.interfaces import MetadataReader

class CompositeMetadataReader(MetadataReader):
    def get_creation_time(self, file_path: Path) -> datetime | None:
        # Try reading with tinytag first
        try:
            tag = tinytag.TinyTag.get(str(file_path))
            if tag.year:
                return datetime.strptime(tag.year, '%Y')
        except Exception:
            pass

        # If that fails, try reading with exifread for images
        try:
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f)
                if 'EXIF DateTimeOriginal' in tags:
                    return datetime.strptime(str(tags['EXIF DateTimeOriginal']), '%Y:%m:%d %H:%M:%S')
        except Exception:
            pass

        return None
