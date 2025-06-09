import os
import zipfile
import argparse
import re
import py7zr
import shutil
from pathlib import Path

def natural_sort_key(s):
    """
    Sort strings with embedded numbers in natural order.
    E.g. ["img1.jpg", "img10.jpg", "img2.jpg"] -> ["img1.jpg", "img2.jpg", "img10.jpg"]
    """
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', s)]

def unpack_manga_archive(input_file, output_dir=None):
    """
    Unpack a CBZ/CB7 file to a directory of images.
    
    Args:
        input_file: Path to the CBZ/CB7 file
        output_dir: Directory to extract images to (optional)
    """
    # Validate input file
    if not os.path.isfile(input_file):
        print(f"Error: '{input_file}' is not a valid file")
        return False
    
    # Check if file is a CBZ or CB7
    if input_file.lower().endswith('.cbz'):
        archive_type = 'cbz'
    elif input_file.lower().endswith('.cb7'):
        archive_type = 'cb7'
    else:
        print(f"Error: '{input_file}' is not a CBZ or CB7 file")
        return False
    
    # Determine output directory if not provided
    if not output_dir:
        output_dir = os.path.splitext(input_file)[0]
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        if archive_type == 'cbz':
            print(f"Extracting CBZ archive: {input_file}")
            with zipfile.ZipFile(input_file, 'r') as zipf:
                # Get list of image files
                image_files = [f for f in zipf.namelist() 
                               if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
                
                # Sort images naturally
                image_files.sort(key=natural_sort_key)
                
                # Extract each file
                for image in image_files:
                    zipf.extract(image, output_dir)
        
        elif archive_type == 'cb7':
            print(f"Extracting CB7 archive: {input_file}")
            with py7zr.SevenZipFile(input_file, 'r') as archive:
                # Extract all files
                archive.extractall(output_dir)
                
                # Get list of extracted image files for counting
                image_files = [f for f in os.listdir(output_dir) 
                               if os.path.isfile(os.path.join(output_dir, f)) and 
                               f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        
        print(f"Successfully extracted {len(image_files)} images to '{output_dir}'")
        return True
    
    except Exception as e:
        print(f"Error extracting archive: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Unpack CBZ/CB7 manga files to images.')
    parser.add_argument('-i', '--input', required=True, help='Input CBZ/CB7 file')
    parser.add_argument('-o', '--output', help='Output directory (optional)')
    args = parser.parse_args()
    
    unpack_manga_archive(args.input, args.output)

if __name__ == "__main__":
    main()
