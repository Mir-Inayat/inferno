from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from document_processor import DocumentProcessor

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'tiff', 'txt'}
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize document processor
processor = DocumentProcessor()

# Make sure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_files():
    # Check if any file was sent
    if 'files[]' not in request.files:
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist('files[]')
    
    if not files or files[0].filename == '':
        return jsonify({"error": "No selected files"}), 400

    results = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            try:
                # Process the document
                result = processor.process_document(file_path)
                results.append({
                    "filename": filename,
                    "status": "success",
                    "analysis": result
                })
            except Exception as e:
                results.append({
                    "filename": filename,
                    "status": "error",
                    "error": str(e)
                })
        else:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": "Invalid file type"
            })

    return jsonify({
        "message": "Files processed",
        "results": results
    }), 200

@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File is too large"}), 413

if __name__ == '__main__':
    app.run(debug=True, port=8000)
