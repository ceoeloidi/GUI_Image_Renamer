import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
from PIL import Image, ImageTk
import pytesseract
import re
from pathlib import Path

class ImageRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch Image Renamer with Zonal OCR")
        self.root.geometry("800x600")
        
        # Variables
        self.source_files = []
        self.destination_folder = tk.StringVar()
        self.ocr_zones = []  # List of (x1, y1, x2, y2) tuples
        self.current_image = None
        self.current_image_path = ""
        self.preview_image = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Source files section
        ttk.Label(main_frame, text="Source JPG Files:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        files_frame = ttk.Frame(main_frame)
        files_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        files_frame.columnconfigure(0, weight=1)
        
        self.files_listbox = tk.Listbox(files_frame, height=6)
        self.files_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.files_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
        files_scrollbar = ttk.Scrollbar(files_frame, orient="vertical", command=self.files_listbox.yview)
        files_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.files_listbox.configure(yscrollcommand=files_scrollbar.set)
        
        ttk.Button(files_frame, text="Select Files", command=self.select_files).grid(row=1, column=0, pady=(5, 0))
        
        # Image preview and zone selection
        preview_frame = ttk.LabelFrame(main_frame, text="Image Preview & Zone Selection", padding="5")
        preview_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # Canvas for image preview
        self.canvas = tk.Canvas(preview_frame, width=400, height=300, bg="white")
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.canvas.bind("<Button-1>", self.start_zone_selection)
        self.canvas.bind("<B1-Motion>", self.update_zone_selection)
        self.canvas.bind("<ButtonRelease-1>", self.end_zone_selection)
        
        # Zone selection variables
        self.zone_start_x = 0
        self.zone_start_y = 0
        self.zone_rect = None
        
        # Zone controls
        zone_controls = ttk.Frame(preview_frame)
        zone_controls.grid(row=1, column=0, pady=(5, 0))
        
        ttk.Label(zone_controls, text="OCR Zones:").pack(side=tk.LEFT)
        self.zones_var = tk.StringVar()
        self.zones_label = ttk.Label(zone_controls, textvariable=self.zones_var)
        self.zones_label.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(zone_controls, text="Clear Zones", command=self.clear_zones).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(zone_controls, text="Test OCR", command=self.test_ocr).pack(side=tk.RIGHT)
        
        # Destination folder
        ttk.Label(main_frame, text="Destination Folder:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        
        dest_frame = ttk.Frame(main_frame)
        dest_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        dest_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(dest_frame, textvariable=self.destination_folder, state="readonly").grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(dest_frame, text="Browse", command=self.select_destination).grid(row=0, column=1)
        
        # Processing options
        options_frame = ttk.LabelFrame(main_frame, text="Processing Options", padding="5")
        options_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.clean_text_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Clean OCR text (remove special characters)", 
                       variable=self.clean_text_var).pack(anchor=tk.W)
        
        self.add_counter_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Add counter to prevent duplicate names", 
                       variable=self.add_counter_var).pack(anchor=tk.W)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=7, column=0, columnspan=2, pady=(0, 10))
        
        # Process button
        self.process_button = ttk.Button(main_frame, text="Process Images", command=self.process_images)
        self.process_button.grid(row=8, column=0, columnspan=2, pady=10)
        
    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select JPG Images",
            filetypes=[("JPEG files", "*.jpg *.jpeg"), ("All files", "*.*")]
        )
        if files:
            self.source_files = list(files)
            self.files_listbox.delete(0, tk.END)
            for file in self.source_files:
                self.files_listbox.insert(tk.END, os.path.basename(file))
            self.status_var.set(f"Selected {len(self.source_files)} files")
            
    def on_file_select(self, event):
        selection = self.files_listbox.curselection()
        if selection:
            index = selection[0]
            self.current_image_path = self.source_files[index]
            self.load_image_preview()
            
    def load_image_preview(self):
        try:
            # Load and resize image for preview
            image = Image.open(self.current_image_path)
            self.current_image = image.copy()
            
            # Calculate size to fit canvas
            canvas_width = self.canvas.winfo_width() or 400
            canvas_height = self.canvas.winfo_height() or 300
            
            image.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            self.preview_image = ImageTk.PhotoImage(image)
            
            # Clear canvas and display image
            self.canvas.delete("all")
            self.canvas.create_image(canvas_width//2, canvas_height//2, image=self.preview_image)
            
            # Redraw zones
            self.redraw_zones()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            
    def start_zone_selection(self, event):
        self.zone_start_x = event.x
        self.zone_start_y = event.y
        
    def update_zone_selection(self, event):
        if self.zone_rect:
            self.canvas.delete(self.zone_rect)
        self.zone_rect = self.canvas.create_rectangle(
            self.zone_start_x, self.zone_start_y, event.x, event.y,
            outline="red", width=2
        )
        
    def end_zone_selection(self, event):
        if abs(event.x - self.zone_start_x) > 10 and abs(event.y - self.zone_start_y) > 10:
            # Convert canvas coordinates to image coordinates
            if self.current_image and self.preview_image:
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                
                # Get the actual displayed image size
                img_width = self.preview_image.width()
                img_height = self.preview_image.height()
                
                # Calculate the offset (image is centered)
                x_offset = (canvas_width - img_width) // 2
                y_offset = (canvas_height - img_height) // 2
                
                # Convert to image coordinates
                x1 = max(0, min(self.zone_start_x, event.x) - x_offset)
                y1 = max(0, min(self.zone_start_y, event.y) - y_offset)
                x2 = min(img_width, max(self.zone_start_x, event.x) - x_offset)
                y2 = min(img_height, max(self.zone_start_y, event.y) - y_offset)
                
                # Scale to original image size
                scale_x = self.current_image.width / img_width
                scale_y = self.current_image.height / img_height
                
                zone = (int(x1 * scale_x), int(y1 * scale_y), int(x2 * scale_x), int(y2 * scale_y))
                self.ocr_zones.append(zone)
                self.update_zones_display()
                
    def redraw_zones(self):
        if not self.current_image or not self.preview_image:
            return
            
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_width = self.preview_image.width()
        img_height = self.preview_image.height()
        
        x_offset = (canvas_width - img_width) // 2
        y_offset = (canvas_height - img_height) // 2
        
        scale_x = img_width / self.current_image.width
        scale_y = img_height / self.current_image.height
        
        for i, zone in enumerate(self.ocr_zones):
            x1, y1, x2, y2 = zone
            canvas_x1 = int(x1 * scale_x) + x_offset
            canvas_y1 = int(y1 * scale_y) + y_offset
            canvas_x2 = int(x2 * scale_x) + x_offset
            canvas_y2 = int(y2 * scale_y) + y_offset
            
            self.canvas.create_rectangle(canvas_x1, canvas_y1, canvas_x2, canvas_y2,
                                       outline="blue", width=2)
            self.canvas.create_text(canvas_x1 + 5, canvas_y1 + 5, text=f"Zone {i+1}",
                                  fill="blue", anchor="nw")
                                  
    def update_zones_display(self):
        self.zones_var.set(f"{len(self.ocr_zones)} zones defined")
        self.redraw_zones()
        
    def clear_zones(self):
        self.ocr_zones.clear()
        self.update_zones_display()
        if self.current_image_path:
            self.load_image_preview()
            
    def test_ocr(self):
        if not self.current_image_path or not self.ocr_zones:
            messagebox.showwarning("Warning", "Please select an image and define OCR zones first.")
            return
            
        try:
            image = Image.open(self.current_image_path)
            ocr_results = []
            
            for i, zone in enumerate(self.ocr_zones):
                x1, y1, x2, y2 = zone
                cropped = image.crop((x1, y1, x2, y2))
                text = pytesseract.image_to_string(cropped).strip()
                if self.clean_text_var.get():
                    text = self.clean_ocr_text(text)
                ocr_results.append(f"Zone {i+1}: '{text}'")
                
            result_text = "\n".join(ocr_results)
            messagebox.showinfo("OCR Test Results", result_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"OCR test failed: {str(e)}")
            
    def clean_ocr_text(self, text):
        # Remove special characters and extra whitespace
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'\s+', '_', text.strip())
        return text
        
    def select_destination(self):
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.destination_folder.set(folder)
            
    def process_images(self):
        if not self.source_files:
            messagebox.showwarning("Warning", "Please select source files first.")
            return
            
        if not self.destination_folder.get():
            messagebox.showwarning("Warning", "Please select a destination folder.")
            return
            
        if not self.ocr_zones:
            messagebox.showwarning("Warning", "Please define at least one OCR zone.")
            return
            
        try:
            self.process_button.config(state="disabled")
            total_files = len(self.source_files)
            processed_count = 0
            error_count = 0
            
            for i, source_path in enumerate(self.source_files):
                try:
                    self.status_var.set(f"Processing {os.path.basename(source_path)}...")
                    self.root.update()
                    
                    # Perform OCR
                    image = Image.open(source_path)
                    ocr_texts = []
                    
                    for zone in self.ocr_zones:
                        x1, y1, x2, y2 = zone
                        cropped = image.crop((x1, y1, x2, y2))
                        text = pytesseract.image_to_string(cropped).strip()
                        if self.clean_text_var.get():
                            text = self.clean_ocr_text(text)
                        if text:
                            ocr_texts.append(text)
                    
                    # Generate new filename
                    if ocr_texts:
                        new_name = "_".join(ocr_texts)
                    else:
                        new_name = f"no_text_found_{i+1}"
                        
                    # Add counter if needed
                    if self.add_counter_var.get():
                        new_name = f"{i+1:03d}_{new_name}"
                        
                    # Ensure valid filename
                    new_name = re.sub(r'[<>:"/\\|?*]', '_', new_name)
                    new_name = new_name[:100]  # Limit length
                    
                    # Copy file with new name
                    file_ext = os.path.splitext(source_path)[1]
                    dest_path = os.path.join(self.destination_folder.get(), f"{new_name}{file_ext}")
                    
                    # Handle duplicate names
                    counter = 1
                    original_dest_path = dest_path
                    while os.path.exists(dest_path):
                        name_part = os.path.splitext(original_dest_path)[0]
                        dest_path = f"{name_part}_{counter}{file_ext}"
                        counter += 1
                        
                    shutil.copy2(source_path, dest_path)
                    processed_count += 1
                    
                except Exception as e:
                    print(f"Error processing {source_path}: {str(e)}")
                    error_count += 1
                    
                # Update progress
                progress = ((i + 1) / total_files) * 100
                self.progress_var.set(progress)
                self.root.update()
                
            # Show completion message
            message = f"Processing complete!\nProcessed: {processed_count}\nErrors: {error_count}"
            messagebox.showinfo("Complete", message)
            
            self.status_var.set("Ready")
            self.progress_var.set(0)
            
        except Exception as e:
            messagebox.showerror("Error", f"Processing failed: {str(e)}")
            
        finally:
            self.process_button.config(state="normal")

def main():
    root = tk.Tk()
    app = ImageRenamerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
