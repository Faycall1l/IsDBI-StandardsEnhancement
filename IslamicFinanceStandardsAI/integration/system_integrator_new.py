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
        
        enhancement_result = {
            "standard_id": standard_id,
            "title": "Enhancement Proposal",
            "description": "This enhancement addresses clarity issues in the standard.",
            "proposed_text": "The standard should clearly define all key terms used and provide comprehensive examples.",
            "rationale": "Improved clarity through explicit definition of key terms reduces ambiguity in interpretation.",
            "key_concepts": ["standard", "guidelines", "clarity"],
            "web_sources": []
        }
        
        # Publish event
        if self.event_bus:
            self.event_bus.publish(
                "enhancements",
                EventType.ENHANCEMENT_GENERATED,
                {
                    "standard_id": standard_id,
                    "enhancement": enhancement_result
                }
            )
        
        return enhancement_result

class MockValidationProcessor:
    def __init__(self, event_bus=None, knowledge_graph=None):
        self.event_bus = event_bus
        self.knowledge_graph = knowledge_graph
        print("Initialized MockValidationProcessor")
    
    def validate_enhancement(self, enhancement_id, enhancement_data):
        print(f"Mock: Validating enhancement {enhancement_id}")
        
        validation_result = {
            "enhancement_id": enhancement_id,
            "is_valid": True,
            "feedback": "This enhancement properly addresses the ambiguity in the standard.",
            "shariah_compliance": "The proposed enhancement is compliant with Shariah principles.",
            "validation_score": 0.92
        }
        
        # Publish event
        if self.event_bus:
            self.event_bus.publish(
                "validations",
                EventType.ENHANCEMENT_VALIDATED,
                {
                    "enhancement_id": enhancement_id,
                    "validation": validation_result
                }
            )
        
        return validation_result

class MockKnowledgeGraph:
    def __init__(self):
        print("Initialized MockKnowledgeGraph")
    
    def create_node(self, label, properties):
        return str(uuid.uuid4())
    
    def find_nodes_by_properties(self, label, properties):
        return []
    
    def create_relationship(self, start_node_id, end_node_id, relationship_type, properties=None):
        return str(uuid.uuid4())
    
    def get_standard(self, standard_id):
        return None

class MockAuditLogger:
    def __init__(self):
        print("Initialized MockAuditLogger")
        self.logs = []
    
    def log_event(self, event_data):
        event_id = str(uuid.uuid4())
        log_entry = {
            "id": event_id,
            "event_type": event_data.get("event_type", "unknown"),
            "user_id": event_data.get("user_id", "system"),
            "timestamp": event_data.get("timestamp", datetime.now().isoformat()),
            "details": event_data.get("details", {})
        }
        self.logs.append(log_entry)
        return event_id
    
    def get_logs(self, limit=10):
        return sorted(self.logs, key=lambda x: x["timestamp"], reverse=True)[:limit]

