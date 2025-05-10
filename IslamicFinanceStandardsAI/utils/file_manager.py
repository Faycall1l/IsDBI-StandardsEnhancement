"""
File Manager for Islamic Finance Standards Enhancement System

This module provides a file system manager that handles document storage and sharing
between all components of the system, including the web interface, agents, and knowledge graph.
"""

import os
import json
import shutil
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, BinaryIO
import threading
import uuid

class FileManager:
    """File system manager for system integration"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, base_dir=None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(FileManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, base_dir=None):
        with self._lock:
            if self._initialized:
                return
                
            self._initialized = True
            self.logger = logging.getLogger(__name__)
            
            # Set base directory
            if base_dir:
                self.base_dir = base_dir
            else:
                # Default to project directory
                project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                self.base_dir = os.path.join(project_dir, 'data')
            
            # Create directory structure
            self._create_directory_structure()
            
            self.logger.info(f"Initialized file manager at {self.base_dir}")
    
    def _create_directory_structure(self):
        """Create the directory structure"""
        # Create main directories
        os.makedirs(self.base_dir, exist_ok=True)
        
        # Create subdirectories
        directories = [
            'standards',           # For standard documents
            'enhancements',        # For enhancement proposals
            'validations',         # For validation results
            'uploads',             # For user uploads
            'exports',             # For exports
            'temp',                # For temporary files
            'logs',                # For log files
            'events',              # For event logs
            'audit',               # For audit logs
            'backups'              # For backups
        ]
        
        for directory in directories:
            os.makedirs(os.path.join(self.base_dir, directory), exist_ok=True)
        
        self.logger.info("Directory structure created")
    
    def save_standard_document(self, standard_id: str, file_content: Union[str, bytes, BinaryIO], filename: str = None) -> str:
        """
        Save a standard document to the file system
        
        Args:
            standard_id: ID of the standard
            file_content: Content of the file (string, bytes, or file-like object)
            filename: Optional filename (if not provided, will use standard_id)
            
        Returns:
            Path to the saved file
        """
        # Create standard directory if it doesn't exist
        standard_dir = os.path.join(self.base_dir, 'standards', standard_id)
        os.makedirs(standard_dir, exist_ok=True)
        
        # Determine filename
        if not filename:
            filename = f"{standard_id}.pdf"
        
        # Determine file path
        file_path = os.path.join(standard_dir, filename)
        
        # Save file
        if isinstance(file_content, str):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
        elif isinstance(file_content, bytes):
            with open(file_path, 'wb') as f:
                f.write(file_content)
        else:  # File-like object
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(file_content, f)
        
        self.logger.info(f"Saved standard document {filename} for {standard_id}")
        return file_path
    
    def get_standard_document_path(self, standard_id: str, filename: str = None) -> Optional[str]:
        """
        Get the path to a standard document
        
        Args:
            standard_id: ID of the standard
            filename: Optional filename (if not provided, will use standard_id)
            
        Returns:
            Path to the file, or None if not found
        """
        # Determine standard directory
        standard_dir = os.path.join(self.base_dir, 'standards', standard_id)
        
        # Determine filename
        if not filename:
            filename = f"{standard_id}.pdf"
        
        # Determine file path
        file_path = os.path.join(standard_dir, filename)
        
        # Check if file exists
        if os.path.isfile(file_path):
            return file_path
        
        return None
    
    def save_standard_extraction(self, standard_id: str, extraction_data: Dict) -> str:
        """
        Save extracted data for a standard
        
        Args:
            standard_id: ID of the standard
            extraction_data: Extracted data
            
        Returns:
            Path to the saved file
        """
        # Create standard directory if it doesn't exist
        standard_dir = os.path.join(self.base_dir, 'standards', standard_id)
        os.makedirs(standard_dir, exist_ok=True)
        
        # Determine file path
        file_path = os.path.join(standard_dir, 'extraction.json')
        
        # Save file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(extraction_data, f, indent=2)
        
        self.logger.info(f"Saved extraction data for {standard_id}")
        return file_path
    
    def get_standard_extraction(self, standard_id: str) -> Optional[Dict]:
        """
        Get extracted data for a standard
        
        Args:
            standard_id: ID of the standard
            
        Returns:
            Extracted data, or None if not found
        """
        # Determine file path
        file_path = os.path.join(self.base_dir, 'standards', standard_id, 'extraction.json')
        
        # Check if file exists
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def save_enhancement_proposal(self, proposal_id: str, proposal_data: Dict) -> str:
        """
        Save an enhancement proposal
        
        Args:
            proposal_id: ID of the proposal
            proposal_data: Proposal data
            
        Returns:
            Path to the saved file
        """
        # Create enhancements directory if it doesn't exist
        os.makedirs(os.path.join(self.base_dir, 'enhancements'), exist_ok=True)
        
        # Determine file path
        file_path = os.path.join(self.base_dir, 'enhancements', f"{proposal_id}.json")
        
        # Save file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(proposal_data, f, indent=2)
        
        self.logger.info(f"Saved enhancement proposal {proposal_id}")
        return file_path
    
    def get_enhancement_proposal(self, proposal_id: str) -> Optional[Dict]:
        """
        Get an enhancement proposal
        
        Args:
            proposal_id: ID of the proposal
            
        Returns:
            Proposal data, or None if not found
        """
        # Determine file path
        file_path = os.path.join(self.base_dir, 'enhancements', f"{proposal_id}.json")
        
        # Check if file exists
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def get_all_enhancement_proposals(self) -> List[Dict]:
        """
        Get all enhancement proposals
        
        Returns:
            List of proposal data
        """
        # Determine directory
        directory = os.path.join(self.base_dir, 'enhancements')
        
        # Check if directory exists
        if not os.path.isdir(directory):
            return []
        
        # Get all JSON files
        proposals = []
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    proposals.append(json.load(f))
        
        return proposals
    
    def save_validation_result(self, validation_id: str, validation_data: Dict) -> str:
        """
        Save a validation result
        
        Args:
            validation_id: ID of the validation
            validation_data: Validation data
            
        Returns:
            Path to the saved file
        """
        # Create validations directory if it doesn't exist
        os.makedirs(os.path.join(self.base_dir, 'validations'), exist_ok=True)
        
        # Determine file path
        file_path = os.path.join(self.base_dir, 'validations', f"{validation_id}.json")
        
        # Save file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(validation_data, f, indent=2)
        
        self.logger.info(f"Saved validation result {validation_id}")
        return file_path
    
    def get_validation_result(self, validation_id: str) -> Optional[Dict]:
        """
        Get a validation result
        
        Args:
            validation_id: ID of the validation
            
        Returns:
            Validation data, or None if not found
        """
        # Determine file path
        file_path = os.path.join(self.base_dir, 'validations', f"{validation_id}.json")
        
        # Check if file exists
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def save_event_log(self, event_id: str, event_data: Dict) -> str:
        """
        Save an event log
        
        Args:
            event_id: ID of the event
            event_data: Event data
            
        Returns:
            Path to the saved file
        """
        # Create events directory if it doesn't exist
        os.makedirs(os.path.join(self.base_dir, 'events'), exist_ok=True)
        
        # Determine file path
        file_path = os.path.join(self.base_dir, 'events', f"{event_id}.json")
        
        # Save file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(event_data, f, indent=2)
        
        self.logger.info(f"Saved event log {event_id}")
        return file_path
    
    def get_event_log(self, event_id: str) -> Optional[Dict]:
        """
        Get an event log
        
        Args:
            event_id: ID of the event
            
        Returns:
            Event data, or None if not found
        """
        # Determine file path
        file_path = os.path.join(self.base_dir, 'events', f"{event_id}.json")
        
        # Check if file exists
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def get_recent_event_logs(self, limit: int = 10) -> List[Dict]:
        """
        Get recent event logs
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of event data
        """
        # Determine directory
        directory = os.path.join(self.base_dir, 'events')
        
        # Check if directory exists
        if not os.path.isdir(directory):
            return []
        
        # Get all JSON files
        events = []
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    events.append(json.load(f))
        
        # Sort by timestamp (newest first)
        events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Limit results
        return events[:limit]
    
    def save_audit_log(self, audit_id: str, audit_data: Dict) -> str:
        """
        Save an audit log
        
        Args:
            audit_id: ID of the audit log
            audit_data: Audit data
            
        Returns:
            Path to the saved file
        """
        # Create audit directory if it doesn't exist
        os.makedirs(os.path.join(self.base_dir, 'audit'), exist_ok=True)
        
        # Determine file path
        file_path = os.path.join(self.base_dir, 'audit', f"{audit_id}.json")
        
        # Save file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(audit_data, f, indent=2)
        
        self.logger.info(f"Saved audit log {audit_id}")
        return file_path
    
    def get_audit_log(self, audit_id: str) -> Optional[Dict]:
        """
        Get an audit log
        
        Args:
            audit_id: ID of the audit log
            
        Returns:
            Audit data, or None if not found
        """
        # Determine file path
        file_path = os.path.join(self.base_dir, 'audit', f"{audit_id}.json")
        
        # Check if file exists
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def get_recent_audit_logs(self, limit: int = 10) -> List[Dict]:
        """
        Get recent audit logs
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of audit data
        """
        # Determine directory
        directory = os.path.join(self.base_dir, 'audit')
        
        # Check if directory exists
        if not os.path.isdir(directory):
            return []
        
        # Get all JSON files
        audits = []
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    audits.append(json.load(f))
        
        # Sort by timestamp (newest first)
        audits.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Limit results
        return audits[:limit]
    
    def save_upload(self, file_content: Union[str, bytes, BinaryIO], filename: str) -> str:
        """
        Save an uploaded file
        
        Args:
            file_content: Content of the file (string, bytes, or file-like object)
            filename: Filename
            
        Returns:
            Path to the saved file
        """
        # Create uploads directory if it doesn't exist
        os.makedirs(os.path.join(self.base_dir, 'uploads'), exist_ok=True)
        
        # Generate unique filename to avoid collisions
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Determine file path
        file_path = os.path.join(self.base_dir, 'uploads', unique_filename)
        
        # Save file
        if isinstance(file_content, str):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
        elif isinstance(file_content, bytes):
            with open(file_path, 'wb') as f:
                f.write(file_content)
        else:  # File-like object
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(file_content, f)
        
        self.logger.info(f"Saved uploaded file {filename}")
        return file_path
    
    def get_upload(self, filename: str) -> Optional[str]:
        """
        Get an uploaded file
        
        Args:
            filename: Filename
            
        Returns:
            Path to the file, or None if not found
        """
        # Determine directory
        directory = os.path.join(self.base_dir, 'uploads')
        
        # Check if directory exists
        if not os.path.isdir(directory):
            return None
        
        # Find file with matching name (ignoring UUID prefix)
        for file in os.listdir(directory):
            if file.endswith(filename):
                return os.path.join(directory, file)
        
        return None
    
    def create_backup(self) -> str:
        """
        Create a backup of all data
        
        Returns:
            Path to the backup directory
        """
        # Create backups directory if it doesn't exist
        os.makedirs(os.path.join(self.base_dir, 'backups'), exist_ok=True)
        
        # Generate backup directory name
        backup_dir = os.path.join(self.base_dir, 'backups', f"backup_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Copy all data to backup directory
        for directory in ['standards', 'enhancements', 'validations', 'events', 'audit']:
            src_dir = os.path.join(self.base_dir, directory)
            dst_dir = os.path.join(backup_dir, directory)
            
            if os.path.isdir(src_dir):
                shutil.copytree(src_dir, dst_dir)
        
        self.logger.info(f"Created backup at {backup_dir}")
        return backup_dir
