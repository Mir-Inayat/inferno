import requests
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os
import uuid
from datetime import datetime
import re
from transformers import pipeline
import time

class DocumentProcessor:
    def __init__(self):
        # Use the provided API token
        self.api_token = "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"
        self.headers = {"Authorization": f"Bearer {self.api_token}"}
        self.summarizer_api = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        self.qa_api = "https://api-inference.huggingface.co/models/impira/layoutlm-document-qa"
        self.poppler_path = r"C:\poppler\Library\bin"

    def _extract_field_with_qa(self, image, question):
        """Extract information using LayoutLM QA with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                payload = {
                    "inputs": {
                        "image": self._encode_image(image),
                        "question": question
                    }
                }
                
                response = requests.post(
                    self.qa_api, 
                    headers=self.headers, 
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 503:
                    # Model is loading, wait and retry
                    time.sleep(5)
                    continue
                    
                response.raise_for_status()
                result = response.json()
                return result[0].get('answer') if result else None

            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"QA extraction failed for {question}: {str(e)}")
                    return None
                time.sleep(2)

    def _encode_image(self, image):
        """Convert PIL Image to base64"""
        import base64
        from io import BytesIO
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    def _extract_document_info(self, image):
        """Extract all relevant information using LayoutLM QA"""
        questions = {
            "name": "What is the person's full name or applicant name?",
            "email": "What is the email address?",
            "government_id": "What is the government ID, SSN, or identification number?",
            "account_type": "What type of document is this? Is it a resume, application, or other document type?",
            "employment": "What is the current job title or role?",
            "income": "What is the annual income or salary mentioned?",
            "education": "What is the highest education level or degree?"
        }
        
        info = {}
        for field, question in questions.items():
            info[field] = self._extract_field_with_qa(image, question)

        # Improve document classification based on content
        doc_type = self._classify_document(info)
        
        return {
            "person": {
                "name": info.get("name"),
                "government_id": f"XXX-XX-{info['government_id'][-4:]}" if info.get("government_id") else None,
                "email": info.get("email"),
                "confidence_score": 0.95 if info.get("name") and info.get("email") else 0.5
            },
            "document_type": doc_type,
            "extracted_fields": {
                "document_type": info.get("account_type"),
                "role": info.get("employment"),
                "education": info.get("education"),
                "annual_income": info.get("income")
            }
        }

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

            # Extract text for summary
            text = pytesseract.image_to_string(image)
            print(text)
            
            # Get document info using LayoutLM
            doc_info = self._extract_document_info(image)
            print(doc_info)
            
            # Generate summary
            summary = self._generate_summary(text)

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

    def _generate_summary(self, text):
        try:
            payload = {"inputs": text[:1000], "parameters": {"max_length": 150, "min_length": 40}}
            response = requests.post(self.summarizer_api, headers=self.headers, json=payload)
            response.raise_for_status()  # Raise exception for bad status codes
            return response.json()[0]['summary_text']
        except Exception as e:
            raise Exception(f"Summary generation failed: {str(e)}")

    def _classify_document(self, extracted_info):
        """Classify document based on extracted information"""
        doc_type = str(extracted_info.get("account_type", "")).lower()
        employment = str(extracted_info.get("employment", "")).lower()
        
        if "resume" in doc_type or "cv" in doc_type:
            return {
                "primary_category": "Professional Document",
                "sub_category": "Resume/CV",
                "confidence_score": 0.9
            }
        elif employment and "developer" in employment.lower():
            return {
                "primary_category": "Professional Document",
                "sub_category": "Technical Resume",
                "confidence_score": 0.85
            }
        else:
            return {
                "primary_category": "Professional Document",
                "sub_category": "Unknown",
                "confidence_score": 0.7
            } 