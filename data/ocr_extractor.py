import fitz
from PIL import Image
import pytesseract
import os
import re
import time
import platform
import json
import statistics

PDF_FILE_PATH = "file3.pdf"

def extract_data_with_ocr(pdf_path: str) -> dict:
    start_time = time.time()
    if not os.path.exists(pdf_path):
        return {"error": f"File not found: {pdf_path}"}

    doc = fitz.open(pdf_path)
    results = {
        "extraction_details": {
            "source_method": "Tesseract OCR Extraction",
            "file_name": os.path.basename(pdf_path),
            "execution_time_seconds": None,
        },
        "system_information": {
            "python_version": platform.python_version(),
            "os": f"{platform.system()} {platform.release()}",
            "pytesseract_version": pytesseract.get_tesseract_version()
        },
        "ocr_specific_details": {
            "image_dpi_for_ocr": 300,
            "avg_word_confidence_page_1": None,
        },
        "extracted_form_data": {}
    }

    page = doc.load_page(0)
    pix = page.get_pixmap(dpi=results["ocr_specific_details"]["image_dpi_for_ocr"])
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    
    # Calculate OCR confidence
    confidences = [int(c) for c in ocr_data['conf'] if int(c) > -1]
    if confidences:
        results["ocr_specific_details"]["avg_word_confidence_page_1"] = round(statistics.mean(confidences), 2)

    # --- Robust Helper Functions for OCR data ---
    def find_value_on_line(anchor, stop_word=None):
        num_items = len(ocr_data['text'])
        for i in range(num_items):
            if anchor in ocr_data['text'][i]:
                y0 = ocr_data['top'][i]
                line_text = []
                for j in range(i + 1, num_items):
                    if abs(ocr_data['top'][j] - y0) < 10:
                        current_word = ocr_data['text'][j]
                        if stop_word and stop_word in current_word: break
                        line_text.append(current_word)
                    elif line_text: break
                return " ".join(line_text)
        return ""

    data = {}
    full_text_p1 = " ".join(ocr_data['text']).lower()
    data["form_type"] = "OREA Form 400 - Agreement to Lease" if "form 400" in full_text_p1 else "Unknown"
    data["tenant_name"] = find_value_on_line("TENANT:")
    data["landlord_name"] = find_value_on_line("LANDLORD:")
    data["property_address"] = find_value_on_line("as:")
    data["lease_start_date"] = find_value_on_line("commencing")
    
    rent_match = re.search(r"sum of ([\w\s]+) ([\d,]+)", full_text_p1, re.IGNORECASE)
    data["monthly_rent"] = float(rent_match.group(2).replace(",", "")) if rent_match else None
    
    deposit_match = re.search(r"amount of ([\w\s]+) ([\d,]+)", full_text_p1, re.IGNORECASE)
    data["deposit_amount"] = float(deposit_match.group(2).replace(",", "")) if deposit_match else None

    data["utilities_paid_by"] = "Checkbox logic is too brittle for OCR and requires advanced computer vision."
    data["party_initials"] = [ocr_data['text'][i] for i, top in enumerate(ocr_data['top']) if top > (pix.height * 0.9) and ocr_data['text'][i].isalpha() and len(ocr_data['text'][i]) < 5]

    results["extracted_form_data"] = data
    results["extraction_details"]["execution_time_seconds"] = round(time.time() - start_time, 4)
    doc.close()
    return results

if __name__ == "__main__":
    print("--- Running OCR-Based Extractor (Final Showcase) ---")
    final_data = extract_data_with_ocr(PDF_FILE_PATH)
    print(json.dumps(final_data, indent=2))