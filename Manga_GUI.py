import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import sys
import zipfile
import py7zr
import re
import shutil

def natural_sort_key(s):
    """
    Sort strings with embedded numbers in natural order.
    E.g. ["img1.jpg", "img10.jpg", "img2.jpg"] -> ["img1.jpg", "img2.jpg", "img10.jpg"]
    """
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', s)]

class RedirectText:
    """Class to redirect stdout to a tkinter Text widget"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""

    def write(self, string):
        self.buffer += string
        # Update the text widget in the main thread
        self.text_widget.after(0, self.update_widget)

    def update_widget(self):
        self.text_widget.configure(state=tk.NORMAL)
        self.text_widget.insert(tk.END, self.buffer)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state=tk.DISABLED)
        self.buffer = ""

    def flush(self):
        pass

class MangaUtilityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Manga Packer/Unpacker Utility")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Set up the main frame
        main_frame = ttk.Frame(root, padding="10 10 10 10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create tabs
        pack_tab = ttk.Frame(self.notebook)
        unpack_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(pack_tab, text="Pack Manga")
        self.notebook.add(unpack_tab, text="Unpack Manga")
        
        # === PACK TAB ===
        pack_frame = ttk.LabelFrame(pack_tab, text="Pack Manga Images to CBZ/CB7", padding="10 10 10 10")
        pack_frame.pack(fill=tk.BOTH, expand=True)
        
        # Source directory selection
        ttk.Label(pack_frame, text="Source Directory (containing JPG files):").grid(column=0, row=0, sticky=tk.W)
        self.pack_source_dir = tk.StringVar()
        ttk.Entry(pack_frame, width=50, textvariable=self.pack_source_dir).grid(column=0, row=1, sticky=(tk.W, tk.E))
        ttk.Button(pack_frame, text="Browse...", command=self.browse_pack_source).grid(column=1, row=1, sticky=tk.W)
        
        # Output file selection
        ttk.Label(pack_frame, text="Output File (optional):").grid(column=0, row=2, sticky=tk.W, pady=(10, 0))
        self.pack_output_file = tk.StringVar()
        ttk.Entry(pack_frame, width=50, textvariable=self.pack_output_file).grid(column=0, row=3, sticky=(tk.W, tk.E))
        ttk.Button(pack_frame, text="Browse...", command=self.browse_pack_output).grid(column=1, row=3, sticky=tk.W)
        
        # Format selection
        ttk.Label(pack_frame, text="Format:").grid(column=0, row=4, sticky=tk.W, pady=(10, 0))
        self.pack_format = tk.StringVar(value="cbz")
        format_frame = ttk.Frame(pack_frame)
        format_frame.grid(column=0, row=5, sticky=tk.W)
        ttk.Radiobutton(format_frame, text="CBZ (Standard ZIP)", value="cbz", variable=self.pack_format).pack(side=tk.LEFT)
        ttk.Radiobutton(format_frame, text="CB7 (LZMA2 Ultra)", value="cb7", variable=self.pack_format).pack(side=tk.LEFT)
        
        # Pack button
        ttk.Button(pack_frame, text="Pack Manga", command=self.pack_manga).grid(column=0, row=6, sticky=tk.W, pady=10)
        
        # === UNPACK TAB ===
        unpack_frame = ttk.LabelFrame(unpack_tab, text="Unpack CBZ/CB7 to Images", padding="10 10 10 10")
        unpack_frame.pack(fill=tk.BOTH, expand=True)
        
        # Source file selection
        ttk.Label(unpack_frame, text="Source File (CBZ/CB7):").grid(column=0, row=0, sticky=tk.W)
        self.unpack_source_file = tk.StringVar()
        ttk.Entry(unpack_frame, width=50, textvariable=self.unpack_source_file).grid(column=0, row=1, sticky=(tk.W, tk.E))
        ttk.Button(unpack_frame, text="Browse...", command=self.browse_unpack_source).grid(column=1, row=1, sticky=tk.W)
        
        # Output directory selection
        ttk.Label(unpack_frame, text="Output Directory (optional):").grid(column=0, row=2, sticky=tk.W, pady=(10, 0))
        self.unpack_output_dir = tk.StringVar()
        ttk.Entry(unpack_frame, width=50, textvariable=self.unpack_output_dir).grid(column=0, row=3, sticky=(tk.W, tk.E))
        ttk.Button(unpack_frame, text="Browse...", command=self.browse_unpack_output).grid(column=1, row=3, sticky=tk.W)
        
        # Unpack button
        ttk.Button(unpack_frame, text="Unpack Manga", command=self.unpack_manga).grid(column=0, row=4, sticky=tk.W, pady=10)
        
        # === OUTPUT LOG ===
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10 10 10 10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Output log text widget
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.configure(state=tk.DISABLED)
        
        # Scrollbar for log text
        log_scroll = ttk.Scrollbar(self.log_text, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        
        # Redirect stdout to the log text widget
        self.stdout_redirect = RedirectText(self.log_text)
        sys.stdout = self.stdout_redirect
        
        print("Welcome to Manga Packer/Unpacker! Please select an operation.")

    def browse_pack_source(self):
        directory = filedialog.askdirectory(title="Select Directory with Images")
        if directory:
            self.pack_source_dir.set(directory)
    
    def browse_pack_output(self):
        format_ext = ".cb7" if self.pack_format.get() == "cb7" else ".cbz"
        file = filedialog.asksaveasfilename(
            title="Save Archive As",
            filetypes=[("Comic Book Archive", f"*{format_ext}")],
            defaultextension=format_ext
        )
        if file:
            self.pack_output_file.set(file)
    
    def browse_unpack_source(self):
        file = filedialog.askopenfilename(
            title="Select CBZ/CB7 Archive",
            filetypes=[("Comic Book Archives", "*.cbz *.cb7"), ("CBZ Files", "*.cbz"), 
                      ("CB7 Files", "*.cb7"), ("All Files", "*.*")]
        )
        if file:
            self.unpack_source_file.set(file)
    
    def browse_unpack_output(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.unpack_output_dir.set(directory)
    
    def pack_manga(self):
        source_dir = self.pack_source_dir.get()
        output_file = self.pack_output_file.get()
        format_type = self.pack_format.get()
        
        if not source_dir:
            messagebox.showerror("Error", "Please select a source directory.")
            return
            
        # Start packing in a separate thread to avoid freezing the GUI
        thread = threading.Thread(target=self._pack_thread, args=(source_dir, output_file, format_type))
        thread.daemon = True
        thread.start()
    
    def _pack_thread(self, source_dir, output_file, format_type):
        try:
            print(f"Packing manga from {source_dir}...")
            
            # Validate input directory
            if not os.path.isdir(source_dir):
                print(f"Error: '{source_dir}' is not a valid directory")
                return
            
            # Get all JPG files
            jpg_files = [f for f in os.listdir(source_dir) if f.lower().endswith(('.jpg', '.jpeg'))]
            
            if not jpg_files:
                print(f"Error: No JPG images found in '{source_dir}'")
                return
            
            # Sort files naturally
            jpg_files.sort(key=natural_sort_key)
            
            # Determine output filename if not provided
            if not output_file:
                output_file = os.path.basename(os.path.normpath(source_dir))
                
                # Add extension if not present
                if format_type == "cb7" and not output_file.lower().endswith('.cb7'):
                    output_file += '.cb7'
                elif format_type == "cbz" and not output_file.lower().endswith('.cbz'):
                    output_file += '.cbz'
            
            if format_type == "cb7":
                # Pack as CB7 with LZMA2 Ultra
                print("Using 7z LZMA2 Ultra compression")
                
                # Create file paths dictionary
                files_to_archive = {}
                for jpg_file in jpg_files:
                    file_path = os.path.join(source_dir, jpg_file)
                    files_to_archive[os.path.basename(jpg_file)] = file_path
                
                # Create CB7 file with optimal settings
                optimal_filters = [
                    {
                        'id': py7zr.FILTER_LZMA2,
                        'preset': 9,
                        'dict_size': 32 * 1024 * 1024  # 32MB is usually sufficient for manga
                    }
                ]
                
                with py7zr.SevenZipFile(output_file, 'w', filters=optimal_filters) as archive:
                    archive.writeall(files_to_archive)
                
            else:
                # Pack as CBZ with standard ZIP compression
                print("Using standard ZIP compression")
                
                with zipfile.ZipFile(output_file, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
                    for jpg_file in jpg_files:
                        file_path = os.path.join(source_dir, jpg_file)
                        zipf.write(file_path, arcname=os.path.basename(file_path))
            
            print(f"Successfully created '{output_file}' with {len(jpg_files)} images")
            
        except Exception as e:
            print(f"Error packing manga: {str(e)}")
    
    def unpack_manga(self):
        source_file = self.unpack_source_file.get()
        output_dir = self.unpack_output_dir.get()
        
        if not source_file:
            messagebox.showerror("Error", "Please select a source CBZ/CB7 file.")
            return
        
        # Start unpacking in a separate thread to avoid freezing the GUI
        thread = threading.Thread(target=self._unpack_thread, args=(source_file, output_dir))
        thread.daemon = True
        thread.start()
    
    def _unpack_thread(self, source_file, output_dir):
        try:
            print(f"Unpacking manga from {source_file}...")
            
            # Validate input file
            if not os.path.isfile(source_file):
                print(f"Error: '{source_file}' is not a valid file")
                return
            
            # Check if file is a CBZ or CB7
            if source_file.lower().endswith('.cbz'):
                archive_type = 'cbz'
            elif source_file.lower().endswith('.cb7'):
                archive_type = 'cb7'
            else:
                print(f"Error: '{source_file}' is not a CBZ or CB7 file")
                return
            
            # Determine output directory if not provided
            if not output_dir:
                output_dir = os.path.splitext(source_file)[0]
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            if archive_type == 'cbz':
                print(f"Extracting CBZ archive: {source_file}")
                with zipfile.ZipFile(source_file, 'r') as zipf:
                    # Get list of image files
                    image_files = [f for f in zipf.namelist() 
                                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
                    
                    # Check if there are directories in the archive
                    directories = set()
                    for path in image_files:
                        if '/' in path or '\\' in path:
                            dir_path = os.path.dirname(path)
                            directories.add(dir_path)
                    
                    # Report directory structure if found
                    if directories:
                        print(f"Found {len(directories)} directories in the archive:")
                        for dir_path in sorted(directories):
                            print(f" - {dir_path}")
                        print("All files will be extracted to the root output directory.")
                    
                    # Sort images naturally (considering filenames only, not paths)
                    image_files.sort(key=lambda x: natural_sort_key(os.path.basename(x)))
                    print(f"Found {len(image_files)} images to extract")
                    
                    # Extract each file - flatten directory structure
                    for image in image_files:
                        # Get just the filename without any directory structure
                        image_filename = os.path.basename(image)
                        
                        # Extract the file data
                        source = zipf.open(image)
                        target_path = os.path.join(output_dir, image_filename)
                        
                        # Write the file to the output directory
                        with open(target_path, "wb") as target:
                            shutil.copyfileobj(source, target)
                        
                        source.close()
                    
                    print(f"Extracted {len(image_files)} images to '{output_dir}'")
            
            elif archive_type == 'cb7':
                print(f"Extracting CB7 archive: {source_file}")
                with py7zr.SevenZipFile(source_file, 'r') as archive:
                    # Get list of all files in archive
                    all_files = archive.getnames()
                    
                    # Filter for image files
                    image_files = [f for f in all_files 
                                  if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
                    
                    # Extract only images and flatten directory structure
                    for image in image_files:
                        # Extract to a temporary location
                        archive.extract(path=output_dir, targets=[image])
                        
                        # Move from potential nested directory to root output dir
                        source_path = os.path.join(output_dir, image)
                        target_path = os.path.join(output_dir, os.path.basename(image))
                        
                        # If the file is in a subdirectory, move it to the root
                        if os.path.dirname(image) and os.path.exists(source_path):
                            shutil.move(source_path, target_path)
                    
                    # Clean up any empty directories created during extraction
                    for root, dirs, files in os.walk(output_dir, topdown=False):
                        for dir in dirs:
                            dir_path = os.path.join(root, dir)
                            if not os.listdir(dir_path):  # Check if directory is empty
                                os.rmdir(dir_path)
                    
                    # Re-count files after flattening
                    image_files = [f for f in os.listdir(output_dir) 
                                  if os.path.isfile(os.path.join(output_dir, f)) and 
                                  f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
            
            print(f"Successfully extracted all images to '{output_dir}'")
            
        except Exception as e:
            print(f"Error unpacking manga: {str(e)}")
            # Print more detailed error for debugging
            import traceback
            print(traceback.format_exc())

def main():
    root = tk.Tk()
    app = MangaUtilityApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()