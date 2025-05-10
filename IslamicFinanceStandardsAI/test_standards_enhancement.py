#!/usr/bin/env python3
"""
Standards Enhancement Subsystem Test

This script tests the Standards Enhancement subsystem of the Islamic Finance Standards AI system,
focusing on the specific components described in the architecture document:
1. Document parsing and ambiguity extraction
2. Chain-of-thought enhancement generation
3. Validation against Shariah principles
4. Immutable logging of changes

The test simulates the event-driven architecture described in the full system design.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import system components
from database.mock_knowledge_graph import MockKnowledgeGraph
from agents.document_agent.document_agent import DocumentAgent
from agents.enhancement_agent.enhancement_agent import EnhancementAgent
from agents.validation_agent.validation_agent import ValidationAgent
from models.enhancement_schema import EnhancementProposal, EnhancementType
from models.validation_schema import ValidationResult, ValidationStatus
from test_multi_agent_workflow import AgentCoordinator, Event, EventTopics, EventBus

# Configure logging
log_file = f"standards_enhancement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create a separate event logger for tracking agent interactions
event_log_file = f"enhancement_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
event_logger = logging.getLogger("enhancement_events")
event_logger.setLevel(logging.INFO)
event_handler = logging.FileHandler(event_log_file)
event_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
event_logger.addHandler(event_handler)

class AuditLogger:
    """
    Simulates the Hyperledger Fabric immutable audit log for standards enhancements
    """
    def __init__(self):
        self.audit_log = []
        self.log_file = f"audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
    def log_event(self, event_type: str, data: Dict, metadata: Optional[Dict] = None):
        """Log an event to the audit trail"""
        entry = {
            "id": f"{event_type}-{int(time.time() * 1000)}",
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data,
            "metadata": metadata or {}
        }
        self.audit_log.append(entry)
        
        # Write to file immediately for persistence
        with open(self.log_file, "w") as f:
            json.dump(self.audit_log, f, indent=2, default=str)
        
        logger.info(f"Audit log entry created: {event_type}")
        
    def get_audit_trail(self):
        """Get the full audit trail"""
        return self.audit_log

class StandardsEnhancementCoordinator(AgentCoordinator):
    """
    Specialized coordinator for the Standards Enhancement subsystem
    """
    def __init__(self):
        super().__init__()
        self.audit_logger = AuditLogger()
        
        # Subscribe to additional events for audit logging
        self.event_bus.subscribe(EventTopics.DOCUMENT_PROCESSED, self._audit_document_processed)
        self.event_bus.subscribe(EventTopics.ENHANCEMENT_PROPOSED, self._audit_enhancement_proposed)
        self.event_bus.subscribe(EventTopics.VALIDATION_COMPLETED, self._audit_validation_completed)
    
    def _audit_document_processed(self, event: Event):
        """Audit log document processing"""
        self.audit_logger.log_event(
            event_type="DOCUMENT_PROCESSED",
            data={
                "standard_id": event.data["standard_id"],
                "standard_info": event.data["standard_info"],
                "file_path": event.data["file_path"]
            },
            metadata={
                "agent": "document_agent",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def _audit_enhancement_proposed(self, event: Event):
        """Audit log enhancement proposals"""
        self.audit_logger.log_event(
            event_type="ENHANCEMENT_PROPOSED",
            data={
                "standard_id": event.data["standard_id"],
                "proposal_ids": event.data["proposal_ids"],
                "proposal_count": event.data["proposal_count"]
            },
            metadata={
                "agent": "enhancement_agent",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def _audit_validation_completed(self, event: Event):
        """Audit log validation results"""
        self.audit_logger.log_event(
            event_type="VALIDATION_COMPLETED",
            data={
                "standard_id": event.data["standard_id"],
                "validation_results": event.data["validation_results"],
                "validation_count": event.data["validation_count"]
            },
            metadata={
                "agent": "validation_agent",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def process_ambiguity_flag(self, standard_id: str, ambiguity_text: str, confidence_score: float):
        """
        Process an ambiguity flag from the Reverse Transactions layer
        
        This simulates receiving an ambiguity flag from the Reverse Transactions layer,
        which would trigger a targeted review of the corresponding standard.
        """
        logger.info(f"Processing ambiguity flag for standard ID: {standard_id}")
        
        # Get standard info
        standard_info = self.knowledge_graph.get_node_by_id(standard_id)
        if not standard_info:
            raise ValueError(f"Standard with ID {standard_id} not found")
        
        # Create ambiguity node
        ambiguity_id = self.knowledge_graph.create_node(
            label="Ambiguity",
            properties={
                "text": ambiguity_text,
                "context": f"Flagged by Reverse Transactions with confidence score: {confidence_score}",
                "indicator": "LOW_CONFIDENCE"
            }
        )
        
        # Link ambiguity to standard
        self.knowledge_graph.create_relationship(
            start_node_id=standard_id,
            end_node_id=ambiguity_id,
            relationship_type="HAS_AMBIGUITY"
        )
        
        # Audit log the ambiguity flag
        self.audit_logger.log_event(
            event_type="AMBIGUITY_FLAGGED",
            data={
                "standard_id": standard_id,
                "ambiguity_id": ambiguity_id,
                "ambiguity_text": ambiguity_text,
                "confidence_score": confidence_score
            },
            metadata={
                "source": "reverse_transactions",
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Publish event to trigger enhancement generation
        event = Event(
            topic=EventTopics.DOCUMENT_PROCESSED,
            data={
                "standard_id": standard_id,
                "standard_info": {
                    "id": standard_id,
                    "title": standard_info["properties"]["title"],
                    "standard_type": standard_info["properties"]["standard_type"],
                    "standard_number": standard_info["properties"]["standard_number"],
                    "ambiguities_count": 1
                },
                "file_path": None  # No file path since we're processing an existing standard
            },
            metadata={
                "source": "reverse_transactions",
                "timestamp": datetime.now().isoformat()
            }
        )
        self.event_bus.publish(event)
        
        return ambiguity_id

def generate_enhancement_report(coordinator):
    """Generate a detailed report of the standards enhancement process"""
    report = []
    report.append("\n" + "=" * 80)
    report.append("ISLAMIC FINANCE STANDARDS ENHANCEMENT REPORT")
    report.append("=" * 80)
    
    # Summary statistics
    report.append(f"\nSUMMARY STATISTICS:")
    report.append(f"Standards processed: {len(coordinator.processed_standards)}")
    report.append(f"Enhancements generated: {len(coordinator.enhancement_proposals)}")
    report.append(f"Validation results: {len(coordinator.validation_results)}")
    
    # Validation status breakdown
    status_counts = {}
    for result in coordinator.validation_results:
        status = result.status.value
        status_counts[status] = status_counts.get(status, 0) + 1
    
    report.append("\nVALIDATION RESULTS:")
    for status, count in status_counts.items():
        report.append(f"  {status}: {count}")
    
    # Enhancement details by type
    report.append("\nENHANCEMENT TYPES:")
    enhancement_types = {}
    for proposal in coordinator.enhancement_proposals:
        enhancement_types[proposal.enhancement_type] = enhancement_types.get(proposal.enhancement_type, 0) + 1
    
    for etype, count in enhancement_types.items():
        report.append(f"  {etype}: {count}")
    
    # Audit log statistics
    audit_counts = {}
    for entry in coordinator.audit_logger.audit_log:
        event_type = entry["event_type"]
        audit_counts[event_type] = audit_counts.get(event_type, 0) + 1
    
    report.append("\nAUDIT LOG STATISTICS:")
    for event_type, count in audit_counts.items():
        report.append(f"  {event_type}: {count}")
    
    report.append("\n" + "=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80 + "\n")
    
    return "\n".join(report)

def test_standards_enhancement(document_paths=None, timeout_seconds=300):
    """Test the standards enhancement subsystem"""
    logger.info("Starting standards enhancement subsystem test")
    
    # Default sample documents to process if none provided
    if document_paths is None:
        document_paths = [
            "/Users/faycalamrouche/Desktop/IsDBI/Resources/FI5F55_1_Musharaka Financing(4).PDF"
        ]
    
    # Create standards enhancement coordinator
    coordinator = StandardsEnhancementCoordinator()
    
    # Process documents to extract standards
    for document_path in document_paths:
        coordinator.process_document(document_path)
    
    # Wait for initial processing to complete
    time.sleep(5)
    
    # Simulate receiving ambiguity flags from Reverse Transactions layer
    if coordinator.processed_standards:
        standard_id = coordinator.processed_standards[0]["id"]
        
        # Simulate multiple ambiguity flags
        ambiguity_flags = [
            {
                "text": "Unclear profit distribution mechanism in Musharaka",
                "confidence_score": 0.35
            },
            {
                "text": "Ambiguous termination conditions for diminishing Musharaka",
                "confidence_score": 0.42
            }
        ]
        
        for flag in ambiguity_flags:
            coordinator.process_ambiguity_flag(
                standard_id=standard_id,
                ambiguity_text=flag["text"],
                confidence_score=flag["confidence_score"]
            )
    
    # Wait for workflow completion
    start_time = time.time()
    while True:
        time.sleep(1)
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            logger.warning(f"Workflow timeout after {timeout_seconds} seconds")
            break
        
        # Check if we have validation results for all standards and ambiguities
        if (len(coordinator.validation_results) >= 
            len(coordinator.processed_standards) + len(coordinator.enhancement_proposals)):
            logger.info("All standards and ambiguities processed")
            break
    
    # Generate and log report
    report = generate_enhancement_report(coordinator)
    logger.info(report)
    print(report)
    
    # Save event log to file
    event_log_path = f"enhancement_event_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(event_log_path, "w") as f:
        json.dump(coordinator.event_bus.event_log, f, indent=2, default=str)
    
    logger.info(f"Event log saved to {event_log_path}")
    logger.info("Standards enhancement test completed successfully")
    
    return coordinator

def check_environment():
    """Check that required environment variables are set"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\nERROR: OpenAI API key not found!")
        print("Please set your OpenAI API key in the .env file.")
        print("Example: OPENAI_API_KEY=sk-your-actual-api-key\n")
        return False
    
    return True

if __name__ == "__main__":
    if check_environment():
        # Parse command line arguments
        import argparse
        parser = argparse.ArgumentParser(description="Test the Standards Enhancement subsystem")
        parser.add_argument("--document", "-d", type=str, help="Path to document to process", action="append")
        parser.add_argument("--timeout", "-t", type=int, default=300, help="Timeout in seconds for workflow completion")
        args = parser.parse_args()
        
        # Run the test
        test_standards_enhancement(document_paths=args.document, timeout_seconds=args.timeout)
    else:
        print("Environment setup incomplete. Please fix the issues above and try again.")
