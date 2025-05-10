"""
Simple Document Processor for Islamic Finance Standards Enhancement System

This script provides a simplified document processing functionality that works
without any database constraints or errors.
"""

import os
import json
import logging
from datetime import datetime
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'islamic_finance_standards_enhancement'

# In-memory storage
STANDARDS = [
    {"id": "FAS4", "name": "FAS 4 - Musharaka", "type": "FAS", "number": "4", "description": "Standard for Musharaka financing"},
    {"id": "FAS10", "name": "FAS 10 - Salam and Parallel Salam", "type": "FAS", "number": "10", "description": "Standard for Salam transactions"},
    {"id": "FAS32", "name": "FAS 32 - Ijarah", "type": "FAS", "number": "32", "description": "Standard for Ijarah transactions"}
]

PROCESSED_DOCUMENTS = []

@app.route('/')
def index():
    return render_template('simple_index.html', standards=STANDARDS)

@app.route('/process-document', methods=['GET', 'POST'])
def process_document():
    if request.method == 'POST':
        standard_id = request.form.get('standard_id')
        
        if not standard_id:
            flash('Please select a standard', 'danger')
            return redirect(url_for('process_document'))
        
        # Check if file was uploaded
        if 'document_file' not in request.files:
            flash('No file uploaded', 'danger')
            return redirect(url_for('process_document'))
        
        file = request.files['document_file']
        
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('process_document'))
        
        if not file.filename.lower().endswith('.pdf'):
            flash('Only PDF files are allowed', 'danger')
            return redirect(url_for('process_document'))
        
        try:
            # Create data directory if it doesn't exist
            os.makedirs('data/uploads', exist_ok=True)
            
            # Save the file
            file_path = os.path.join('data/uploads', f"{standard_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")
            file.save(file_path)
            
            # Process the document (simplified mock processing)
            document_id = str(uuid.uuid4())
            
            # Create a mock result
            result = {
                "id": document_id,
                "standard_id": standard_id,
                "file_path": file_path,
                "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "extracted_data": {
                    "definitions": [
                        {"term": "Musharaka", "definition": "A partnership contract between two or more parties."},
                        {"term": "Diminishing Musharaka", "definition": "A form of partnership where one partner promises to buy the equity share of the other partner gradually."}
                    ],
                    "accounting_treatments": [
                        {"title": "Initial Recognition", "content": "The partner's share in Musharaka capital shall be recognized when payment is made."},
                        {"title": "Profit Distribution", "content": "Profits shall be recognized based on the agreed profit-sharing ratio."}
                    ]
                }
            }
            
            # Save the result
            PROCESSED_DOCUMENTS.append(result)
            
            # Save to a JSON file for persistence
            os.makedirs('data/output', exist_ok=True)
            output_file = os.path.join('data/output', f"processed_{document_id}.json")
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            flash(f'Document processed successfully!', 'success')
            return redirect(url_for('index'))
                
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}", exc_info=True)
            flash(f'Error processing document: {str(e)}', 'danger')
            return redirect(url_for('process_document'))
    
    # Get standards for the dropdown
    return render_template('simple_process_document.html', standards=STANDARDS)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
