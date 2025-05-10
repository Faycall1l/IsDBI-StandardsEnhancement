"""
System Integrator for Islamic Finance Standards Enhancement System

This module integrates the multi-agent architecture with the web interface,
connecting all components through shared database, file system, and event bus.
"""

import os
import sys
import json
import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import shared components
from IslamicFinanceStandardsAI.integration.event_bus import EventBus, EventType
from IslamicFinanceStandardsAI.database.shared_database import SharedDatabase
from IslamicFinanceStandardsAI.utils.file_manager import FileManager

# Import agents
try:
    from IslamicFinanceStandardsAI.agents.document_agent.document_processor import DocumentProcessor
    document_agent_available = True
except ImportError:
    document_agent_available = False
    print("Warning: DocumentProcessor not available, using mock implementation")

try:
    from IslamicFinanceStandardsAI.agents.enhancement_agent.enhancement_generator import EnhancementGenerator
    enhancement_agent_available = True
except ImportError:
    enhancement_agent_available = False
    print("Warning: EnhancementGenerator not available, using mock implementation")

try:
    from IslamicFinanceStandardsAI.agents.validation_agent.validation_processor import ValidationProcessor
    validation_agent_available = True
except ImportError:
    validation_agent_available = False
    print("Warning: ValidationProcessor not available, using mock implementation")

# Import knowledge graph
try:
    from IslamicFinanceStandardsAI.database.knowledge_graph import KnowledgeGraph
    knowledge_graph_available = True
except ImportError:
    knowledge_graph_available = False
    print("Warning: KnowledgeGraph not available, using mock implementation")

# Import audit logger
try:
    from IslamicFinanceStandardsAI.utils.audit_logger import AuditLogger
    audit_logger_available = True
except ImportError:
    audit_logger_available = False
    print("Warning: AuditLogger not available, using mock implementation")

# Mock implementations
class MockDocumentProcessor:
    def __init__(self, event_bus=None, knowledge_graph=None):
        self.event_bus = event_bus
        self.knowledge_graph = knowledge_graph
        print("Initialized MockDocumentProcessor")
    
    def process_document(self, document_path, standard_id):
        print(f"Mock: Processing document {document_path} for standard {standard_id}")
        
        # Publish event
        if self.event_bus:
            self.event_bus.publish(
                "documents",
                EventType.DOCUMENT_PROCESSED,
                {
                    "standard_id": standard_id,
                    "document_path": document_path,
                    "extracted_data": {
                        "definitions": [
                            {"term": "Musharaka", "definition": "A partnership between two or more parties..."}
                        ],
                        "accounting_treatments": [
                            {"title": "Initial Recognition", "text": "The partner's share in Musharaka capital..."}
                        ],
                        "transaction_structures": [
                            {"title": "Diminishing Musharaka", "description": "A form of partnership..."}
                        ],
                        "ambiguities": [
                            {"text": "The standard does not clearly specify...", "severity": "medium"}
                        ]
                    }
                }
            )
        
        return {
            "standard_id": standard_id,
            "success": True,
            "message": "Document processed successfully (mock)",
            "extracted_data": {
                "definitions": [
                    {"term": "Musharaka", "definition": "A partnership between two or more parties..."}
                ],
                "accounting_treatments": [
                    {"title": "Initial Recognition", "text": "The partner's share in Musharaka capital..."}
                ],
                "transaction_structures": [
                    {"title": "Diminishing Musharaka", "description": "A form of partnership..."}
                ],
                "ambiguities": [
                    {"text": "The standard does not clearly specify...", "severity": "medium"}
                ]
            }
        }

class MockEnhancementGenerator:
    def __init__(self, event_bus=None, knowledge_graph=None):
        self.event_bus = event_bus
        self.knowledge_graph = knowledge_graph
        print("Initialized MockEnhancementGenerator")
    
    def generate_enhancement(self, standard_id, standard_text, use_web_search=True):
        print(f"Mock: Generating enhancement for standard {standard_id}")
        
        enhancement_id = f"enhancement-{standard_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "id": enhancement_id,
            "standard_id": standard_id,
            "title": "Enhanced Standard",
            "description": "This enhancement addresses ambiguities in the standard.",
            "proposed_text": standard_text + "\n\nAdditional clarity: The standard should explicitly define all terms and provide clear examples.",
            "rationale": "The enhancement improves clarity and reduces potential for misinterpretation.",
            "created_at": datetime.now().isoformat()
        }

