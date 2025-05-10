#!/usr/bin/env python3
"""
Audit Logger

This module provides an immutable audit logging system that simulates Hyperledger Fabric
for recording important events in the Islamic Finance Standards AI system.
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class AuditLogger:
    """Simulates the Hyperledger Fabric immutable audit log"""
    
    def __init__(self, log_dir: str = None):
        """Initialize the audit logger"""
        self.logger = logging.getLogger(__name__)
        self.log_dir = log_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "audit_logs")
        
        # Create log directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Initialize log file
        self.log_file = os.path.join(self.log_dir, f"audit_log_{datetime.now().strftime('%Y%m%d')}.json")
        
        # Initialize log entries
        self.log_entries = []
        
        # Load existing log entries if file exists
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r") as f:
                    self.log_entries = json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading audit log: {str(e)}")
    
    def log_event(self, event_type: str, user_id: str = None, data: Dict[str, Any] = None) -> str:
        """Log an event to the audit log
        
        Args:
            event_type: Type of event
            user_id: ID of the user who triggered the event
            data: Additional data about the event
            
        Returns:
            str: ID of the log entry
        """
        event_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "id": event_id,
            "event_type": event_type,
            "user_id": user_id,
            "timestamp": timestamp,
            "details": data or {}
        }
        
        # Add to log entries
        self.log_entries.append(log_entry)
        
        # Write to log file
        try:
            with open(self.log_file, "w") as f:
                json.dump(self.log_entries, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error writing to audit log: {str(e)}")
        
        # Return the log entry
        logger.info(f"Audit log entry created: {event_type}")
        return entry
    
    def get_events(self, event_type: Optional[str] = None) -> List[Dict]:
        """Get all events, optionally filtered by event type"""
        if event_type:
            return [entry for entry in self.log_entries if entry["event_type"] == event_type]
        return self.log_entries
    
    def get_event_by_id(self, event_id: str) -> Optional[Dict]:
        """Get an event by its ID"""
        for entry in self.log_entries:
            if entry["id"] == event_id:
                return entry
        return None
        
    def get_logs(self, limit: int = 10) -> List[Dict]:
        """Get recent audit logs
        
        Args:
            limit (int): Maximum number of logs to return
            
        Returns:
            List[Dict]: List of audit log entries
        """
        return sorted(self.log_entries, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]
