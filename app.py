import os
import uuid
import subprocess
import threading
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://converter:converter123@db/file_converter'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)

# Initialize database
db = SQLAlchemy(app)

# Database model
class Conversion(db.Model):
    __tablename__ = 'conversions'
    
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255), nullable=False)
    converted_filename = db.Column(db.String(255), nullable=False)
    conversion_type = db.Column(db.Enum('pdf_to_word', 'word_to_pdf'), nullable=False)
    status = db.Column(db.Enum('pending', 'processing', 'completed', 'failed'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'original_filename': self.original_filename,
            'converted_filename': self.converted_filename,
            'conversion_type': self.conversion_type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message
        }

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def convert_file(conversion_id):
    """Convert file using LibreOffice in a background thread"""
    with app.app_context():
        try:
            conversion = Conversion.query.get(conversion_id)
            if not conversion:
                return
            
            conversion.status = 'processing'
            db.session.commit()
            
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], conversion.original_filename)
            output_path = os.path.join(app.config['CONVERTED_FOLDER'], conversion.converted_filename)
            
            # LibreOffice command for conversion
            if conversion.conversion_type == 'pdf_to_word':
                # Convert PDF to DOCX
                cmd = [
                    'libreoffice', '--headless', '--convert-to', 'docx',
                    '--outdir', app.config['CONVERTED_FOLDER'], input_path
                ]
            else:
                # Convert DOCX to PDF
                cmd = [
                    'libreoffice', '--headless', '--convert-to', 'pdf',
                    '--outdir', app.config['CONVERTED_FOLDER'], input_path
                ]
            
            # Run conversion
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                conversion.status = 'completed'
                conversion.completed_at = datetime.utcnow()
                logger.info(f"Conversion completed successfully: {conversion.original_filename}")
            else:
                conversion.status = 'failed'
                conversion.error_message = f"LibreOffice conversion failed: {result.stderr}"
                logger.error(f"Conversion failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            conversion.status = 'failed'
            conversion.error_message = "Conversion timed out after 5 minutes"
            logger.error("Conversion timed out")
        except Exception as e:
            conversion.status = 'failed'
            conversion.error_message = str(e)
            logger.error(f"Conversion error: {str(e)}")
        finally:
            db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        conversion_type = request.form.get('conversion_type')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if conversion_type not in ['pdf_to_word', 'word_to_pdf']:
            return jsonify({'error': 'Invalid conversion type'}), 400
        
        # Check file extension
        if conversion_type == 'pdf_to_word':
            if not allowed_file(file.filename, {'pdf'}):
                return jsonify({'error': 'Only PDF files are allowed for PDF to Word conversion'}), 400
        else:
            if not allowed_file(file.filename, {'docx', 'doc'}):
                return jsonify({'error': 'Only DOCX/DOC files are allowed for Word to PDF conversion'}), 400
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Save uploaded file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Determine output filename
        if conversion_type == 'pdf_to_word':
            output_filename = f"{uuid.uuid4()}.docx"
        else:
            output_filename = f"{uuid.uuid4()}.pdf"
        
        # Create database record
        conversion = Conversion(
            original_filename=unique_filename,
            converted_filename=output_filename,
            conversion_type=conversion_type
        )
        db.session.add(conversion)
        db.session.commit()
        
        # Start conversion in background thread
        thread = threading.Thread(target=convert_file, args=(conversion.id,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'conversion_id': conversion.id,
            'status': conversion.status
        }), 200
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': 'Upload failed'}), 500

@app.route('/status/<int:conversion_id>')
def get_status(conversion_id):
    try:
        conversion = Conversion.query.get(conversion_id)
        if not conversion:
            return jsonify({'error': 'Conversion not found'}), 404
        
        return jsonify(conversion.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({'error': 'Status check failed'}), 500

@app.route('/download/<int:conversion_id>')
def download_file(conversion_id):
    try:
        conversion = Conversion.query.get(conversion_id)
        if not conversion:
            return jsonify({'error': 'Conversion not found'}), 404
        
        if conversion.status != 'completed':
            return jsonify({'error': 'Conversion not completed'}), 400
        
        file_path = os.path.join(app.config['CONVERTED_FOLDER'], conversion.converted_filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'Converted file not found'}), 404
        
        return send_file(file_path, as_attachment=True, download_name=conversion.converted_filename)
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': 'Download failed'}), 500

@app.route('/conversions')
def list_conversions():
    try:
        conversions = Conversion.query.order_by(Conversion.created_at.desc()).limit(50).all()
        return jsonify([conv.to_dict() for conv in conversions]), 200
        
    except Exception as e:
        logger.error(f"List conversions error: {str(e)}")
        return jsonify({'error': 'Failed to list conversions'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5001, debug=True) 