class MockValidationProcessor:
    def __init__(self, event_bus=None, knowledge_graph=None):
        self.event_bus = event_bus
        self.knowledge_graph = knowledge_graph
        print("Initialized MockValidationProcessor")
    
    def validate_enhancement(self, enhancement_id, enhancement_data):
        print(f"Mock: Validating enhancement {enhancement_id}")
        
        validation_id = f"validation-{enhancement_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "id": validation_id,
            "enhancement_id": enhancement_id,
            "is_valid": True,
            "feedback": "The enhancement is valid and improves the standard.",
            "shariah_compliance": "The enhancement is compliant with Shariah principles.",
            "created_at": datetime.now().isoformat()
        }

class MockKnowledgeGraph:
    def __init__(self):
        print("Initialized MockKnowledgeGraph")
    
    def create_node(self, label, properties):
        return f"node-{uuid.uuid4()}"
    
    def find_nodes_by_properties(self, label, properties):
        return []
    
    def create_relationship(self, start_node_id, end_node_id, relationship_type, properties=None):
        return f"rel-{uuid.uuid4()}"
    
    def get_standard(self, standard_id):
        return None

class MockAuditLogger:
    def __init__(self):
        print("Initialized MockAuditLogger")
        self.logs = []
    
    def log_event(self, event_data):
        log_id = f"log-{uuid.uuid4()}"
        log_entry = {
            "id": log_id,
            "event_type": event_data.get("event_type"),
            "data": event_data.get("details", {}),
            "user_id": event_data.get("user_id"),
            "timestamp": event_data.get("timestamp") or datetime.now().isoformat()
        }
        self.logs.append(log_entry)
        return log_id
    
    def get_logs(self, limit=10):
        return self.logs[:limit]

