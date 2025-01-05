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
            # Person Identification
            "name": "What is the person's full name or applicant name?",
            "email": "What is the email address?",
            "government_id": "What is the government ID, SSN, passport number, or driver's license number?",
            "dob": "What is the date of birth?",
            "address": "What is the residential address?",
            
            # Account/Application Related
            "account_type": "What type of account or service is being applied for? (e.g., savings, checking, credit card)",
            "account_number": "Is there any account number or reference number?",
            "application_date": "What is the application or document date?",
            
            # Financial Information
            "income": "What is the annual income or salary mentioned?",
            "employer": "What is the employer name?",
            "employment_status": "What is the employment status?",
            "tax_year": "What tax year is mentioned?",
            "transaction_amount": "What is the transaction or payment amount?",
            
            # Document Specific
            "document_type": "What type of document is this? (e.g., bank statement, tax return, pay stub, receipt)",
            "issuing_authority": "What organization or authority issued this document?",
            "expiration_date": "Is there an expiration date on the document?"
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
            print("text extracted")
            
            # Get document info using LayoutLM
            doc_info = self._extract_document_info(image)
            print("doc_info extracted")
            
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
        """Enhanced document classification for financial documents"""
        doc_type = str(extracted_info.get("document_type", "")).lower()
        account_type = str(extracted_info.get("account_type", "")).lower()
        
        # Primary Categories and their indicators
        categories = {
            "Account Application": {
                "keywords": ["application", "apply", "new account", "credit card", "savings", "checking"],
                "sub_categories": {
                    "Credit Card Application": ["credit card", "credit application", "card application"],
                    "Savings Account": ["savings", "save"],
                    "Checking Account": ["checking", "check"]
                }
            },
            "Identity Document": {
                "keywords": ["passport", "driver", "license", "identification", "id card"],
                "sub_categories": {
                    "Passport": ["passport"],
                    "Driver's License": ["driver", "license", "dmv"],
                    "State ID": ["state id", "identification card"]
                }
            },
            "Financial Statement": {
                "keywords": ["statement", "income", "tax", "return", "paystub", "salary"],
                "sub_categories": {
                    "Tax Return": ["tax", "return", "1040", "w2"],
                    "Pay Stub": ["pay", "stub", "salary", "wage"],
                    "Bank Statement": ["bank statement", "account statement"],
                    "Income Statement": ["income statement", "earnings"]
                }
            },
            "Receipt": {
                "keywords": ["receipt", "payment", "transaction", "purchase"],
                "sub_categories": {
                    "Payment Receipt": ["payment", "paid"],
                    "Transaction Receipt": ["transaction"],
                    "Purchase Receipt": ["purchase"]
                }
            }
        }
        
        def calculate_confidence(text, keywords):
            if not text:
                return 0
            matches = sum(1 for keyword in keywords if keyword in text)
            return min(0.9, (matches * 0.3 + 0.6)) if matches > 0 else 0.5

        # Find best matching category
        best_category = None
        best_sub_category = None
        highest_confidence = 0

        for category, data in categories.items():
            confidence = calculate_confidence(doc_type + " " + account_type, data["keywords"])
            
            if confidence > highest_confidence:
                highest_confidence = confidence
                best_category = category
                
                # Find best sub-category
                best_sub_conf = 0
                for sub_cat, sub_keywords in data["sub_categories"].items():
                    sub_conf = calculate_confidence(doc_type + " " + account_type, sub_keywords)
                    if sub_conf > best_sub_conf:
                        best_sub_conf = sub_conf
                        best_sub_category = sub_cat

        return {
            "primary_category": best_category or "Unknown Document",
            "sub_category": best_sub_category or "General",
            "confidence_score": highest_confidence
        } 