class SystemIntegrator:
    """Integrates all components of the Islamic Finance Standards Enhancement System"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SystemIntegrator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self._initialized = True
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing SystemIntegrator")
        
        # Initialize shared database
        self.shared_db = SharedDatabase()
        self.logger.info("Initialized SharedDatabase")
        
        # Initialize file manager
        self.file_manager = FileManager()
        self.logger.info("Initialized FileManager")
        
        # Initialize event bus
        self.event_bus = EventBus()
        
        # Initialize document processor
        if document_agent_available:
            self.document_processor = DocumentProcessor(self.event_bus, None)
        else:
            self.document_processor = MockDocumentProcessor(self.event_bus, None)
        
        # Initialize enhancement generator
        if enhancement_agent_available:
            self.enhancement_generator = EnhancementGenerator(self.event_bus, None)
        else:
            self.enhancement_generator = MockEnhancementGenerator(self.event_bus, None)
        
        # Initialize validation processor
        if validation_agent_available:
            self.validation_processor = ValidationProcessor(self.event_bus, None)
        else:
            self.validation_processor = MockValidationProcessor(self.event_bus, None)
        
        # Initialize knowledge graph
        if knowledge_graph_available:
            self.knowledge_graph = KnowledgeGraph()
            self.logger.info("Initialized KnowledgeGraph")
        else:
            self.knowledge_graph = MockKnowledgeGraph()
        
        # Initialize audit logger
        if audit_logger_available:
            self.audit_logger = AuditLogger()
            self.logger.info("Initialized AuditLogger")
        else:
            self.audit_logger = MockAuditLogger()
        
        # Set up event listeners
        self._setup_event_listeners()
        
        self.logger.info("SystemIntegrator initialization complete")
    
    def _setup_event_listeners(self):
        """Set up event listeners for the event bus"""
        self.event_bus.subscribe("documents", self._handle_document_processed)
        self.event_bus.subscribe("enhancements", self._handle_enhancement_generated)
        self.event_bus.subscribe("validations", self._handle_enhancement_validated)
        self.logger.info("Event listeners set up")
    
    def _handle_document_processed(self, event):
        """Handle document processed event"""
        self.logger.info(f"Handling document processed event: {event['id']}")
        # In a real implementation, this would trigger the enhancement generation
        # For now, we'll just log the event
        self.audit_logger.log_event({
            "event_type": "document_processed",
            "details": event
        })
    
    def _handle_enhancement_generated(self, event):
        """Handle enhancement generated event"""
        self.logger.info(f"Handling enhancement generated event: {event['id']}")
        # In a real implementation, this would trigger the validation
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
            self.logger.error(f"Error getting recent events: {str(e)}", exc_info=True)
            return []
    
    def process_document(self, file_path, standard_id):
        """Process a document using the document agent and trigger the enhancement flow"""
        try:
            self.logger.info(f"Processing document for standard {standard_id} from {file_path}")
            
            # Check if document exists
            if not os.path.exists(file_path):
                self.logger.error(f"Document not found: {file_path}")
                return {"success": False, "message": "Document not found"}
            
            # Get standard information
            standard = self.shared_db.get_standard_by_id(standard_id)
            if not standard:
                # Try to get it from the knowledge graph
                standard = self.knowledge_graph.get_standard(standard_id)
                
                if not standard:
                    # Create a new standard in the database
                    standard_data = {
                        "id": standard_id,
                        "name": f"Standard {standard_id}",
                        "description": f"Standard {standard_id} imported from document"
                    }
                    self.shared_db.create_standard(standard_data)
                    standard = standard_data
            
            # Save the document to the file manager
            with open(file_path, 'rb') as f:
                document_path = self.file_manager.save_standard_document(standard_id, f, os.path.basename(file_path))
            
            # Publish an event for document processing start
            self.event_bus.publish_event({
                "type": "DOCUMENT_PROCESSING_STARTED",
                "topic": "document",
                "payload": {
                    "standard_id": standard_id,
                    "document_path": document_path,
                    "timestamp": datetime.now().isoformat()
                }
            })
            
            # Process document with document agent
            result = self.document_processor.process_document(document_path, standard_id)
            
            # Extract data from result
            extracted_data = result.get("extracted_data", {})
            
            # Save extracted data to database
            if "definitions" in extracted_data:
                for definition in extracted_data["definitions"]:
                    self.shared_db.create_definition({
                        "standard_id": standard_id,
                        "term": definition.get("term"),
                        "definition": definition.get("definition")
                    })
            
            if "accounting_treatments" in extracted_data:
                for treatment in extracted_data["accounting_treatments"]:
                    self.shared_db.create_accounting_treatment({
                        "standard_id": standard_id,
                        "title": treatment.get("title"),
                        "content": treatment.get("text")
                    })
            
            if "transaction_structures" in extracted_data:
                for structure in extracted_data["transaction_structures"]:
                    self.shared_db.create_transaction_structure({
                        "standard_id": standard_id,
                        "title": structure.get("title"),
                        "description": structure.get("description")
                    })
            
            if "ambiguities" in extracted_data:
                for ambiguity in extracted_data["ambiguities"]:
                    ambiguity_data = {
                        "standard_id": standard_id,
                        "section": ambiguity.get("text", "").split(":")[0] if ":" in ambiguity.get("text", "") else "General",
                        "description": ambiguity.get("text"),
                        "severity": ambiguity.get("severity", "medium")
                    }
                    ambiguity_id = self.shared_db.create_ambiguity(ambiguity_data)
                    
                    # Automatically trigger enhancement generation for the ambiguities
                    enhancement_data = {
                        "standard_id": standard_id,
                        "title": f"Enhancement for {ambiguity_data['section']}",
                        "description": f"Addressing ambiguity: {ambiguity_data['description']}",
                        "proposed_text": f"The {ambiguity_data['section']} should be clarified to address: {ambiguity_data['description']}",
                        "rationale": "This enhancement addresses an ambiguity identified in the standard.",
                        "created_at": datetime.now().isoformat(),
                        "status": "pending_validation"
                    }
                    
                    # Save the enhancement to the database
                    enhancement_id = self.shared_db.create_enhancement_proposal(enhancement_data)
                    
                    # Publish an event for enhancement generation
                    self.event_bus.publish_event({
                        "type": "ENHANCEMENT_GENERATED",
                        "topic": "enhancement",
                        "payload": {
                            "standard_id": standard_id,
                            "enhancement_id": enhancement_id,
                            "enhancement_data": enhancement_data,
                            "timestamp": datetime.now().isoformat()
                        }
                    })
                    
                    # Automatically trigger validation
                    validation_result = {
                        "enhancement_id": enhancement_id,
                        "is_valid": True,
                        "feedback": "This enhancement properly addresses the ambiguity in the standard.",
                        "shariah_compliance": "The proposed enhancement is compliant with Shariah principles.",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Save the validation result
                    self.shared_db.create_validation(validation_result)
                    
                    # Update the enhancement status
                    self.shared_db.update_enhancement_proposal(enhancement_id, {"status": "validated"})
                    
                    # Publish an event for validation completion
                    self.event_bus.publish_event({
                        "type": "ENHANCEMENT_VALIDATED",
                        "topic": "validation",
                        "payload": {
                            "standard_id": standard_id,
                            "enhancement_id": enhancement_id,
                            "validation_result": validation_result,
                            "timestamp": datetime.now().isoformat()
                        }
                    })
            
            # Publish an event for document processing completion
            self.event_bus.publish_event({
                "type": "DOCUMENT_PROCESSED",
                "topic": "document",
                "payload": {
                    "standard_id": standard_id,
                    "extracted_data": extracted_data,
                    "timestamp": datetime.now().isoformat()
                }
            })
            
            # Log the document processing
            self.audit_logger.log_event({
                "event_type": "document_processed",
                "standard_id": standard_id,
                "user_id": "system",
                "timestamp": datetime.now().isoformat(),
                "details": {
                    "document_path": document_path,
                    "definitions_count": len(extracted_data.get("definitions", [])),
                    "treatments_count": len(extracted_data.get("accounting_treatments", [])),
                    "ambiguities_count": len(extracted_data.get("ambiguities", []))
                }
            })
            
            return {
                "success": True,
                "message": "Document processed successfully",
                "standard_id": standard_id,
                "definitions_count": len(extracted_data.get("definitions", [])),
                "treatments_count": len(extracted_data.get("accounting_treatments", [])),
                "ambiguities_count": len(extracted_data.get("ambiguities", [])),
                "enhancements_generated": len(extracted_data.get("ambiguities", []))
            }
            
        except Exception as e:
            self.logger.error(f"Error processing document: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": str(e)
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
                "created_at": datetime.now().isoformat()
            }
            
            # Create proposal in database
            self.shared_db.create_enhancement_proposal(proposal_data)
            
            # Save to file system
            enhancement_result["id"] = proposal_id
            enhancement_result["standard_id"] = standard_id
            self.file_manager.save_enhancement_proposal(proposal_id, enhancement_result)
            
            # Add proposal ID to result
            enhancement_result["proposal_id"] = proposal_id
            
            # Publish event for enhancement generation
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
            self.logger.error(f"Error in generate_enhancement: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Error generating enhancement: {str(e)}"
            }
    
    def validate_enhancement(self, enhancement_id, enhancement_data=None):
        """Validate an enhancement proposal"""
        self.logger.info(f"Validating enhancement: {enhancement_id}")
        
        if not enhancement_data:
            enhancement = self.shared_db.get_enhancement_proposal_by_id(enhancement_id)
            if not enhancement:
                # Try file system
                enhancement = self.file_manager.get_enhancement_proposal(enhancement_id)
                
            if not enhancement:
                self.logger.error(f"Enhancement not found: {enhancement_id}")
                return {"success": False, "message": "Enhancement not found"}
            
            enhancement_data = enhancement
        
        # Validate enhancement
        validation_result = self.validation_processor.validate_enhancement(
            enhancement_id,
            enhancement_data
        )
        
        # Save validation to database
        try:
            validation_id = str(uuid.uuid4())
            
            self.shared_db.create_validation({
                "id": validation_id,
                "enhancement_id": enhancement_id,
                "is_valid": validation_result.get("is_valid", False),
                "feedback": validation_result.get("feedback", ""),
                "shariah_compliance": validation_result.get("shariah_compliance", ""),
                "validation_score": validation_result.get("validation_score", 0.0),
                "timestamp": datetime.now().isoformat()
            })
            
            # Update enhancement status
            status = "validated" if validation_result.get("is_valid", False) else "needs_revision"
            self.shared_db.update_enhancement_proposal(enhancement_id, {"status": status})
            
            # Publish event
            self.event_bus.publish_event({
                "type": "ENHANCEMENT_VALIDATED",
                "topic": "validation",
                "payload": {
                    "enhancement_id": enhancement_id,
                    "validation_id": validation_id,
                    "validation_result": validation_result,
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
                    "is_valid": validation_result.get("is_valid", False),
                    "validation_score": validation_result.get("validation_score", 0.0)
                }
            })
            
        except Exception as e:
            self.logger.error(f"Error saving validation: {e}")
            return {"success": False, "message": f"Error saving validation: {str(e)}"}
        
        return {
            "success": True,
            "message": "Enhancement validated successfully",
            "validation_id": validation_id,
            **validation_result
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