class SystemIntegrator:
    """Integrates all components of the Islamic Finance Standards Enhancement System"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SystemIntegrator, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self._initialized = True
        self.logger = logging.getLogger(__name__)
        
        # Initialize event bus
        self.event_bus = EventBus()
        self.logger.info("Initialized EventBus")
        
        # Initialize knowledge graph
        if knowledge_graph_available:
            self.knowledge_graph = KnowledgeGraph()
        else:
            self.knowledge_graph = MockKnowledgeGraph()
        self.logger.info("Initialized KnowledgeGraph")
        
        # Initialize document processor
        if document_agent_available:
            self.document_processor = DocumentProcessor(self.event_bus, self.knowledge_graph)
        else:
            self.document_processor = MockDocumentProcessor(self.event_bus, self.knowledge_graph)
        self.logger.info("Initialized DocumentProcessor")
        
        # Initialize enhancement generator
        if enhancement_agent_available:
            self.enhancement_generator = EnhancementGenerator(self.event_bus, self.knowledge_graph)
        else:
            self.enhancement_generator = MockEnhancementGenerator(self.event_bus, self.knowledge_graph)
        self.logger.info("Initialized EnhancementGenerator")
        
        # Initialize validation processor
        if validation_agent_available:
            self.validation_processor = ValidationProcessor(self.event_bus, self.knowledge_graph)
        else:
            self.validation_processor = MockValidationProcessor(self.event_bus, self.knowledge_graph)
        self.logger.info("Initialized ValidationProcessor")
        
        # Initialize audit logger
        if audit_logger_available:
            self.audit_logger = AuditLogger()
        else:
            self.audit_logger = MockAuditLogger()
        self.logger.info("Initialized AuditLogger")
        
        # Initialize shared database
        self.shared_db = SharedDatabase()
        self.logger.info("Initialized SharedDatabase")
        
        # Initialize file manager
        self.file_manager = FileManager()
        self.logger.info("Initialized FileManager")
        
        # Set up event listeners
        self._setup_event_listeners()
        self.logger.info("Event listeners set up")
        
        self.logger.info("SystemIntegrator initialization complete")
    
    def _setup_event_listeners(self):
        """Set up event listeners for the event bus"""
        self.event_bus.subscribe("documents", self._handle_document_processed)
        self.event_bus.subscribe("enhancements", self._handle_enhancement_generated)
        self.event_bus.subscribe("validations", self._handle_enhancement_validated)
    
    def _handle_document_processed(self, event):
        """Handle document processed event"""
        self.logger.info(f"Handling document processed event: {event['id']}")
        # In a real implementation, this would trigger enhancement generation
        # For now, we'll just log the event
        self.audit_logger.log_event({
            "event_type": "document_processed",
            "details": event
        })
    
    def _handle_enhancement_generated(self, event):
        """Handle enhancement generated event"""
        self.logger.info(f"Handling enhancement generated event: {event['id']}")
        # In a real implementation, this would trigger validation
        # For now, we'll just log the event
        self.audit_logger.log_event({
            "event_type": "enhancement_generated",
            "details": event
        })
        
        # Get the enhancement data
        enhancement_data = event["payload"].get("enhancement", {})
        enhancement_id = enhancement_data.get("id")
        
        # Trigger validation if we have an enhancement ID
        if enhancement_id:
            self.validate_enhancement(enhancement_id, enhancement_data)
    
    def _handle_enhancement_validated(self, event):
        """Handle enhancement validated event"""
        self.logger.info(f"Handling enhancement validated event: {event['id']}")
        # In a real implementation, this would update the enhancement status
        # For now, we'll just log the event
        self.audit_logger.log_event({
            "event_type": "enhancement_validated",
            "details": event
        })
    
    def publish_event(self, event_data):
        """Publish an event to the event bus"""
        return self.event_bus.publish_event(event_data)
    
    def get_recent_events(self, limit=10):
        """Get recent events from the event bus"""
        try:
            return self.event_bus.get_recent_events(limit=limit)
        except Exception as e:
            self.logger.error(f"Error getting recent events: {e}")
            return []
    
    def process_document(self, file_path, standard_id):
        """Process a document using the document agent and trigger enhancement flow
        
        Args:
            file_path: Path to the document file
            standard_id: ID of the standard
            
        Returns:
            dict: Result of the processing
        """
        try:
            self.logger.info(f"Processing document for standard {standard_id} from {file_path}")
            
            # Check if document exists
            if not os.path.exists(file_path):
                self.logger.error(f"Document not found: {file_path}")
                return {"success": False, "message": "Document not found"}
            
            # Process document with document agent
            result = self.document_processor.process_document(file_path, standard_id)
            
            # Extract data from result
            extracted_data = result.get("extracted_data", {})
            
            # Log the document processing
            self.logger.info(f"Processed document for standard {standard_id}: " +
                           f"{len(extracted_data.get('definitions', []))} definitions, " +
                           f"{len(extracted_data.get('accounting_treatments', []))} accounting treatments, " +
                           f"{len(extracted_data.get('transaction_structures', []))} transaction structures, " +
                           f"{len(extracted_data.get('ambiguities', []))} ambiguities")
            
            # Return success result
            return {
                "success": True,
                "message": "Document processed successfully",
                "standard_id": standard_id,
                "document_path": file_path,
                "extracted_data_summary": {
                    "definitions": len(extracted_data.get("definitions", [])),
                    "accounting_treatments": len(extracted_data.get("accounting_treatments", [])),
                    "transaction_structures": len(extracted_data.get("transaction_structures", [])),
                    "ambiguities": len(extracted_data.get("ambiguities", []))
                }
            }
        except Exception as e:
            self.logger.error(f"Error processing document: {e}")
            return {
                "success": False,
                "message": f"Error processing document: {e}"
            }
    
    def generate_enhancement(self, standard_id, standard_text, use_web_search=True):
        """Generate an enhancement for a standard"""
        self.logger.info(f"Generating enhancement for standard: {standard_id}")
        
        try:
            # Get standard from database if it exists
            standard = self.shared_db.get_standard_by_id(standard_id)
            if not standard and not standard_text:
                self.logger.error(f"Standard not found: {standard_id}")
                return {"success": False, "message": "Standard not found"}
            
            # Use enhancement generator to generate enhancement
            enhancement_result = self.enhancement_generator.generate_enhancement(
                standard_id, standard_text, use_web_search
            )
            
            # Generate a unique ID for the proposal
            proposal_id = str(uuid.uuid4())
            
            # Prepare proposal data
            proposal_data = {
                "id": proposal_id,
                "standard_id": standard_id,
                "title": enhancement_result.get("title", "Enhancement Proposal"),
                "description": enhancement_result.get("description", ""),
                "proposed_text": enhancement_result.get("proposed_text", ""),
                "rationale": enhancement_result.get("rationale", ""),
                "status": "pending_validation",
                "created_at": datetime.now().isoformat(),
                "created_by": "system"
            }
            
            # Save the proposal to the database
            try:
                self.shared_db.create_enhancement_proposal(proposal_data)
            except Exception as db_error:
                self.logger.warning(f"Could not save enhancement proposal to database: {db_error}")
            
            # Publish an event for enhancement generation
            self.event_bus.publish_event({
                "type": "ENHANCEMENT_GENERATED",
                "topic": "enhancement",
                "payload": {
                    "standard_id": standard_id,
                    "enhancement_id": proposal_id,
                    "enhancement_data": proposal_data,
                    "timestamp": datetime.now().isoformat()
                }
            })
            
            # Log the enhancement generation
            self.audit_logger.log_event({
                "event_type": "enhancement_generated",
                "standard_id": standard_id,
                "enhancement_id": proposal_id,
                "user_id": "system",
                "timestamp": datetime.now().isoformat(),
                "details": {
                    "title": proposal_data["title"],
                    "use_web_search": use_web_search
                }
            })
            
            # Automatically trigger validation
            self.validate_enhancement(proposal_id, enhancement_result)
            
            return {
                "success": True,
                "message": "Enhancement generated successfully",
                "proposal_id": proposal_id,
                **enhancement_result
            }
        except Exception as e:
            self.logger.error(f"Error generating enhancement: {e}")
            return {
                "success": False,
                "message": f"Error generating enhancement: {e}"
            }
    
    def validate_enhancement(self, enhancement_id, enhancement_data=None):
        """Validate an enhancement proposal"""
        self.logger.info(f"Validating enhancement: {enhancement_id}")
        
        try:
            # Get enhancement data from database if not provided
            if not enhancement_data:
                enhancement_data = self.shared_db.get_enhancement_proposal_by_id(enhancement_id)
                if not enhancement_data:
                    self.logger.error(f"Enhancement proposal not found: {enhancement_id}")
                    return {"success": False, "message": "Enhancement proposal not found"}
            
            # Use validation processor to validate enhancement
            validation_result = self.validation_processor.validate_enhancement(
                enhancement_id, enhancement_data
            )
            
            # Generate a unique ID for the validation
            validation_id = str(uuid.uuid4())
            
            # Prepare validation data
            validation_data = {
                "id": validation_id,
                "enhancement_id": enhancement_id,
                "is_valid": validation_result.get("is_valid", False),
                "feedback": validation_result.get("feedback", ""),
                "shariah_compliance": validation_result.get("shariah_compliance", ""),
                "created_at": datetime.now().isoformat()
            }
            
            # Save the validation to the database
            try:
                self.shared_db.create_validation(validation_data)
            except Exception as db_error:
                self.logger.warning(f"Could not save validation to database: {db_error}")
            
            # Update the enhancement status based on validation
            new_status = "validated" if validation_data["is_valid"] else "needs_revision"
            try:
                self.shared_db.update_enhancement_proposal_status(enhancement_id, new_status)
            except Exception as db_error:
                self.logger.warning(f"Could not update enhancement status: {db_error}")
            
            # Publish an event for validation completion
            self.event_bus.publish_event({
                "type": "ENHANCEMENT_VALIDATED",
                "topic": "validation",
                "payload": {
                    "enhancement_id": enhancement_id,
                    "validation_id": validation_id,
                    "validation_result": validation_data,
                    "timestamp": datetime.now().isoformat()
                }
            })
            
            # Log the validation
            self.audit_logger.log_event({
                "event_type": "enhancement_validated",
                "enhancement_id": enhancement_id,
                "validation_id": validation_id,
                "user_id": "system",
                "timestamp": datetime.now().isoformat(),
                "details": {
                    "is_valid": validation_data["is_valid"],
                    "feedback": validation_data["feedback"]
                }
            })
            
            return {
                "success": True,
                "message": "Enhancement validated successfully",
                "validation_id": validation_id,
                **validation_result
            }
        except Exception as e:
            self.logger.error(f"Error validating enhancement: {e}")
            return {
                "success": False,
                "message": f"Error validating enhancement: {e}"
            }
    
    def get_audit_logs(self, limit=10):
        """Get recent audit logs"""
        # Try to get logs from database first
        try:
            logs = self.shared_db.get_audit_logs(limit)
            if logs:
                return logs
        except Exception as e:
            self.logger.error(f"Error getting audit logs from database: {e}")
        
        # Fall back to audit logger
        logs = self.audit_logger.get_logs(limit)
        
        # Try file system as last resort
        if not logs:
            try:
                logs = self.file_manager.get_recent_audit_logs(limit)
            except Exception as e:
                self.logger.error(f"Error getting audit logs from file system: {e}")
        
        return logs
    
    def get_standards(self):
        """Get all standards"""
        return self.shared_db.get_standards()
    
    def get_standard_by_id(self, standard_id):
        """Get a standard by ID"""
        return self.shared_db.get_standard_by_id(standard_id)
    
    def get_enhancement_proposals(self, status=None):
        """Get all enhancement proposals"""
        return self.shared_db.get_enhancement_proposals(status)
    
    def get_enhancement_proposal_by_id(self, proposal_id):
        """Get an enhancement proposal by ID"""
        return self.shared_db.get_enhancement_proposal_by_id(proposal_id)
    
    def add_comment_to_proposal(self, proposal_id, comment_text, user_id=None):
        """Add a comment to a proposal"""
        comment_id = self.shared_db.create_comment({
            "proposal_id": proposal_id,
            "user_id": user_id,
            "text": comment_text
        })
        
        # Publish event
        self.event_bus.publish_event({
            "type": "COMMENT_ADDED",
            "topic": "enhancements",
            "payload": {
                "proposal_id": proposal_id,
                "comment_id": comment_id,
                "user_id": user_id,
                "text": comment_text,
                "timestamp": datetime.now().isoformat()
            }
        })
        
        return comment_id
    
    def vote_on_proposal(self, proposal_id, vote_type, user_id=None):
        """Vote on a proposal"""
        vote_id = self.shared_db.record_vote({
            "proposal_id": proposal_id,
            "user_id": user_id,
            "vote_type": vote_type
        })
        
        # Publish event
        self.event_bus.publish_event({
            "type": "VOTE_RECORDED",
            "topic": "enhancements",
            "payload": {
                "proposal_id": proposal_id,
                "vote_id": vote_id,
                "user_id": user_id,
                "vote_type": vote_type,
                "timestamp": datetime.now().isoformat()
            }
        })
        
        return vote_id
    
    def update_proposal_status(self, proposal_id, status, reason=None, user_id=None):
        """Update the status of a proposal"""
        success = self.shared_db.update_enhancement_proposal_status(proposal_id, status)
        
        if success:
            # Determine event type
            event_type = None
            if status == "approved":
                event_type = "ENHANCEMENT_APPROVED"
            elif status == "rejected":
                event_type = "ENHANCEMENT_REJECTED"
            elif status == "needs_revision":
                event_type = "ENHANCEMENT_NEEDS_REVISION"
            
            if event_type:
                # Publish event
                self.event_bus.publish_event({
                    "type": event_type,
                    "topic": "enhancements",
                    "payload": {
                        "proposal_id": proposal_id,
                        "user_id": user_id,
                        "reason": reason,
                        "timestamp": datetime.now().isoformat()
                    }
                })
        
        return success
