import argparse
import configparser
import logging
from pathlib import Path

from media_sorter.infrastructure.hachoir_metadata_reader import HachoirMetadataReader
from media_sorter.infrastructure.local_file_system import LocalFileSystem
from media_sorter.services import MediaSorterService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def main():
    """
    The main entry point for the media sorter application.
    """
    parser = argparse.ArgumentParser(description="Sorts media files into a structured directory.")
    parser.add_argument("source_dir", type=Path, help="The source directory containing unsorted media.")
    parser.add_argument("target_dir", type=Path, help="The target directory for the sorted media.")
    args = parser.parse_args()

    # Read configuration
    config = configparser.ConfigParser()
    config.read('config.ini')
    path_format = config.get('sorting', 'path_format', fallback='%Y/%m-%B')
    extensions_str = config.get('sorting', 'supported_extensions', fallback='.jpg,.jpeg,.png,.gif,.mp4,.mov,.avi,.mkv')
    supported_extensions = [ext.strip() for ext in extensions_str.split(',')]

    # Instantiate adapters
    file_system = LocalFileSystem()
    metadata_reader = HachoirMetadataReader()

    # Check if source directory exists
    if not args.source_dir.is_dir():
        logging.error("Source directory does not exist.")
        return

    # Ensure target directory exists
    if not args.target_dir.is_dir():
        logging.info("Target directory does not exist. Creating it.")
        args.target_dir.mkdir(parents=True, exist_ok=True)

    # Instantiate service with the adapters
    sorter_service = MediaSorterService(
        file_system=file_system,
        metadata_reader=metadata_reader,
        path_format=path_format,
        supported_extensions=supported_extensions
    )

    # Execute the service
    sorter_service.execute(args.source_dir, args.target_dir)


if __name__ == "__main__":
    main()
