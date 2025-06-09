import os
import argparse
import re
import py7zr

def natural_sort_key(s):
    """
    Sort strings with embedded numbers in natural order.
    E.g. ["img1.jpg", "img10.jpg", "img2.jpg"] -> ["img1.jpg", "img2.jpg", "img10.jpg"]
    """
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', s)]

def pack_manga_to_7z(input_dir, output_file=None):
    """
    Pack all JPG images from input_dir into a 7z-compressed CBZ file.
    
    Args:
        input_dir: Directory containing JPG images
        output_file: Name of the output CBZ file (optional)
    """
    # Validate input directory
    if not os.path.isdir(input_dir):
        print(f"Error: '{input_dir}' is not a valid directory")
        return False
    
    # Get all JPG files
    jpg_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg'))]
    
    if not jpg_files:
        print(f"Error: No JPG images found in '{input_dir}'")
        return False
    
    # Sort files naturally
    jpg_files.sort(key=natural_sort_key)
    
    # Determine output filename if not provided
    if not output_file:
        output_file = os.path.basename(os.path.normpath(input_dir))
    
    # Add .cbz extension if not present
    if not output_file.lower().endswith('.cbz'):
        output_file += '.cbz'
    
    # 7z provides better compression than ZIP, LZMA2 is the default algorithm
    print("Using 7z LZMA2 compression for maximum file size reduction")
    
    try:
        # Create file paths dictionary
        files_to_archive = {}
        for jpg_file in jpg_files:
            file_path = os.path.join(input_dir, jpg_file)
            # Add file with its basename to avoid directory structure in the archive
            files_to_archive[os.path.basename(jpg_file)] = file_path
        
        # Create the archive with maximum compression
        with py7zr.SevenZipFile(output_file, 'w', filters=[{'id': py7zr.FILTER_LZMA2, 'preset': 9}]) as archive:
            archive.writeall(files_to_archive)
        
        print(f"Successfully created '{output_file}' with {len(jpg_files)} images using 7z compression")
        return True
    except Exception as e:
        print(f"Error creating CBZ file: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Pack manga JPG images into a CBZ file with 7z compression.')
    parser.add_argument('-i', '--input', required=True, help='Directory containing JPG images')
    parser.add_argument('-o', '--output', help='Output CBZ filename (optional)')
    args = parser.parse_args()
    
    pack_manga_to_7z(args.input, args.output)

if __name__ == "__main__":
    main()
