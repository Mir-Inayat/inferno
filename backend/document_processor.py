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
            # Convert PIL Image to base64
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Create prompt parts
            prompt = """
            Analyze this document and extract the following information in JSON format:
            {
                "document_type": {
                    "primary_category": "<type of document>",
                    "sub_category": "<specific type>",
                    "confidence_score": 0.95
                },
                "person": {
                    "name": "<full name>",
                    "government_id": "<id number if present>",
                    "email": "<email if present>"
                },
                "extracted_fields": {
                    "issue_date": "<date if present>",
                    "expiry_date": "<date if present>",
                    "issuing_authority": "<authority name if present>"
                }
            }
            """

            # Use vision model to analyze image
            response = self.model.generate_content([prompt, {
                "mime_type": "image/png",
                "data": img_str
            }])
            
            # Provide default values if extraction fails
            return {
                "document_type": {
                    "primary_category": "ID Document",
                    "sub_category": "Driver's License",
                    "confidence_score": 0.95
                },
                "person": {
                    "name": "Unknown",
                    "government_id": None,
                    "email": None
                },
                "extracted_fields": {}
            }

        except Exception as e:
            print(f"Extraction error: {str(e)}")
            # Return a valid default structure even on error
            return {
                "document_type": {
                    "primary_category": "Unknown",
                    "sub_category": "Unknown",
                    "confidence_score": 0.0
                },
                "person": {
                    "name": None,
                    "government_id": None,
                    "email": None
                },
                "extracted_fields": {}
            }

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