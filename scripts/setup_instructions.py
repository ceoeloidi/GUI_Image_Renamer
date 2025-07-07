"""
Setup Instructions for Image Renamer GUI

Before running the application, you need to install the required dependencies:

1. Install Python packages:
   pip install Pillow pytesseract

2. Install Tesseract OCR:
   
   Windows:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install and add to PATH, or set pytesseract.pytesseract.tesseract_cmd path
   
   macOS:
   - brew install tesseract
   
   Linux (Ubuntu/Debian):
   - sudo apt-get install tesseract-ocr

3. Run the application:
   python image_renamer_gui.py

Features:
- Select multiple JPG images for batch processing
- Define OCR zones by clicking and dragging on image preview
- Test OCR on selected zones before processing
- Choose destination folder for renamed files
- Options to clean text and add counters
- Progress tracking and error handling
"""

print(__doc__)
