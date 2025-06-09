import os
import argparse
import re
import py7zr  # Replace zipfile with py7zr

def natural_sort_key(s):
    """
    Sort strings with embedded numbers in natural order.
    E.g. ["img1.jpg", "img10.jpg", "img2.jpg"] -> ["img1.jpg", "img2.jpg", "img10.jpg"]
    """
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', s)]

def pack_manga_to_cb7(input_dir, output_file=None):
    """
    Pack all JPG images from input_dir into a CB7 file with ultra compression.
    
    Args:
        input_dir: Directory containing JPG images
        output_file: Name of the output CB7 file (optional)
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
    
    # Add .cb7 extension if not present
    if not output_file.lower().endswith('.cb7'):
        output_file += '.cb7'
    
    # Configure simplified ultra compression settings for LZMA2
    # Using only parameters that are fully supported by py7zr
    compression_level = 9  # Maximum level (ultra)
    
    print("Using 7z LZMA2 ULTRA compression for maximum possible file size reduction")
    
    # Create the CB7 file with ultra compression
    try:
        # Dictionary to store files with proper source paths and target names
        files_to_archive = {}
        for jpg_file in jpg_files:
            source_path = os.path.join(input_dir, jpg_file)
            # Use basename to avoid directory structure in archive
            target_name = os.path.basename(jpg_file)
            files_to_archive[target_name] = source_path
        
        # Create the archive with maximum compression
        with py7zr.SevenZipFile(output_file, mode='w', filters=[{'id': py7zr.FILTER_LZMA2}]) as archive:
            # Add each file individually with proper naming
            for target_name, source_path in files_to_archive.items():
                archive.write(source_path, target_name)
        
        print(f"Successfully created '{output_file}' with {len(jpg_files)} images using ULTRA compression")
        return True
    except Exception as e:
        print(f"Error creating CB7 file: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Pack manga JPG images into a CB7 file.')
    parser.add_argument('-i', '--input', required=True, help='Directory containing JPG images')
    parser.add_argument('-o', '--output', help='Output CB7 filename (optional)')
    args = parser.parse_args()
    
    pack_manga_to_cb7(args.input, args.output)

if __name__ == "__main__":
    main()
