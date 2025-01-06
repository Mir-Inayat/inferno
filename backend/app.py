from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Document, Person
import os
from werkzeug.utils import secure_filename
from document_processor import DocumentProcessor
from deep_translator import GoogleTranslator

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'tiff', 'txt'}
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize document processor
processor = DocumentProcessor()

# Make sure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database setup
DATABASE_URL = "sqlite:///./documents.db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/documents', methods=['GET'])
def get_documents():
    session = Session()
    try:
        documents = session.query(Document).all()
        return jsonify({
            "status": "success",
            "documents": [{
                "id": doc.id,
                "file_name": doc.file_name,
                "file_path": doc.file_path,
                "primary_category": doc.primary_category,
                "sub_category": doc.sub_category,
                "confidence_score": doc.confidence_score,
                "summary": doc.summary,
                "person": {
                    "name": doc.person.name if doc.person else None,
                    "email": doc.person.email if doc.person else None,
                    "government_id": doc.person.government_id if doc.person else None
                } if doc.person else None,
                "upload_date": doc.upload_date.isoformat() if doc.upload_date else None
            } for doc in documents]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        session.close()

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        print("No files provided in request")
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist('files[]')
    session = Session()
    
    try:
        results = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                print(f"Processing file: {filename}")
                file.save(file_path)
                
                # Process document
                print("Starting document processing...")
                doc_info = processor.process_document(file_path)
                print(f"Document processing result: {doc_info}")
                
                if doc_info.get('status') == 'error':
                    raise Exception(doc_info.get('error', 'Unknown processing error'))
                
                # Save to database
                person_data = doc_info['classification']['person']
                person = session.query(Person).filter_by(
                    government_id=person_data['government_id']
                ).first()
                
                if not person:
                    print(f"Creating new person: {person_data['name']}")
                    person = Person(
                        name=person_data['name'],
                        government_id=person_data['government_id'],
                        email=person_data['email']
                    )
                    session.add(person)
                
                print("Creating document record...")
                document = Document(
                    file_path=file_path,
                    file_name=filename,
                    primary_category=doc_info['classification']['document_type']['primary_category'],
                    sub_category=doc_info['classification']['document_type']['sub_category'],
                    confidence_score=doc_info['classification']['document_type']['confidence_score'],
                    extracted_fields=doc_info['classification']['extracted_fields'],
                    person=person,
                    processing_status='completed'
                )
                session.add(document)
                results.append(doc_info)
                print(f"Successfully processed file: {filename}")
        
        session.commit()
        print("Database transaction committed")
        return jsonify({"status": "success", "results": results})
    
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/download/<int:doc_id>')
def download_document(doc_id):
    session = Session()
    try:
        document = session.query(Document).get(doc_id)
        if document and os.path.exists(document.file_path):
            return send_file(document.file_path)
        return jsonify({"error": "Document not found"}), 404
    finally:
        session.close()

@app.route('/api/translate', methods=['POST'])
def translate_text():
    try:
        data = request.get_json()
        if not data or 'text' not in data or 'target_language' not in data:
            return jsonify({"error": "Missing text or target language"}), 400

        translator = GoogleTranslator(source='auto', target=data['target_language'])
        translated_text = translator.translate(data['text'])
        
        return jsonify({
            "translatedText": translated_text,
            "sourceLanguage": "auto"
        })
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File is too large"}), 413

if __name__ == '__main__':
    app.run(debug=True, port=5000)
