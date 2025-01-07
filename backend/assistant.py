import google.generativeai as genai
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Document, Person, Category, Base
import json

class DocumentAssistant:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key="AIzaSyBIKuGKwYEmo41cOTXPjKGIu3ue7ELwPus")
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Configure database connection
        self.engine = create_engine('sqlite:///documents.db')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Initialize conversation history
        self.chat = self.model.start_chat(history=[])

    def _get_detailed_document_context(self):
        """Retrieve detailed document information including full content from database"""
        context = {
            'documents': [],
            'persons': [],
            'categories': []
        }
        
        # Get all documents with their related information
        documents = self.session.query(Document).all()
        for doc in documents:
            doc_info = {
                'id': doc.id,
                'primary_category': doc.primary_category,
                'sub_category': doc.sub_category,
                'summary': doc.summary,
                'processed_text': doc.processed_text,  # Full document content
                'extracted_fields': doc.extracted_fields,
                'file_type': doc.file_type,
                'upload_date': str(doc.upload_date) if doc.upload_date else None,
                'doc_metadata': doc.doc_metadata
            }
            
            # Add categories information
            doc_categories = []
            for category in doc.categories:
                doc_categories.append({
                    'name': category.name,
                    'description': category.description
                })
            doc_info['categories'] = doc_categories
            
            context['documents'].append(doc_info)
            
            # Add person information if available
            if doc.person:
                person_info = {
                    'id': doc.person.id,
                    'name': doc.person.name,
                    'email': doc.person.email
                }
                if person_info not in context['persons']:
                    context['persons'].append(person_info)

        return context

    def ask_question(self, question):
        """Process user question and provide an answer based on detailed document content"""
        try:
            # Get detailed context from database
            context = self._get_detailed_document_context()
            
            # Construct prompt with enhanced focus on document content
            prompt = f"""
            Given the following document database context:
            {json.dumps(context, indent=2)}

            Please answer this question: {question}

            Rules:
            1. Focus primarily on document content and summaries when answering
            2. Quote relevant portions of documents when applicable
            3. If multiple documents are relevant, mention all of them
            4. Provide specific details from the document content
            5. If the answer requires information from specific documents, cite them by ID
            6. Don't reveal sensitive personal information
            7. If you can't find relevant information in the documents, say so
            8. Organize the answer with document references first, followed by relevant quotes or content
            """

            # Get response from Gemini
            response = self.chat.send_message(prompt)
            return response.text

        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"

    def get_document_details(self, document_id):
        """Get comprehensive details about a specific document"""
        try:
            document = self.session.query(Document).filter(Document.id == document_id).first()
            if document:
                details = {
                    'id': document.id,
                    'summary': document.summary,
                    'processed_text': document.processed_text,
                    'categories': [cat.name for cat in document.categories],
                    'extracted_fields': document.extracted_fields,
                    'metadata': document.doc_metadata
                }
                
                prompt = f"""
                Analyze this document information and provide a detailed overview:
                {json.dumps(details, indent=2)}
                
                Include:
                1. Main topics or themes
                2. Key points from the content
                3. Important extracted information
                4. Document classification and relevance
                """
                
                response = self.model.generate_content(prompt)
                return response.text
            return "Document not found"
        except Exception as e:
            return f"Error retrieving document details: {str(e)}"

    def search_documents(self, query):
        """Enhanced search through documents with content-based matching"""
        try:
            context = self._get_detailed_document_context()
            
            prompt = f"""
            Given these documents with their full content:
            {json.dumps(context['documents'], indent=2)}

            Search query: "{query}"
            
            Provide a detailed response that:
            1. Lists relevant documents by ID
            2. Explains why each document matches
            3. Quotes relevant portions of the matching documents
            4. Ranks the documents by relevance to the query
            """

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            return f"Search error: {str(e)}"

    def close(self):
        """Close the database session"""
        self.session.close()

def main():
    assistant = DocumentAssistant()
    print("Document Assistant initialized. Type 'quit' to exit.")
    print("\nYou can:")
    print("1. Ask questions about document content")
    print("2. Search for specific information")
    print("3. Get detailed document analysis (use 'analyze doc_id')")
    
    try:
        while True:
            user_input = input("\nWhat would you like to know about the documents? ")
            if user_input.lower() == 'quit':
                break
            
            if user_input.lower().startswith('analyze'):
                try:
                    doc_id = int(user_input.split()[1])
                    answer = assistant.get_document_details(doc_id)
                except (IndexError, ValueError):
                    answer = "Please provide a valid document ID (e.g., 'analyze 1')"
            else:
                answer = assistant.ask_question(user_input)
            
            print("\nAssistant:", answer)
    
    finally:
        assistant.close()

if __name__ == "__main__":
    main() 