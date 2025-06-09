# Manga Packer

A set of tools for packing manga images into comic book archives (CBZ/CB7) and unpacking them.

## Requirements

- **Python 3.6 or higher** required
- Required libraries: `py7zr` (for CB7 compression/decompression)
- Optional: `pyinstaller` (for creating standalone executables)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/manga_packer.git
cd manga_packer

# Install dependencies
pip install -r requirements.txt
```

## Usage

### GUI Application
```bash
python Manga_GUI.py
```

### Command Line Tools
Pack images to CBZ with standard compression:
```bash
python Manga_packer.py -i /path/to/images -o output.cbz
```

Pack images to CB7 with ultra compression:
```bash
python Manga_packer_cb7_ultra.py -i /path/to/images -o output.cb7
```

Unpack a comic book archive:
```bash
python Manga_unpacker.py -i /path/to/archive.cbz -o /output/folder
```

## Creating an Executable
```bash
pyinstaller --onefile --windowed --name MangaPackerApp Manga_GUI.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The MIT License is a permissive license that is short and to the point. It lets people do almost anything they want with your project, like making and distributing closed source versions, as long as they include the original license and copyright notice in any copy of the software/source.
