# python_extractor_final.py
import fitz  # PyMuPDF
import os
import re
import time
import platform
import json

PDF_FILE_PATH = "file3.pdf"

def extract_data_natively(pdf_path: str) -> dict:
    start_time = time.time()
    if not os.path.exists(pdf_path):
        return {"error": f"File not found: {pdf_path}"}

    doc = fitz.open(pdf_path)
    results = {
        "extraction_details": {
            "source_method": "Native PDF Text & Object Extraction (No OCR)",
            "file_name": os.path.basename(pdf_path),
            "execution_time_seconds": None,
        },
        "system_information": {
            "python_version": platform.python_version(),
            "os": f"{platform.system()} {platform.release()}",
            "pymupdf_version": fitz.__doc__.split(' ')[1]
        },
        "pdf_internal_details": {
            "page_count": len(doc),
            "metadata": doc.metadata,
            "fonts_on_page_1": [font[3] for font in doc.load_page(0).get_fonts()],
            "images_on_page_1": len(doc.load_page(0).get_images()),
            "vector_drawings_on_page_1": len(doc.load_page(0).get_drawings())
        },
        "extracted_form_data": {}
    }

    page = doc.load_page(0)
    words = page.get_text("words")
    
    # --- Robust Helper Functions ---
    def find_value_on_line(anchor, stop_word=None):
        for i, w in enumerate(words):
            if w[4] == anchor:
                y0 = w[1]
                line_text = []
                for j in range(i + 1, len(words)):
                    if abs(words[j][1] - y0) < 5:
                        if stop_word and stop_word in words[j][4]: break
                        line_text.append(words[j][4])
                    elif line_text: break
                return " ".join(line_text)
        return ""

    def find_value_below(anchor, height_limit=40):
        for i, w in enumerate(words):
            if anchor in w[4]:
                y1 = w[3]
                line_text = []
                for j in range(i + 1, len(words)):
                    if 0 < (words[j][1] - y1) < height_limit:
                        line_text.append(words[j][4])
                return " ".join(line_text)
        return ""

    data = {}
    data["form_type"] = "OREA Form 400 - Agreement to Lease" if "form 400" in page.get_text().lower() else "Unknown"
    data["tenant_name"] = find_value_on_line("TENANT:", stop_word="(")
    data["landlord_name"] = find_value_on_line("LANDLORD:", stop_word="(")
    data["property_address"] = find_value_below("known as:")
    data["lease_start_date"] = find_value_on_line("commencing")
    
    full_text = " ".join([w[4] for w in words])
    rent_match = re.search(r"sum of ([\w\s]+) Dollars \(CDN\$\) ([\d,]+)", full_text, re.IGNORECASE)
    data["monthly_rent"] = float(rent_match.group(2).replace(",", "")) if rent_match else None
    
    deposit_match = re.search(r"amount of ([\w\s]+) Dollars \(CDN\$\) ([\d,]+)", full_text, re.IGNORECASE)
    data["deposit_amount"] = float(deposit_match.group(2).replace(",", "")) if deposit_match else None

    # Corrected Utility Logic
    data["utilities_paid_by"] = {}
    utility_rows = {}
    utility_labels = ["Gas", "Electricity", "Hot", "Water", "Cable", "Garbage"]
    for w in words:
        if any(label in w[4] for label in utility_labels):
            utility_rows[w[1]] = w[4] # Map Y-coordinate to label
    
    for w in words:
        if w[4].lower() == 'x':
            x_y_coord = w[1]
            closest_y = min(utility_rows.keys(), key=lambda y: abs(y - x_y_coord))
            label = utility_rows[closest_y]
            # Column determined by X position
            payee = "Tenant" if w[0] > 400 else "Landlord"
            data["utilities_paid_by"][label] = payee

    data["party_initials"] = [w[4] for w in words if w[1] > 720 and len(w[4]) < 5 and w[4].isalpha()]

    results["extracted_form_data"] = data
    results["extraction_details"]["execution_time_seconds"] = round(time.time() - start_time, 4)
    doc.close()
    return results

if __name__ == "__main__":
    print("--- Running Native Python Extractor (Final Showcase) ---")
    final_data = extract_data_natively(PDF_FILE_PATH)
    print(json.dumps(final_data, indent=2))