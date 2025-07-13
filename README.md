# Media Sorter

A Python CLI program to organize media files from a source directory into a structured target directory based on their creation timestamp.

## How It Works

The script processes files from a source directory. For each file, it attempts to read the creation time from its metadata.

- **Sortable Files**: If a `creation_time` is found, the file is copied to a structured subdirectory in the target directory, like `YYYY/MM-MonthName`. For example, a photo from January 2023 goes to `2023/01-January/`.
- **Unsortable Files**: If no `creation_time` can be read, the file is copied to an `unsorted` subdirectory.
- **Duplicates**: If a file already exists at the destination, the copy is skipped, and a warning is logged.

## Configuration

The behavior of the sorter can be customized by editing the `config.ini` file.

### Path Format

The `path_format` option under the `[sorting]` section controls the output directory structure. It uses standard `strftime` format codes.

- **Default**: `%Y/%m-%B` (e.g., `2023/10-October`)
- **Custom Example**: `%Y-%m/%d` (e.g., `2023-10/22`)

### Supported File Types

The `supported_extensions` option is a comma-separated list of file extensions (including the dot) that the sorter should process. Any other file types will be ignored.

**Example `config.ini`:**
```ini
[sorting]
path_format = %Y/%m-%B
supported_extensions = .jpg, .jpeg, .png, .gif, .mp4, .mov
```

## Project Structure

The code is organized to separate core logic from external concerns like file systems or specific libraries.

- `src/media_sorter/domain`: Contains the core business entities (e.g., `MediaFile`). This is the heart of the application and has no external dependencies.
- `src/media_sorter/services.py`: The application's service layer, which orchestrates the business logic. It depends on abstract interfaces, not concrete implementations.
- `src/media_sorter/interfaces.py`: Defines the abstract contracts (interfaces) for any external services the application needs, such as a `FileSystem` or a `MetadataReader`.
- `src/media_sorter/infrastructure`: Contains the concrete implementations (adapters) of the interfaces. For example, `local_file_system.py` interacts with the local disk.
- `src/media_sorter/main.py`: The application's entry point, responsible for instantiating the concrete infrastructure and injecting it into the service.

```
.
├── src/
│   └── media_sorter/
│       ├── domain/
│       ├── infrastructure/
│       ├── interfaces.py
│       ├── services.py
│       └── main.py
├── tests/
...
```

## Getting Started

### Prerequisites

This project uses [Conda](https://docs.conda.io/en/latest/) to manage its environment.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd media-sorter
    ```

2.  **Create and activate the Conda environment:**
    ```bash
    conda env create -f environment.yml
    conda activate media-sorter
    ```

### Usage

Run the sorter from the **root directory** of the project:

```bash
python -m media_sorter.main path/to/source_directory path/to/target_directory
```
The `-m` flag is important as it ensures Python correctly handles the imports within the `src` layout.

## Development

This project uses `ruff` for linting and `unittest` for testing. The `Makefile` provides convenient commands.

- **Run tests:**
  ```bash
  make test
  ```
- **Run the linter:**
  ```bash
  make lint
  ```

## Building an Executable

You can build a standalone executable for the application using PyInstaller. This allows you to run the sorter without needing to have Python or any dependencies installed.

1.  **Install the build dependencies:**
    Make sure you have the Conda environment activated.

2.  **Build the executable:**
    ```bash
    make build
    ```
    The executable will be created in the `dist` directory.

### Running the Executable

Once built, you can run the executable directly:

```bash
./dist/media-sorter path/to/source_directory path/to/target_directory
```

## Extending the Code

The architecture makes it easy to extend the application.

### Example: Adding a New Metadata Reader

If you wanted to use a different library (e.g., `exifread`), you would:

1.  **Create a new infrastructure component:**
    Create a new file, `src/media_sorter/infrastructure/exif_reader.py`, that implements the `MetadataReader` interface from `interfaces.py`.

    ```python
    # src/media_sorter/infrastructure/exif_reader.py
    from media_sorter.interfaces import MetadataReader
    import exifread

    class ExifReader(MetadataReader):
        def get_creation_time(self, file_path):
            # Your implementation using exifread
            ...
    ```

2.  **Update the Composition Root:**
    In `src/media_sorter/main.py`, swap out the `HachoirMetadataReader` with your new implementation.

    ```python
    # src/media_sorter/main.py
    # from media_sorter.infrastructure.hachoir_metadata_reader import HachoirMetadataReader
    from media_sorter.infrastructure.exif_reader import ExifReader

    def main():
        ...
        # metadata_reader = HachoirMetadataReader()
        metadata_reader = ExifReader()
        ...
    ```
No other part of the application needs to change. The `MediaSorterService` remains completely unaware of the underlying implementation details.
