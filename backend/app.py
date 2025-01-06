from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Document, Person
import os
from werkzeug.utils import secure_filename
from document_processor import DocumentProcessor
from deep_translator import GoogleTranslator
from celery import Celery

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

# Celery setup
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend='redis://localhost:6379/0',  # Results backend
        broker='redis://localhost:6379/0'   # Message broker
    )
    celery.conf.update(app.config)
    return celery

app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://localhost:6379/0'
)

celery = make_celery(app)

#Celery task for processing documents asynchronously.

@celery.task
def process_document_async(file_path):
    # Perform document processing asynchronously
    # Example: Call your existing document processing logic
    processor = DocumentProcessor()
    result = processor.process_document(file_path)
    return result


#By this method we check the status of the tast using its task_id.
@app.route('/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task = process_document_async.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            "state": task.state,
            "status": "Task is pending"
        }
    elif task.state != 'FAILURE':
        response = {
            "state": task.state,
            "result": task.result
        }
    else:
        response = {
            "state": task.state,
            "status": str(task.info)  # Contains error traceback
        }
    
    return jsonify(response)



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
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist('files[]')
    session = Session()
    
    try:
        task_ids = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # Enqueue the Celery task
                task = process_document_async.delay(file_path)
                task_ids.append(task.id)

        return jsonify({"status": "success", "tasks": task_ids})
    
    except Exception as e:
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
