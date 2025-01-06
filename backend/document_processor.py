import google.generativeai as genai
import os
import uuid
from datetime import datetime
import json

class DocumentProcessor:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key="AIzaSyBIKuGKwYEmo41cOTXPjKGIu3ue7ELwPus")
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.poppler_path = r"C:\poppler\Library\bin"

    def _extract_document_info(self, file_path):
        """Extract information using Gemini"""
        try:
            # Upload file directly to Gemini (supports both PDFs and images)
            file = genai.upload_file(file_path)
            
            prompt = """
            Analyze this document and provide the information in JSON format.
            Return ONLY the JSON, no additional text.
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

            # Use vision model to analyze document
            response = self.model.generate_content([prompt, file])
            
            # Process response
            response_text = response.text.strip()
            json_str = response_text.replace('```json', '').replace('```', '').strip()
            
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except json.JSONDecodeError:
                        raise ValueError("Could not parse JSON from response")
                return self._get_default_structure()

        except Exception as e:
            print(f"Extraction error: {str(e)}")
            return self._get_default_structure()

    def _mask_id(self, id_number):
        """Mask sensitive ID information"""
        if not id_number:
            return None
        return f"XXX-XX-{id_number[-4:]}" if len(id_number) >= 4 else "XXX-XX-XXXX"

    def process_document(self, file_path):
        try:
            # Extract document info using Gemini
            doc_info = self._extract_document_info(file_path)
            
            # Generate a summary using Gemini
            file = genai.upload_file(file_path)
            summary_prompt = "Provide a brief summary of this document in 2-3 sentences."
            summary_response = self.model.generate_content([summary_prompt, file])
            summary = summary_response.text

            return {
                "status": "success",
                "document_id": f"DOC{uuid.uuid4().hex[:6].upper()}",
                "classification": doc_info,
                "metadata": {
                    "date_received": datetime.now().strftime("%Y-%m-%d"),
                    "processing_timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "file_type": os.path.splitext(file_path)[1][1:],
                    "page_count": 1  # You might want to add PDF page counting if needed
                },
                "summary": summary
            }

        except Exception as e:
            print(f"Processing error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }