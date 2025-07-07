# GUI_Image_Renamer

This Python GUI application provides a complete solution for batch renaming JPG images using zonal OCR. Here are the key features:

## Key Features:

1. **File Selection**: Browse and select multiple JPG files for processing
2. **Image Preview**: View selected images in a canvas with zoom-to-fit
3. **Zone Definition**: Click and drag to define OCR zones on images
4. **OCR Testing**: Test OCR on defined zones before batch processing
5. **Destination Selection**: Choose where to save renamed files
6. **Text Cleaning**: Option to remove special characters from OCR text
7. **Counter Addition**: Add sequential numbers to prevent duplicate names
8. **Progress Tracking**: Visual progress bar and status updates
9. **Error Handling**: Graceful handling of OCR and file operation errors


## How to Use:

1. **Install Dependencies**: Run the requirements installation
2. **Select Images**: Click "Select Files" to choose JPG images
3. **Define OCR Zones**: Select an image, then click and drag to create OCR zones
4. **Test OCR**: Use "Test OCR" to verify text extraction
5. **Choose Destination**: Select where to save renamed files
6. **Process**: Click "Process Images" to rename and copy files


## Technical Details:

- Uses **tkinter** for the GUI (built into Python)
- **Pillow (PIL)** for image handling and display
- **pytesseract** for OCR functionality
- Supports multiple OCR zones per image
- Handles duplicate filenames automatically
- Preserves original files (copies to destination)
