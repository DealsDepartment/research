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
def run_gemini_extraction(pdf_path: str):
    """
    Uploads a PDF directly to Gemini 1.5 Pro and extracts structured data
    based on a detailed prompt.
    """
    print("\n" + "="*80)
    print("🚀 METHOD 1: DIRECT AI EXTRACTION (GEMINI 1.5 PRO)")
    print("="*80)
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        print(f"[INFO] Uploading '{pdf_path}' to Gemini... (this may take a moment)")
        # Gemini 1.5 Pro can handle native file uploads.
        pdf_file = genai.upload_file(path=pdf_path, display_name="Lease Agreement")
        print(f"[SUCCESS] File uploaded successfully. File URI: {pdf_file.uri}")

        model = genai.GenerativeModel(model_name="models/gemini-2.5-pro-latest")

        # This prompt is designed for maximum information retrieval.
        prompt = """
        You are a world-class paralegal AI specializing in Ontario real estate documents.
        Analyze the provided PDF file (OREA Form 400) in its entirety. Extract a comprehensive
        set of information and return it as a single, clean JSON object.
        Do not include any text outside of the JSON.

        Extract the following:
        
        1.  **Parties**:
            - "tenant_full_name": Full legal name of the Tenant.
            - "landlord_full_name": Full legal name of the Landlord.
            - "tenant_initials": The initials of the Tenant found at the bottom of the pages.
            - "landlord_initials": The initials of the Landlord found at the bottom of the pages.

        2.  **Addresses**:
            - "property_leased_address": The full address of the property being leased.
            - "landlord_notice_address": The Landlord's address for receiving notices.
            - "tenant_notice_address": The Tenant's address for service after the lease begins.

        3.  **Lease Terms**:
            - "lease_term_duration": A descriptive string of the lease term (e.g., "1 year").
            - "lease_start_date": The commencement date in "YYYY-MM-DD" format.
            - "agreement_date": The date the agreement was made, in "YYYY-MM-DD" format.
            - "irrevocability_date": The date the offer is irrevocable until, in "YYYY-MM-DD" format.
            - "irrevocability_time": The time the offer is irrevocable until (e.g., "11:59 pm").

        4.  **Financials**:
            - "monthly_rent_amount": The monthly rent as a number (float).
            - "monthly_rent_in_words": The monthly rent written in words.
            - "deposit_amount": The total deposit paid as a number (float).
            - "deposit_in_words": The deposit amount written in words.
            - "deposit_payable_to": The entity the deposit cheque is payable to.

        5.  **Utilities & Services (Return a list of objects)**:
            - "services": An array of objects, each with "service_name" and "paid_by" ('Landlord' or 'Tenant').
              Analyze all checkboxes including Gas, Electricity, Water, Cable TV, etc.

        6.  **Conditions & Clauses**:
            - "use_of_premises": The specified use of the premises.
            - "parking_description": The description of parking (e.g., "1 Included").
            - "locker_description": The description of the locker.
            - "schedules_attached": A list of attached schedules (e.g., ["A", "B"]).
            - "credit_check_clause_days": The number of business days the tenant has to provide a credit check.

        7.  **Brokerage Information**:
            - "listing_brokerage_name": Name of the listing brokerage.
            - "listing_brokerage_phone": Phone number of the listing brokerage.
            - "co_op_brokerage_name": Name of the tenant's brokerage.
            - "co_op_brokerage_phone": Phone number of the tenant's brokerage.
            
        8. **Signatures**:
           - "is_tenant_signature_present": boolean (true if a signature is visible in the tenant section).
           - "is_landlord_signature_present": boolean (true if a signature is visible in the landlord section).
           - "signature_date": The date the agreement was signed by the parties, in "YYYY-MM-DD" format.
        """

        print("[INFO] Sending comprehensive extraction prompt to Gemini 1.5 Pro...")
        response = model.generate_content([prompt, pdf_file])
        
        print("[SUCCESS] Received response from Gemini.")
        print("\n--- Gemini 1.5 Pro Extraction Results ---")
        # Clean up and print the JSON response
        json_response = json.loads(response.text.strip())
        print(json.dumps(json_response, indent=2))

    except Exception as e:
        print(f"[FATAL ERROR] An error occurred during Gemini extraction: {e}", file=sys.stderr)
