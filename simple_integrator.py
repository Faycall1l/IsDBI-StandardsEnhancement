"""
Simplified System Integrator for Islamic Finance Standards Enhancement System

This module provides a simplified implementation of the system integrator
that connects the document agent, enhancement agent, and validation agent
through a shared database and file manager.
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleSystemIntegrator:
    """A simplified system integrator that connects all components."""
    
    def __init__(self):
        """Initialize the system integrator."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing SimpleSystemIntegrator")
        
        # Create data directories if they don't exist
        os.makedirs("data/standards", exist_ok=True)
        os.makedirs("data/documents", exist_ok=True)
        os.makedirs("data/enhancements", exist_ok=True)
        os.makedirs("data/validations", exist_ok=True)
        os.makedirs("data/events", exist_ok=True)
        os.makedirs("data/audit", exist_ok=True)
        
        # Initialize in-memory database
        self.standards = []
        self.documents = []
        self.enhancements = []
        self.validations = []
        self.events = []
        self.audit_logs = []
        
        # Load existing data if available
        self._load_data()
    
    def _load_data(self):
        """Load existing data from files."""
        try:
            if os.path.exists("data/standards/standards.json"):
                with open("data/standards/standards.json", "r") as f:
                    self.standards = json.load(f)
            
            if os.path.exists("data/enhancements/enhancements.json"):
                with open("data/enhancements/enhancements.json", "r") as f:
                    self.enhancements = json.load(f)
            
            if os.path.exists("data/validations/validations.json"):
                with open("data/validations/validations.json", "r") as f:
                    self.validations = json.load(f)
            
            if os.path.exists("data/events/events.json"):
                with open("data/events/events.json", "r") as f:
                    self.events = json.load(f)
            
            if os.path.exists("data/audit/audit_logs.json"):
                with open("data/audit/audit_logs.json", "r") as f:
                    self.audit_logs = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
    
    def _save_data(self):
        """Save data to files."""
        try:
            with open("data/standards/standards.json", "w") as f:
                json.dump(self.standards, f, indent=2)
            
            with open("data/enhancements/enhancements.json", "w") as f:
                json.dump(self.enhancements, f, indent=2)
            
            with open("data/validations/validations.json", "w") as f:
                json.dump(self.validations, f, indent=2)
            
            with open("data/events/events.json", "w") as f:
                json.dump(self.events, f, indent=2)
            
            with open("data/audit/audit_logs.json", "w") as f:
                json.dump(self.audit_logs, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving data: {e}")
    
    def get_standards(self):
        """Get all standards."""
        return self.standards
    
    def get_standard_by_id(self, standard_id):
        """Get a standard by ID."""
        for standard in self.standards:
            if standard.get("id") == standard_id:
                return standard
        return None
    
    def create_standard(self, standard_data):
        """Create a new standard."""
        standard_id = standard_data.get("id", str(uuid.uuid4()))
        standard = {
            "id": standard_id,
            "name": standard_data.get("name", ""),
            "type": standard_data.get("type", ""),
            "number": standard_data.get("number", ""),
            "description": standard_data.get("description", ""),
            "created_at": datetime.now().isoformat()
        }
        self.standards.append(standard)
        self._save_data()
        
        # Log the event
        self._log_event("standard_created", {
            "standard_id": standard_id,
            "name": standard.get("name")
        })
        
        return standard_id
    
    def process_document(self, file_path, standard_id):
        """Process a document for a standard."""
        self.logger.info(f"Processing document for standard {standard_id}")
        
        # Check if document exists
        if not os.path.exists(file_path):
            self.logger.error(f"Document not found: {file_path}")
            return {"success": False, "message": "Document not found"}
        
        # Get standard information
        standard = self.get_standard_by_id(standard_id)
        if not standard:
            # Create a new standard
            standard_data = {
                "id": standard_id,
                "name": f"Standard {standard_id}",
                "description": f"Standard {standard_id} imported from document"
            }
            self.create_standard(standard_data)
            standard = self.get_standard_by_id(standard_id)
        
        # Save document to file system
        document_path = f"data/documents/{standard_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        os.makedirs(os.path.dirname(document_path), exist_ok=True)
        with open(file_path, 'rb') as src, open(document_path, 'wb') as dst:
            dst.write(src.read())
        
        # Log document processing event
        self._log_event("document_processing_started", {
            "standard_id": standard_id,
            "document_path": document_path
        })
        
        # Simulate document processing
        extracted_data = {
            "definitions": [
                {"term": "Musharaka", "definition": "A partnership contract between two or more parties, each contributing capital."},
                {"term": "Diminishing Musharaka", "definition": "A form of partnership in which one partner promises to buy the equity share of the other partner gradually."}
            ],
            "accounting_treatments": [
                {"title": "Initial Recognition", "content": "Musharaka should be recognized when payment is made or when capital is paid to partners."},
                {"title": "Profit Distribution", "content": "Profits shall be recognized based on the agreement between partners."}
            ],
            "ambiguities": [
                {"section": "Profit Distribution", "description": "The standard does not clearly specify how to handle losses in case of negligence."},
                {"section": "Termination", "description": "The procedure for early termination is not well defined."}
            ]
        }
        
        # Log document processed event
        self._log_event("document_processed", {
            "standard_id": standard_id,
            "extracted_data": extracted_data
        })
        
        # Generate enhancements for ambiguities
        for ambiguity in extracted_data.get("ambiguities", []):
            self._generate_enhancement_for_ambiguity(standard_id, ambiguity)
        
        return {
            "success": True,
            "message": "Document processed successfully",
            "standard_id": standard_id,
            "definitions_count": len(extracted_data.get("definitions", [])),
            "treatments_count": len(extracted_data.get("accounting_treatments", [])),
            "ambiguities_count": len(extracted_data.get("ambiguities", [])),
            "enhancements_generated": len(extracted_data.get("ambiguities", []))
        }
    
    def _generate_enhancement_for_ambiguity(self, standard_id, ambiguity):
        """Generate an enhancement for an ambiguity."""
        enhancement_data = {
            "standard_id": standard_id,
            "title": f"Enhancement for {ambiguity.get('section')}",
            "description": f"Addressing ambiguity: {ambiguity.get('description')}",
            "proposed_text": f"The {ambiguity.get('section')} should be clarified to address: {ambiguity.get('description')}",
            "rationale": "This enhancement addresses an ambiguity identified in the standard.",
            "created_at": datetime.now().isoformat(),
            "status": "pending_validation"
        }
        
        # Create enhancement
        enhancement_id = self.create_enhancement_proposal(enhancement_data)
        
        # Validate enhancement
        self.validate_enhancement(enhancement_id)
        
        return enhancement_id
    
    def generate_enhancement(self, standard_id, standard_text, use_web_search=True):
        """Generate an enhancement for a standard."""
        self.logger.info(f"Generating enhancement for standard: {standard_id}")
        
        try:
            # Get standard from database if it exists
            standard = self.get_standard_by_id(standard_id)
            if not standard and not standard_text:
                self.logger.error(f"Standard not found: {standard_id}")
                return {"success": False, "message": "Standard not found"}
            
            # Generate enhancement (simulated)
            enhancement_result = {
                "standard_id": standard_id,
                "title": "Enhancement Proposal",
                "description": "This enhancement addresses clarity issues in the standard.",
                "proposed_text": "The standard should clearly define all key terms used and provide comprehensive examples.",
                "rationale": "Improved clarity through explicit definition of key terms reduces ambiguity in interpretation.",
                "key_concepts": ["standard", "guidelines", "clarity"],
                "web_sources": []
            }
            
            # Create enhancement proposal
            proposal_id = self.create_enhancement_proposal({
                "standard_id": standard_id,
                "title": enhancement_result.get("title"),
                "description": enhancement_result.get("description"),
                "proposed_text": enhancement_result.get("proposed_text"),
                "rationale": enhancement_result.get("rationale"),
                "status": "pending_validation",
                "created_at": datetime.now().isoformat()
            })
            
            # Add proposal ID to result
            enhancement_result["proposal_id"] = proposal_id
            
            # Validate enhancement
            self.validate_enhancement(proposal_id)
            
            return {
                "success": True,
                "message": "Enhancement generated successfully",
                "proposal_id": proposal_id,
                **enhancement_result
            }
            
        except Exception as e:
            self.logger.error(f"Error in generate_enhancement: {str(e)}")
            return {
                "success": False,
                "message": f"Error generating enhancement: {str(e)}"
            }
    
    def create_enhancement_proposal(self, proposal_data):
        """Create a new enhancement proposal."""
        proposal_id = proposal_data.get("id", str(uuid.uuid4()))
        proposal = {
            "id": proposal_id,
            "standard_id": proposal_data.get("standard_id"),
            "title": proposal_data.get("title"),
            "description": proposal_data.get("description"),
            "proposed_text": proposal_data.get("proposed_text"),
            "rationale": proposal_data.get("rationale"),
            "status": proposal_data.get("status", "pending"),
            "created_at": proposal_data.get("created_at", datetime.now().isoformat()),
            "votes_up": 0,
            "votes_down": 0,
            "comments": []
        }
        self.enhancements.append(proposal)
        self._save_data()
        
        # Log the event
        self._log_event("enhancement_generated", {
            "standard_id": proposal.get("standard_id"),
            "enhancement_id": proposal_id,
            "title": proposal.get("title")
        })
        
        return proposal_id
    
    def get_enhancement_proposals(self, status=None):
        """Get enhancement proposals."""
        if status:
            return [p for p in self.enhancements if p.get("status") == status]
        return self.enhancements
    
    def get_enhancement_proposal_by_id(self, proposal_id):
        """Get an enhancement proposal by ID."""
        for proposal in self.enhancements:
            if proposal.get("id") == proposal_id:
                return proposal
        return None
    
    def update_enhancement_proposal(self, proposal_id, update_data):
        """Update an enhancement proposal."""
        for i, proposal in enumerate(self.enhancements):
            if proposal.get("id") == proposal_id:
                self.enhancements[i].update(update_data)
                self._save_data()
                
                # Log the event
                self._log_event("enhancement_updated", {
                    "enhancement_id": proposal_id,
                    "updates": update_data
                })
                
                return True
        return False
    
    def validate_enhancement(self, enhancement_id):
        """Validate an enhancement proposal."""
        self.logger.info(f"Validating enhancement: {enhancement_id}")
        
        # Get enhancement
        enhancement = self.get_enhancement_proposal_by_id(enhancement_id)
        if not enhancement:
            self.logger.error(f"Enhancement not found: {enhancement_id}")
            return {"success": False, "message": "Enhancement not found"}
        
        # Simulate validation
        validation_result = {
            "enhancement_id": enhancement_id,
            "is_valid": True,
            "feedback": "This enhancement properly addresses the ambiguity in the standard.",
            "shariah_compliance": "The proposed enhancement is compliant with Shariah principles.",
            "timestamp": datetime.now().isoformat()
        }
        
        # Save validation
        validation_id = self.create_validation(validation_result)
        
        # Update enhancement status
        self.update_enhancement_proposal(enhancement_id, {"status": "validated"})
        
        # Log the event
        self._log_event("enhancement_validated", {
            "enhancement_id": enhancement_id,
            "validation_id": validation_id,
            "is_valid": validation_result.get("is_valid")
        })
        
        return validation_result
    
    def create_validation(self, validation_data):
        """Create a new validation."""
        validation_id = validation_data.get("id", str(uuid.uuid4()))
        validation = {
            "id": validation_id,
            "enhancement_id": validation_data.get("enhancement_id"),
            "is_valid": validation_data.get("is_valid", False),
            "feedback": validation_data.get("feedback", ""),
            "shariah_compliance": validation_data.get("shariah_compliance", ""),
            "timestamp": validation_data.get("timestamp", datetime.now().isoformat())
        }
        self.validations.append(validation)
        self._save_data()
        return validation_id
    
    def get_validations(self, enhancement_id=None):
        """Get validations."""
        if enhancement_id:
            return [v for v in self.validations if v.get("enhancement_id") == enhancement_id]
        return self.validations
    
    def get_recent_events(self, limit=10):
        """Get recent events."""
        return sorted(self.events, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]
    
    def get_audit_logs(self, limit=10):
        """Get audit logs."""
        return sorted(self.audit_logs, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]
    
    def _log_event(self, event_type, payload):
        """Log an event."""
        event = {
            "id": str(uuid.uuid4()),
            "type": event_type,
            "topic": self._get_topic_for_event_type(event_type),
            "payload": payload,
            "timestamp": datetime.now().isoformat()
        }
        self.events.append(event)
        
        # Also add to audit log
        self._log_audit(event_type, payload)
        
        self._save_data()
        return event
    
    def _log_audit(self, event_type, data):
        """Log an audit entry."""
        audit_entry = {
            "id": str(uuid.uuid4()),
            "event_type": event_type,
            "user_id": data.get("user_id", "system"),
            "timestamp": datetime.now().isoformat(),
            "details": data
        }
        self.audit_logs.append(audit_entry)
        self._save_data()
        return audit_entry
    
    def _get_topic_for_event_type(self, event_type):
        """Get the topic for an event type."""
        if event_type.startswith("document"):
            return "document"
        elif event_type.startswith("enhancement"):
            return "enhancement"
        elif event_type.startswith("validation"):
            return "validation"
        elif event_type.startswith("standard"):
            return "standard"
        else:
            return "system"
    
    def publish_event(self, event_data):
        """Publish an event."""
        event = {
            "id": str(uuid.uuid4()),
            "type": event_data.get("type"),
            "topic": event_data.get("topic"),
            "payload": event_data.get("payload"),
            "timestamp": datetime.now().isoformat()
        }
        self.events.append(event)
        self._save_data()
        return event

# Create a singleton instance
system_integrator = SimpleSystemIntegrator()
