"""
Simple Demo for Islamic Finance Standards Enhancement System

This script provides a simple Flask web application to demonstrate the document processing
functionality without relying on any database operations or external dependencies.
"""

import os
import logging
from datetime import datetime
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

# Initialize Flask app
app = Flask(__name__, 
            static_folder='IslamicFinanceStandardsAI/frontend/static',
            template_folder='IslamicFinanceStandardsAI/frontend/templates')
app.secret_key = 'islamic_finance_standards_enhancement'

# Mock data for standards
STANDARDS = [
    {
        "id": "FAS4",
        "name": "FAS 4 - Musharaka",
        "type": "FAS",
        "number": "4",
        "description": "Standard for Musharaka financing"
    },
    {
        "id": "FAS10",
        "name": "FAS 10 - Salam and Parallel Salam",
        "type": "FAS",
        "number": "10",
        "description": "Standard for Salam transactions"
    },
    {
        "id": "FAS32",
        "name": "FAS 32 - Ijarah",
        "type": "FAS",
        "number": "32",
        "description": "Standard for Ijarah transactions"
    }
]

# Mock data for document processing results
def get_mock_result(standard_id, document_path):
    """Generate mock document processing results"""
    return {
        "success": True,
        "message": "Document processed successfully",
        "standard_id": standard_id,
        "document_path": document_path,
        "extracted_data_summary": {
            "definitions": 5,
            "accounting_treatments": 3,
            "transaction_structures": 2,
            "ambiguities": 4
        },
        "extracted_data": {
            "definitions": [
                {"term": "Musharaka", "definition": "A partnership between two or more parties where each partner contributes capital and participates in the work."},
                {"term": "Diminishing Musharaka", "definition": "A form of partnership where one partner's share decreases over time as the other partner gradually purchases it."},
                {"term": "Profit", "definition": "The increase over capital that is distributed according to the agreement."},
                {"term": "Loss", "definition": "The decrease in capital that is distributed according to capital contribution ratios."},
                {"term": "Capital", "definition": "The assets contributed by partners to the Musharaka."}
            ],
            "accounting_treatments": [
                {"title": "Initial Recognition", "text": "The partner's share in Musharaka capital should be recognized when payment is made or when capital is placed at the disposal of the Musharaka venture."},
                {"title": "Subsequent Measurement", "text": "The partner's share is measured at the end of the financial period at historical cost after accounting for any profit or loss."},
                {"title": "Profit Distribution", "text": "Profits are distributed according to the agreed ratio, while losses are distributed according to the capital contribution ratio."}
            ],
            "transaction_structures": [
                {"title": "Diminishing Musharaka", "description": "A form of partnership where one partner gradually purchases the other partner's share over time."},
                {"title": "Constant Musharaka", "description": "A partnership where the partners' shares remain constant throughout the duration of the venture."}
            ],
            "ambiguities": [
                {"text": "The standard does not clearly specify the treatment of losses in case of negligence", "severity": "high"},
                {"text": "There is ambiguity in the profit distribution mechanism when one partner contributes both capital and labor", "severity": "medium"},
                {"text": "The standard lacks clarity on the valuation of non-monetary assets contributed as capital", "severity": "medium"},
                {"text": "The termination procedures in case of partner default are not well-defined", "severity": "low"}
            ]
        }
    }

# Routes
@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@app.route('/process-document', methods=['GET', 'POST'])
def process_document():
    """Process a document"""
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'document_file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['document_file']
        
        # Check if file is empty
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        # Get standard ID
        standard_id = request.form.get('standard_id', 'FAS4')
        
        # Save the file temporarily
        temp_path = os.path.join('temp', file.filename)
        os.makedirs('temp', exist_ok=True)
        file.save(temp_path)
        
        # Get mock result
        result = get_mock_result(standard_id, temp_path)
        
        # Return the result
        return render_template('process_document.html', 
                              standards=STANDARDS, 
                              result=result, 
                              show_result=True)
    
    return render_template('process_document.html', standards=STANDARDS)

@app.route('/system-events')
def system_events():
    """View system events"""
    # Mock events
    events = [
        {
            "id": "event-1",
            "type": "DOCUMENT_PROCESSING_STARTED",
            "topic": "document",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "payload": {
                "standard_id": "FAS4",
                "document_path": "/path/to/document.pdf"
            }
        },
        {
            "id": "event-2",
            "type": "DOCUMENT_PROCESSING_COMPLETED",
            "topic": "document",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "payload": {
                "standard_id": "FAS4",
                "document_path": "/path/to/document.pdf",
                "extracted_data_summary": {
                    "definitions": 5,
                    "accounting_treatments": 3,
                    "transaction_structures": 2,
                    "ambiguities": 4
                }
            }
        }
    ]
    return render_template('system_events.html', events=events)

@app.route('/standards')
def standards():
    """View standards"""
    return render_template('standards.html', standards=STANDARDS)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
