# explore_extraction.py
import os
import sys
import json
from PIL import Image
import fitz  # PyMuPDF
import pytesseract
import google.generativeai as genai

# --- CONFIGURATION ---
# The script will use this API key directly.
# In a real production app, use environment variables.
GEMINI_API_KEY = 'AIzaSyArqBP--GuazTdXz7rLE2kXKuSPWZj0RPc'

PDF_FILE_PATH = "file3.pdf"

# --- METHOD 1: Direct AI Extraction with Gemini 1.5 Pro ---
# See the other file for the Gemini extraction 

# --- METHOD 2: Classic OCR with Tesseract for Coordinate Data ---

def run_tesseract_ocr(pdf_path: str):
    """
    Converts a PDF to images and runs Tesseract OCR to extract all text
    along with its bounding box coordinates.
    """
    print("\n" + "="*80)
    print("🔎 METHOD 2: CLASSIC OCR + COORDINATE MAPPING (TESSERACT)")
    print("="*80)

    try:
        print(f"[INFO] Opening '{pdf_path}' for OCR processing...")
        doc = fitz.open(pdf_path)
        
        # We will focus on the first page for a clear, representative sample.
        # To process all pages, loop through `range(len(doc))`.
        page_num = 0
        page = doc.load_page(page_num)
        
        print(f"[INFO] Converting Page {page_num + 1} to an image for Tesseract...")
        pix = page.get_pixmap(dpi=300)  # Higher DPI for better accuracy
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        print("[INFO] Running Tesseract's image_to_data to get text and coordinates...")
        # This is the core function to get detailed data
        ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        
        print(f"[SUCCESS] Tesseract processed the page.")
        
        print("\n--- Tesseract OCR Results (Page 1 Sample) ---")
        print("This shows every piece of text Tesseract found and its location.")
        print(f"{'Text':<25} | {'Conf':>5} | {'Left':>5} | {'Top':>5} | {'Width':>5} | {'Height':>6}")
        print("-" * 70)
        
        num_items = len(ocr_data['text'])
        for i in range(num_items):
            # Only print items with actual text and a reasonable confidence
            text = ocr_data['text'][i].strip()
            conf = int(ocr_data['conf'][i])
            if text and conf > 50: # Filter out noise
                left = ocr_data['left'][i]
                top = ocr_data['top'][i]
                width = ocr_data['width'][i]
                height = ocr_data['height'][i]
                
                print(f"{text:<25} | {conf:>5} | {left:>5} | {top:>5} | {width:>5} | {height:>6}")

    except Exception as e:
        print(f"[FATAL ERROR] An error occurred during Tesseract OCR: {e}", file=sys.stderr)


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    if not os.path.exists(PDF_FILE_PATH):
        print(f"[FATAL] PDF file not found! Please make sure '{PDF_FILE_PATH}' is in the same directory as the script.", file=sys.stderr)
    else:
        run_gemini_extraction(PDF_FILE_PATH)
        run_tesseract_ocr(PDF_FILE_PATH)