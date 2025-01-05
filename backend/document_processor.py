import google.generativeai as genai
from PIL import Image
from pdf2image import convert_from_path
import os
import uuid
from datetime import datetime
import base64
from io import BytesIO

class DocumentProcessor:
    def __init__(self):
        # Configure Gemini API
        self.api_key = "YOUR_GEMINI_API_KEY"
        genai.configure(api_key="AIzaSyBIKuGKwYEmo41cOTXPjKGIu3ue7ELwPus")
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.poppler_path = r"C:\poppler\Library\bin"

    def _extract_document_info(self, image):
        """Extract information using Gemini"""
        try:
            # Convert PIL Image to bytes for Gemini
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            image_bytes = buffered.getvalue()
            
            # Create Gemini-compatible image
            uploaded_file = genai.upload_file(image_bytes)
            
            prompt = """
            Extract the following details from the uploaded document in JSON format:

            Use this JSON schema:
            DocumentData = {
                "person": {
                    "name": str,
                    "email": str,
                    "government_id": str,
                    "dob": str,
                    "address": str
                },
                "document_info": {
                    "document_type": str,
                    "account_type": str,
                    "account_number": str,
                    "application_date": str
                },
                "financial_info": {
                    "income": str,
                    "employer": str,
                    "employment_status": str,
                    "tax_year": str,
                    "transaction_amount": str
                },
                "metadata": {
                    "issuing_authority": str,
                    "expiration_date": str
                }
            }
            Return: DocumentData

            If any field is missing, return its value as null.
            """.strip()

            response = self.model.generate_content([prompt, uploaded_file])
            extracted_data = response.text
            
            # Process the response to match the expected format
            return {
                "person": {
                    "name": extracted_data.get("person", {}).get("name"),
                    "government_id": self._mask_id(extracted_data.get("person", {}).get("government_id")),
                    "email": extracted_data.get("person", {}).get("email"),
                    "confidence_score": 0.95 if extracted_data.get("person", {}).get("name") else 0.5
                },
                "document_type": extracted_data.get("document_info", {}).get("document_type"),
                "extracted_fields": {
                    "document_type": extracted_data.get("document_info", {}).get("account_type"),
                    "role": extracted_data.get("financial_info", {}).get("employment_status"),
                    "annual_income": extracted_data.get("financial_info", {}).get("income")
                }
            }

        except Exception as e:
            print(f"Extraction error: {str(e)}")
            return None

    def _mask_id(self, id_number):
        """Mask sensitive ID information"""
        if not id_number:
            return None
        return f"XXX-XX-{id_number[-4:]}" if len(id_number) >= 4 else "XXX-XX-XXXX"

    def process_document(self, file_path):
        try:
            # Convert document to image(s)
            if file_path.lower().endswith('.pdf'):
                images = convert_from_path(file_path, poppler_path=self.poppler_path)
                page_count = len(images)
                image = images[0]  # Process first page for main info
            else:
                image = Image.open(file_path)
                page_count = 1

            # Extract document info using Gemini
            doc_info = self._extract_document_info(image)
            
            # Generate a summary using Gemini
            summary_prompt = "Provide a brief summary of this document in 2-3 sentences."
            summary_response = self.model.generate_content([summary_prompt, image])
            summary = summary_response.text

            return {
                "status": "success",
                "document_id": f"DOC{uuid.uuid4().hex[:6].upper()}",
                "classification": doc_info,
                "metadata": {
                    "date_received": datetime.now().strftime("%Y-%m-%d"),
                    "processing_timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "file_type": os.path.splitext(file_path)[1][1:],
                    "page_count": page_count
                },
                "summary": summary
            }

        except Exception as e:
            print(f"Processing error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            } 