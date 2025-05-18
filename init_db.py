"""
Database Initialization Script for Islamic Finance Standards Enhancement System

This script initializes the database with the correct schema and sample data.
"""

import os
import sqlite3
import uuid
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'IslamicFinanceStandardsAI', 'database', 'standards.db')

def init_db():
    """Initialize the database with the correct schema"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Remove existing database if it exists
    if os.path.exists(DB_PATH):
        logger.info(f"Removing existing database at {DB_PATH}")
        os.remove(DB_PATH)
    
    logger.info(f"Initializing database at {DB_PATH}")
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create standards table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS standards (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        number TEXT NOT NULL,
        description TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create definitions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS definitions (
        id TEXT PRIMARY KEY,
        standard_id TEXT NOT NULL,
        term TEXT NOT NULL,
        definition TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (standard_id) REFERENCES standards (id)
    )
    ''')
    
    # Create accounting_treatments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounting_treatments (
        id TEXT PRIMARY KEY,
        standard_id TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (standard_id) REFERENCES standards (id)
    )
    ''')
    
    # Create transaction_structures table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transaction_structures (
        id TEXT PRIMARY KEY,
        standard_id TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (standard_id) REFERENCES standards (id)
    )
    ''')
    
    # Create ambiguities table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ambiguities (
        id TEXT PRIMARY KEY,
        standard_id TEXT NOT NULL,
        text TEXT NOT NULL,
        severity TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (standard_id) REFERENCES standards (id)
    )
    ''')
    
    # Create enhancement_proposals table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS enhancement_proposals (
        id TEXT PRIMARY KEY,
        standard_id TEXT NOT NULL,
        title TEXT NOT NULL,
        current_text TEXT,
        proposed_text TEXT NOT NULL,
        rationale TEXT,
        status TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by TEXT,
        FOREIGN KEY (standard_id) REFERENCES standards (id)
    )
    ''')
    
    # Create comments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id TEXT PRIMARY KEY,
        proposal_id TEXT NOT NULL,
        user_id TEXT,
        text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (proposal_id) REFERENCES enhancement_proposals (id)
    )
    ''')
    
    # Create votes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS votes (
        id TEXT PRIMARY KEY,
        proposal_id TEXT NOT NULL,
        user_id TEXT,
        vote_type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (proposal_id) REFERENCES enhancement_proposals (id)
    )
    ''')
    
    # Create validations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS validations (
        id TEXT PRIMARY KEY,
        enhancement_id TEXT NOT NULL,
        is_valid BOOLEAN NOT NULL,
        feedback TEXT,
        shariah_compliance TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (enhancement_id) REFERENCES enhancement_proposals (id)
    )
    ''')
    
    # Create events table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY,
        topic TEXT NOT NULL,
        type TEXT NOT NULL,
        payload TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create audit_logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_logs (
        id TEXT PRIMARY KEY,
        event_type TEXT NOT NULL,
        data TEXT NOT NULL,
        user_id TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Insert sample data
    insert_sample_data(cursor)
    
    # Commit changes
    conn.commit()
    conn.close()
    
    logger.info("Database initialization complete")

def insert_sample_data(cursor):
    """Insert sample data into the database"""
    logger.info("Inserting sample data")
    
    # Insert sample standards
    standards = [
        {
            "id": "FAS4",
            "name": "FAS 4 - Musharaka",
            "type": "FAS",
            "number": "4",
            "description": "Standard for Musharaka financing",
            "content": "Musharaka is a partnership between two or more parties..."
        },
        {
            "id": "FAS10",
            "name": "FAS 10 - Salam and Parallel Salam",
            "type": "FAS",
            "number": "10",
            "description": "Standard for Salam transactions",
            "content": "Salam is a sale whereby the seller undertakes to supply..."
        },
        {
            "id": "FAS32",
            "name": "FAS 32 - Ijarah",
            "type": "FAS",
            "number": "32",
            "description": "Standard for Ijarah transactions",
            "content": "Ijarah is a lease contract whereby the lessor..."
        }
    ]
    
    for standard in standards:
        cursor.execute(
            "INSERT INTO standards (id, name, type, number, description, content) VALUES (?, ?, ?, ?, ?, ?)",
            (
                standard["id"],
                standard["name"],
                standard["type"],
                standard["number"],
                standard["description"],
                standard["content"]
            )
        )
    
    # Insert sample definitions
    definitions = [
        {
            "standard_id": "FAS4",
            "term": "Musharaka",
            "definition": "A partnership between two or more parties where each party contributes capital and participates in the profits and losses."
        },
        {
            "standard_id": "FAS4",
            "term": "Diminishing Musharaka",
            "definition": "A form of partnership where one partner promises to buy the equity share of the other partner gradually."
        },
        {
            "standard_id": "FAS10",
            "term": "Salam",
            "definition": "A sale whereby the seller undertakes to supply specific goods to the buyer at a future date in exchange for an advanced price paid in full."
        },
        {
            "standard_id": "FAS32",
            "term": "Ijarah",
            "definition": "A lease contract whereby the lessor transfers the usufruct of an asset to the lessee for an agreed period against an agreed consideration."
        }
    ]
    
    for definition in definitions:
        cursor.execute(
            "INSERT INTO definitions (id, standard_id, term, definition) VALUES (?, ?, ?, ?)",
            (
                str(uuid.uuid4()),
                definition["standard_id"],
                definition["term"],
                definition["definition"]
            )
        )
    
    # Insert sample accounting treatments
    treatments = [
        {
            "standard_id": "FAS4",
            "title": "Initial Recognition",
            "content": "The partner's share in Musharaka capital shall be recognized when payment is made."
        },
        {
            "standard_id": "FAS4",
            "title": "Profit Distribution",
            "content": "Profits shall be recognized based on the agreed profit-sharing ratio."
        },
        {
            "standard_id": "FAS10",
            "title": "Salam Capital",
            "content": "Salam capital shall be recognized when payment is made to the seller."
        },
        {
            "standard_id": "FAS32",
            "title": "Ijarah Accounting",
            "content": "Ijarah payments shall be recognized as expenses in the period in which they are incurred."
        }
    ]
    
    for treatment in treatments:
        cursor.execute(
            "INSERT INTO accounting_treatments (id, standard_id, title, content) VALUES (?, ?, ?, ?)",
            (
                str(uuid.uuid4()),
                treatment["standard_id"],
                treatment["title"],
                treatment["content"]
            )
        )
    
    # Insert sample enhancement proposal
    proposal_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO enhancement_proposals (id, standard_id, title, current_text, proposed_text, rationale, status, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            proposal_id,
            "FAS4",
            "Clarification of Profit Distribution in Musharaka",
            "Profits shall be recognized based on the agreed profit-sharing ratio.",
            "Profits shall be recognized based on the agreed profit-sharing ratio. The profit-sharing ratio must be clearly specified at the time of contract and cannot be based on a fixed amount.",
            "This enhancement clarifies that profit-sharing in Musharaka cannot be predetermined as a fixed amount, which would be similar to interest and thus non-compliant with Shariah principles.",
            "pending",
            "system"
        )
    )
    
    # Insert sample validation
    cursor.execute(
        "INSERT INTO validations (id, enhancement_id, is_valid, feedback, shariah_compliance) VALUES (?, ?, ?, ?, ?)",
        (
            str(uuid.uuid4()),
            proposal_id,
            True,
            "The proposed enhancement correctly clarifies the profit distribution mechanism in Musharaka.",
            "The enhancement is compliant with Shariah principles as it emphasizes the prohibition of fixed returns."
        )
    )
    
    logger.info("Sample data insertion complete")

if __name__ == "__main__":
    init_db()
