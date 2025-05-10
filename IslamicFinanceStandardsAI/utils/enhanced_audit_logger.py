"""
Enhanced Audit Logging System

This module provides a production-ready audit logging system that simulates Hyperledger Fabric
for immutable event recording in the Islamic Finance Standards Enhancement system.
It ensures comprehensive event capture, secure storage, and tamper-evident logging.
"""

import os
import json
import time
import uuid
import hashlib
import logging
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Import configuration
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.production import AUDIT_CONFIG

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedAuditLogger:
    """
    Enhanced audit logger that simulates Hyperledger Fabric's immutable ledger
    for comprehensive event tracking and secure audit logging.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EnhancedAuditLogger, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance
    
    def _initialize(self):
        """Initialize the audit logger"""
        self.events = []
        self.event_hashes = []
        self.previous_block_hash = None
        
        # Create audit log directory if it doesn't exist
        self.log_dir = AUDIT_CONFIG.get("storage_path", "audit_logs/")
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Initialize encryption if enabled
        self.encryption_enabled = AUDIT_CONFIG.get("encryption_enabled", False)
        if self.encryption_enabled:
            encryption_key = AUDIT_CONFIG.get("encryption_key")
            if encryption_key:
                # Generate a key from the encryption key
                salt = b'islamic_finance_standards_salt'
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000
                )
                key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
                self.cipher = Fernet(key)
            else:
                logger.warning("Encryption enabled but no key provided. Disabling encryption.")
                self.encryption_enabled = False
        
        # Load existing events if any
        self._load_existing_events()
        
        # Start background thread for periodic flushing
        self.flush_interval = 300  # 5 minutes
        self.flush_thread = threading.Thread(target=self._periodic_flush)
        self.flush_thread.daemon = True
        self.flush_thread.start()
    
    def _load_existing_events(self):
        """Load existing events from the audit log files"""
        try:
            # Find all audit log files
            audit_files = [f for f in os.listdir(self.log_dir) if f.startswith("audit_log_") and f.endswith(".json")]
            
            if not audit_files:
                logger.info("No existing audit log files found")
                return
            
            # Sort files by timestamp
            audit_files.sort()
            latest_file = os.path.join(self.log_dir, audit_files[-1])
            
            logger.info(f"Loading events from latest audit log file: {latest_file}")
            
            with open(latest_file, 'r') as f:
                content = f.read()
                
                # Decrypt if necessary
                if self.encryption_enabled and content.strip():
                    try:
                        content = self.cipher.decrypt(content.encode()).decode()
                    except Exception as e:
                        logger.error(f"Error decrypting audit log: {str(e)}")
                        return
                
                if content.strip():
                    loaded_events = json.loads(content)
                    
                    # Verify the chain of hashes
                    for i, event in enumerate(loaded_events):
                        event_hash = self._calculate_event_hash(event)
                        
                        # Skip hash verification for the first event
                        if i > 0:
                            prev_hash = event.get("previous_hash")
                            if prev_hash != self.event_hashes[-1]:
                                logger.warning(f"Hash chain broken at event {i}. Audit log may be compromised.")
                                break
                        
                        self.events.append(event)
                        self.event_hashes.append(event_hash)
                    
                    # Set the previous block hash for the next event
                    if self.event_hashes:
                        self.previous_block_hash = self.event_hashes[-1]
                        
                    logger.info(f"Loaded {len(self.events)} events from audit log")
        
        except Exception as e:
            logger.error(f"Error loading existing audit events: {str(e)}")
    
    def _periodic_flush(self):
        """Periodically flush events to disk"""
        while True:
            time.sleep(self.flush_interval)
            if self.events:
                self.flush()
    
    def _calculate_event_hash(self, event: Dict[str, Any]) -> str:
        """Calculate a hash for an event"""
        # Create a deterministic string representation of the event
        event_str = json.dumps(event, sort_keys=True)
        return hashlib.sha256(event_str.encode()).hexdigest()
    
    def log_event(self, event_type: str, data: Dict[str, Any], actor: str = "system") -> str:
        """
        Log an event to the audit log
        
        Args:
            event_type: Type of event (e.g., DOCUMENT_PROCESSED, ENHANCEMENT_PROPOSED)
            data: Event data
            actor: Entity that triggered the event
            
        Returns:
            Event ID
        """
        # Create event object
        event_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        event = {
            "id": event_id,
            "timestamp": timestamp,
            "event_type": event_type,
            "actor": actor,
            "data": data,
            "previous_hash": self.previous_block_hash
        }
        
        # Calculate hash for this event
        event_hash = self._calculate_event_hash(event)
        
        # Update event with its hash
        event["hash"] = event_hash
        
        # Add to events list
        with self._lock:
            self.events.append(event)
            self.event_hashes.append(event_hash)
            self.previous_block_hash = event_hash
        
        # Log event summary
        logger.info(f"Audit event logged: {event_type} by {actor} (ID: {event_id})")
        
        # Flush to disk if we have accumulated enough events
        if len(self.events) >= 100:
            self.flush()
        
        return event_id
    
    def flush(self) -> bool:
        """
        Flush events to disk
        
        Returns:
            True if successful, False otherwise
        """
        if not self.events:
            return True
        
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audit_log_{timestamp}.json"
            filepath = os.path.join(self.log_dir, filename)
            
            # Serialize events to JSON
            events_json = json.dumps(self.events, indent=2)
            
            # Encrypt if enabled
            if self.encryption_enabled:
                encrypted_data = self.cipher.encrypt(events_json.encode())
                with open(filepath, 'wb') as f:
                    f.write(encrypted_data)
            else:
                with open(filepath, 'w') as f:
                    f.write(events_json)
            
            logger.info(f"Flushed {len(self.events)} audit events to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error flushing audit events: {str(e)}")
            return False
    
    def get_events(self, 
                  event_type: Optional[str] = None, 
                  start_time: Optional[str] = None,
                  end_time: Optional[str] = None,
                  actor: Optional[str] = None,
                  limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get events from the audit log with optional filtering
        
        Args:
            event_type: Optional event type to filter by
            start_time: Optional start time (ISO format) to filter by
            end_time: Optional end time (ISO format) to filter by
            actor: Optional actor to filter by
            limit: Maximum number of events to return
            
        Returns:
            List of matching events
        """
        filtered_events = []
        
        for event in reversed(self.events):  # Most recent first
            if len(filtered_events) >= limit:
                break
                
            # Apply filters
            if event_type and event["event_type"] != event_type:
                continue
                
            if start_time and event["timestamp"] < start_time:
                continue
                
            if end_time and event["timestamp"] > end_time:
                continue
                
            if actor and event["actor"] != actor:
                continue
                
            filtered_events.append(event)
        
        return filtered_events
    
    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an event by its ID
        
        Args:
            event_id: ID of the event to retrieve
            
        Returns:
            Event dictionary or None if not found
        """
        for event in self.events:
            if event["id"] == event_id:
                return event
        return None
    
    def verify_integrity(self) -> Dict[str, Any]:
        """
        Verify the integrity of the audit log
        
        Returns:
            Dictionary with verification results
        """
        if not self.events:
            return {
                "verified": True,
                "message": "No events to verify",
                "events_checked": 0
            }
        
        broken_chain = False
        first_broken_index = -1
        
        # Recalculate and verify all hashes
        for i in range(1, len(self.events)):
            event = self.events[i]
            prev_event = self.events[i-1]
            
            # Check if previous hash matches
            if event["previous_hash"] != prev_event["hash"]:
                broken_chain = True
                first_broken_index = i
                break
            
            # Recalculate hash and check
            calculated_hash = self._calculate_event_hash(event)
            if calculated_hash != event["hash"]:
                broken_chain = True
                first_broken_index = i
                break
        
        if broken_chain:
            return {
                "verified": False,
                "message": f"Audit log integrity broken at event index {first_broken_index}",
                "events_checked": len(self.events),
                "first_broken_index": first_broken_index
            }
        else:
            return {
                "verified": True,
                "message": "Audit log integrity verified",
                "events_checked": len(self.events)
            }
    
    def export_events(self, filepath: str, 
                     event_type: Optional[str] = None,
                     start_time: Optional[str] = None,
                     end_time: Optional[str] = None) -> bool:
        """
        Export events to a file
        
        Args:
            filepath: Path to export file
            event_type: Optional event type to filter by
            start_time: Optional start time to filter by
            end_time: Optional end time to filter by
            
        Returns:
            True if successful, False otherwise
        """
        try:
            filtered_events = []
            
            for event in self.events:
                # Apply filters
                if event_type and event["event_type"] != event_type:
                    continue
                    
                if start_time and event["timestamp"] < start_time:
                    continue
                    
                if end_time and event["timestamp"] > end_time:
                    continue
                    
                filtered_events.append(event)
            
            with open(filepath, 'w') as f:
                json.dump(filtered_events, f, indent=2)
                
            logger.info(f"Exported {len(filtered_events)} events to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting events: {str(e)}")
            return False
    
    def clear(self):
        """Clear all events (for testing purposes only)"""
        logger.warning("Clearing all audit events - THIS SHOULD NOT BE DONE IN PRODUCTION")
        with self._lock:
            self.events = []
            self.event_hashes = []
            self.previous_block_hash = None

# Create a singleton instance
audit_logger = EnhancedAuditLogger()

# Function to get the singleton instance
def get_audit_logger() -> EnhancedAuditLogger:
    """Get the singleton audit logger instance"""
    return audit_logger
