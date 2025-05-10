"""
Shared Database for Islamic Finance Standards Enhancement System

This module provides a SQLite-based database that serves as a shared data store
for all components of the system, including the web interface, agents, and knowledge graph.
"""

import os
import json
import sqlite3
import logging
import uuid  # Added uuid import
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import threading

class SharedDatabase:
    """SQLite-based shared database for system integration"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, db_path=None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SharedDatabase, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, db_path=None):
        with self._lock:
            if hasattr(self, '_initialized') and self._initialized:
                return
                
            self._initialized = True
            self.logger = logging.getLogger(__name__)
            
            # Set database path
            if db_path:
                self.db_path = db_path
            else:
                # Default to project directory
                project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                self.db_path = os.path.join(project_dir, 'database', 'standards.db')
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            self.logger.info(f"Initializing shared database at {self.db_path}")
            
            # Initialize database
            self._init_db()
    
    def _get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def _init_db(self):
        """Initialize the database schema"""
        conn = self._get_connection()
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
        
        # Insert sample data if tables are empty
        cursor.execute("SELECT COUNT(*) FROM standards")
        if cursor.fetchone()[0] == 0:
            self._insert_sample_data(cursor)
        
        conn.commit()
        conn.close()
    
    def _insert_sample_data(self, cursor):
        """Insert sample data if tables are empty"""
        self.logger.info("Inserting sample data")
        
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
    
    def get_standards(self):
        """Get all standards"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM standards")
        standards = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return standards
    
    def get_standard_by_id(self, standard_id: str):
        """Get a standard by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM standards WHERE id = ?", (standard_id,))
        standard = cursor.fetchone()
        
        conn.close()
        return dict(standard) if standard else None
    
    def create_standard(self, standard_data: Dict) -> str:
        """Create a new standard"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        standard_id = standard_data.get("id") or f"std-{standard_data['type']}-{standard_data['number']}"
        
        cursor.execute(
            "INSERT INTO standards (id, name, type, number, description, content) VALUES (?, ?, ?, ?, ?, ?)",
            (
                standard_id,
                standard_data["name"],
                standard_data["type"],
                standard_data["number"],
                standard_data.get("description", ""),
                standard_data.get("content", "")
            )
        )
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Created standard {standard_id}")
        return standard_id
    
    def create_definition(self, definition_data: Dict) -> str:
        """Create a new definition
        
        Args:
            definition_data: Definition data
            
        Returns:
            str: ID of the created definition
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if definition already exists
            cursor.execute(
                "SELECT id FROM definitions WHERE standard_id = ? AND term = ?",
                (definition_data["standard_id"], definition_data["term"])
            )
            existing = cursor.fetchone()
            
            if existing:
                # Definition already exists, update it instead
                cursor.execute(
                    "UPDATE definitions SET definition = ? WHERE id = ?",
                    (definition_data["definition"], existing[0])
                )
                conn.commit()
                conn.close()
                self.logger.info(f"Updated definition {existing[0]}")
                return existing[0]
            else:
                # Create new definition
                definition_id = str(uuid.uuid4())
                cursor.execute(
                    "INSERT INTO definitions (id, standard_id, term, definition) VALUES (?, ?, ?, ?)",
                    (
                        definition_id,
                        definition_data["standard_id"],
                        definition_data["term"],
                        definition_data["definition"]
                    )
                )
                conn.commit()
                conn.close()
                self.logger.info(f"Created definition {definition_id}")
                return definition_id
        except Exception as e:
            conn.close()
            self.logger.error(f"Failed to create definition: {e}")
            return None
    
    def get_definitions_for_standard(self, standard_id: str) -> List[Dict]:
        """Get all definitions for a standard"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM definitions WHERE standard_id = ?", (standard_id,))
        definitions = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return definitions
    
    def create_accounting_treatment(self, treatment_data: Dict) -> str:
        """Create a new accounting treatment"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if treatment already exists
            cursor.execute(
                "SELECT id FROM accounting_treatments WHERE standard_id = ? AND title = ?",
                (treatment_data["standard_id"], treatment_data["title"])
            )
            existing = cursor.fetchone()
            
            if existing:
                # Treatment already exists, update it instead
                cursor.execute(
                    "UPDATE accounting_treatments SET content = ? WHERE id = ?",
                    (treatment_data["content"], existing[0])
                )
                conn.commit()
                conn.close()
                self.logger.info(f"Updated accounting treatment {existing[0]}")
                return existing[0]
            else:
                # Create new treatment with a unique ID
                treatment_id = str(uuid.uuid4())
                cursor.execute(
                    "INSERT INTO accounting_treatments (id, standard_id, title, content) VALUES (?, ?, ?, ?)",
                    (
                        treatment_id,
                        treatment_data["standard_id"],
                        treatment_data["title"],
                        treatment_data["content"]
                    )
                )
                conn.commit()
                conn.close()
                self.logger.info(f"Created accounting treatment {treatment_id}")
                return treatment_id
        except Exception as e:
            conn.close()
            self.logger.error(f"Failed to create accounting treatment: {e}")
            return None
    
    def get_accounting_treatments_for_standard(self, standard_id: str) -> List[Dict]:
        """Get all accounting treatments for a standard"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM accounting_treatments WHERE standard_id = ?", (standard_id,))
        treatments = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return treatments
    
    def create_transaction_structure(self, structure_data: Dict) -> str:
        """Create a new transaction structure"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if structure already exists
            cursor.execute(
                "SELECT id FROM transaction_structures WHERE standard_id = ? AND title = ?",
                (structure_data["standard_id"], structure_data["title"])
            )
            existing = cursor.fetchone()
            
            if existing:
                # Structure already exists, update it instead
                cursor.execute(
                    "UPDATE transaction_structures SET description = ? WHERE id = ?",
                    (structure_data["description"], existing[0])
                )
                conn.commit()
                conn.close()
                self.logger.info(f"Updated transaction structure {existing[0]}")
                return existing[0]
            else:
                # Create new structure with a unique ID
                structure_id = str(uuid.uuid4())
                cursor.execute(
                    "INSERT INTO transaction_structures (id, standard_id, title, description) VALUES (?, ?, ?, ?)",
                    (
                        structure_id,
                        structure_data["standard_id"],
                        structure_data["title"],
                        structure_data["description"]
                    )
                )
                conn.commit()
                conn.close()
                self.logger.info(f"Created transaction structure {structure_id}")
                return structure_id
        except Exception as e:
            conn.close()
            self.logger.error(f"Failed to create transaction structure: {e}")
            return None
    
    def get_transaction_structures_for_standard(self, standard_id: str) -> List[Dict]:
        """Get all transaction structures for a standard"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM transaction_structures WHERE standard_id = ?", (standard_id,))
        structures = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return structures
    
    def create_ambiguity(self, ambiguity_data: Dict) -> str:
        """Create a new ambiguity"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Generate a unique ID for the ambiguity
            ambiguity_id = str(uuid.uuid4())
            
            # Insert the ambiguity
            cursor.execute(
                "INSERT INTO ambiguities (id, standard_id, text, severity) VALUES (?, ?, ?, ?)",
                (
                    ambiguity_id,
                    ambiguity_data["standard_id"],
                    ambiguity_data.get("text", ""),
                    ambiguity_data.get("severity", "medium")
                )
            )
            
            conn.commit()
            conn.close()
            self.logger.info(f"Created ambiguity {ambiguity_id}")
            return ambiguity_id
        except Exception as e:
            conn.close()
            self.logger.error(f"Failed to create ambiguity: {e}")
            return None
    
    def get_ambiguities_for_standard(self, standard_id: str) -> List[Dict]:
        """Get all ambiguities for a standard"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id, standard_id, text, severity FROM ambiguities WHERE standard_id = ?",
                (standard_id,)
            )
            
            ambiguities = []
            for row in cursor.fetchall():
                ambiguities.append({
                    "id": row[0],
                    "standard_id": row[1],
                    "text": row[2],
                    "severity": row[3]
                })
            
            conn.close()
            return ambiguities
        except Exception as e:
            self.logger.error(f"Error getting ambiguities: {e}")
            conn.close()
            return []
    
    def create_enhancement_proposal(self, proposal_data: Dict) -> str:
        """Create a new enhancement proposal
        
        Args:
            proposal_data: Enhancement proposal data
            
        Returns:
            str: ID of the created proposal
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        proposal_id = proposal_data.get("id") or f"prop-{proposal_data['standard_id']}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        cursor.execute(
            "INSERT INTO enhancement_proposals (id, standard_id, title, current_text, proposed_text, rationale, status, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                proposal_id,
                proposal_data["standard_id"],
                proposal_data["title"],
                proposal_data.get("current_text", proposal_data.get("original_text", "")),
                proposal_data["proposed_text"],
                proposal_data.get("rationale", ""),
                proposal_data.get("status", "pending"),
                proposal_data.get("created_by", "system")
            )
        )
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Created enhancement proposal {proposal_id}")
        return proposal_id
    
    def get_enhancement_proposals(self, status: Optional[str] = None) -> List[Dict]:
        """Get all enhancement proposals, optionally filtered by status"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute("SELECT * FROM enhancement_proposals WHERE status = ?", (status,))
        else:
            cursor.execute("SELECT * FROM enhancement_proposals")
        
        proposals = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return proposals
    
    def get_enhancement_proposal_by_id(self, proposal_id: str) -> Optional[Dict]:
        """Get an enhancement proposal by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM enhancement_proposals WHERE id = ?", (proposal_id,))
        proposal = cursor.fetchone()
        
        conn.close()
        return dict(proposal) if proposal else None
    
    def update_enhancement_proposal(self, proposal_id: str, update_data: Dict) -> bool:
        """Update an enhancement proposal"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Build SET clause and parameters for UPDATE statement
        set_clause = []
        params = []
        
        for key, value in update_data.items():
            if key in ["title", "current_text", "proposed_text", "rationale", "status"]:
                set_clause.append(f"{key} = ?")
                params.append(value)
        
        if not set_clause:
            conn.close()
            return False
        
        # Add proposal_id to params
        params.append(proposal_id)
        
        # Execute UPDATE statement
        cursor.execute(
            f"UPDATE enhancement_proposals SET {', '.join(set_clause)} WHERE id = ?",
            params
        )
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Updated enhancement proposal {proposal_id}")
        return True
    
    def update_enhancement_proposal_status(self, proposal_id: str, status: str) -> bool:
        """Update the status of an enhancement proposal"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE enhancement_proposals SET status = ? WHERE id = ?",
            (status, proposal_id)
        )
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Updated enhancement proposal {proposal_id} status to {status}")
        return True
    
    def create_comment(self, comment_data: Dict) -> str:
        """Create a new comment"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        comment_id = comment_data.get("id") or str(uuid.uuid4())
        
        cursor.execute(
            "INSERT INTO comments (id, proposal_id, user_id, text) VALUES (?, ?, ?, ?)",
            (
                comment_id,
                comment_data["proposal_id"],
                comment_data.get("user_id"),
                comment_data["text"]
            )
        )
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Created comment {comment_id}")
        return comment_id
    
    def get_comments_for_proposal(self, proposal_id: str) -> List[Dict]:
        """Get all comments for a proposal"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM comments WHERE proposal_id = ?", (proposal_id,))
        comments = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return comments
    
    def record_vote(self, vote_data: Dict) -> str:
        """Record a vote for a proposal"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if user has already voted
        if vote_data.get("user_id"):
            cursor.execute(
                "SELECT id, vote_type FROM votes WHERE proposal_id = ? AND user_id = ?",
                (vote_data["proposal_id"], vote_data["user_id"])
            )
            existing_vote = cursor.fetchone()
            
            if existing_vote:
                # User has already voted, update their vote if it's different
                if existing_vote["vote_type"] != vote_data["vote_type"]:
                    cursor.execute(
                        "UPDATE votes SET vote_type = ? WHERE id = ?",
                        (vote_data["vote_type"], existing_vote["id"])
                    )
                    
                    conn.commit()
                    conn.close()
                    
                    self.logger.info(f"Updated vote {existing_vote['id']}")
                    return existing_vote["id"]
                else:
                    # Vote is the same, no need to update
                    conn.close()
                    return existing_vote["id"]
        
        # Create a new vote
        vote_id = vote_data.get("id") or str(uuid.uuid4())
        
        cursor.execute(
            "INSERT INTO votes (id, proposal_id, user_id, vote_type) VALUES (?, ?, ?, ?)",
            (
                vote_id,
                vote_data["proposal_id"],
                vote_data.get("user_id"),
                vote_data["vote_type"]
            )
        )
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Recorded vote {vote_id}")
        return vote_id
    
    def get_vote_count_for_proposal(self, proposal_id: str) -> Dict[str, int]:
        """Get the vote count for a proposal"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT vote_type, COUNT(*) FROM votes WHERE proposal_id = ? GROUP BY vote_type", (proposal_id,))
        vote_counts = {row["vote_type"]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        # Ensure up and down counts are present
        return {
            "up": vote_counts.get("up", 0),
            "down": vote_counts.get("down", 0)
        }
    
    def create_validation(self, validation_data: Dict) -> str:
        """Create a validation for a proposal"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        validation_id = validation_data.get("id") or str(uuid.uuid4())
        
        cursor.execute(
            "INSERT INTO validations (id, enhancement_id, is_valid, feedback, shariah_compliance) VALUES (?, ?, ?, ?, ?)",
            (
                validation_id,
                validation_data["enhancement_id"],
                validation_data["is_valid"],
                validation_data.get("feedback", ""),
                validation_data.get("shariah_compliance", "")
            )
        )
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Created validation {validation_id}")
        return validation_id
    
    def get_validation_for_proposal(self, proposal_id: str) -> Optional[Dict]:
        """Get the validation for a proposal"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM validations WHERE enhancement_id = ?", (proposal_id,))
        validation = cursor.fetchone()
        
        conn.close()
        return dict(validation) if validation else None
    
    def record_event(self, event_data: Dict) -> str:
        """Record an event"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        event_id = event_data.get("id") or str(uuid.uuid4())
        
        cursor.execute(
            "INSERT INTO events (id, topic, type, payload) VALUES (?, ?, ?, ?)",
            (
                event_id,
                event_data["topic"],
                event_data["type"],
                json.dumps(event_data["payload"])
            )
        )
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Recorded event {event_id}")
        return event_id
    
    def get_events(self, topic: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get recent events"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if topic:
            cursor.execute("SELECT * FROM events WHERE topic = ? ORDER BY timestamp DESC LIMIT ?", (topic, limit))
        else:
            cursor.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,))
        
        events = []
        for row in cursor.fetchall():
            event = dict(row)
            event["payload"] = json.loads(event["payload"])
            events.append(event)
        
        conn.close()
        return events
    
    def record_audit_log(self, log_data: Dict) -> str:
        """Record an audit log"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        log_id = log_data.get("id") or str(uuid.uuid4())
        
        cursor.execute(
            "INSERT INTO audit_logs (id, event_type, data, user_id) VALUES (?, ?, ?, ?)",
            (
                log_id,
                log_data["event_type"],
                json.dumps(log_data["data"]),
                log_data.get("user_id")
            )
        )
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Recorded audit log {log_id}")
        return log_id
    
    def get_audit_logs(self, limit: int = 10) -> List[Dict]:
        """Get recent audit logs"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
        
        logs = []
        for row in cursor.fetchall():
            log = dict(row)
            log["data"] = json.loads(log["data"])
            logs.append(log)
        
        conn.close()
        return logs
