#!/usr/bin/env python3
"""
Multi-Agent Workflow Test

This script demonstrates the full multi-agent workflow for the Islamic Finance Standards AI system:
1. Document Agent extracts information from standards
2. Enhancement Agent proposes improvements
3. Validation Agent reviews and approves/rejects enhancements
4. The agents communicate and iterate on enhancements

This test uses the mock knowledge graph to avoid Neo4j dependency and implements
event-based communication between agents to simulate the Kafka-based architecture.
"""

import os
import sys
import logging
import json
import time
import traceback
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

# Import the AuditLogger
from utils.audit_logger import AuditLogger

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import system components
from database.mock_knowledge_graph import MockKnowledgeGraph
from agents.document_agent.document_agent import DocumentAgent
from agents.enhancement_agent.enhancement_agent import EnhancementAgent
from agents.validation_agent.validation_agent import ValidationAgent
from models.enhancement_schema import EnhancementProposal, EnhancementType
from models.validation_schema import ValidationResult, ValidationStatus

# Configure logging with more detailed format
log_file = f"multi_agent_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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
event_log_file = f"agent_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
event_logger = logging.getLogger("agent_events")
event_logger.setLevel(logging.INFO)
event_handler = logging.FileHandler(event_log_file)
event_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
event_logger.addHandler(event_handler)

# Monkey patch the knowledge graph to use our mock implementation
import types
from database.knowledge_graph import KnowledgeGraph
original_init = KnowledgeGraph.__init__

def mock_init(self):
    """Mock initialization that doesn't require Neo4j"""
    self.logger = logging.getLogger(__name__)
    self.logger.info("Using mock knowledge graph implementation")
    
    # Use the mock implementation
    mock_kg = MockKnowledgeGraph()
    
    # Copy all attributes and methods from mock to self
    for attr_name in dir(mock_kg):
        if not attr_name.startswith('__'):
            attr = getattr(mock_kg, attr_name)
            if callable(attr):
                setattr(self, attr_name, types.MethodType(attr.__func__, self))
            else:
                setattr(self, attr_name, attr)

# Apply the monkey patch
KnowledgeGraph.__init__ = mock_init

# Event topics for agent communication (simulating Kafka topics)
class EventTopics:
    DOCUMENT_PROCESSED = "document-processed"
    ENHANCEMENT_PROPOSED = "enhancement-proposed"
    VALIDATION_COMPLETED = "validation-completed"
    WORKFLOW_COMPLETED = "workflow-completed"

class Event:
    """Represents an event in the system"""
    
    def __init__(self, topic: str, data: Dict, metadata: Optional[Dict] = None):
        self.id = f"{topic}-{int(time.time() * 1000)}"
        self.topic = topic
        self.timestamp = datetime.now().isoformat()
        self.data = data
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "topic": self.topic,
            "timestamp": self.timestamp,
            "data": self.data,
            "metadata": self.metadata
        }
    
    def __str__(self) -> str:
        return f"Event(id={self.id}, topic={self.topic})"

class EventBus:
    """Simple event bus to simulate Kafka for agent communication"""
    
    def __init__(self):
        self.subscribers = {}
        self.event_log = []
    
    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers of its topic"""
        event_logger.info(f"PUBLISH: {event.topic} - {json.dumps(event.data, default=str)[:200]}...")
        self.event_log.append(event.to_dict())
        
        if event.topic in self.subscribers:
            for callback in self.subscribers[event.topic]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in subscriber callback: {str(e)}")
                    logger.error(traceback.format_exc())
    
    def subscribe(self, topic: str, callback) -> None:
        """Subscribe to a topic with a callback function"""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
        event_logger.info(f"SUBSCRIBE: {topic}")
    
    def get_events(self, topic: Optional[str] = None) -> List[Dict]:
        """Get all events, optionally filtered by topic"""
        if topic:
            return [event for event in self.event_log if event["topic"] == topic]
        return self.event_log

class AgentCoordinator:
    """Coordinates the multi-agent workflow using event-driven architecture"""
    
    def __init__(self):
        """Initialize the agent coordinator"""
        self.logger = logging.getLogger(__name__)
        self.knowledge_graph = KnowledgeGraph()
        
        # Initialize event bus
        self.event_bus = EventBus()
        
        # Initialize agents
        self.document_agent = DocumentAgent(self.knowledge_graph)
        self.enhancement_agent = EnhancementAgent(self.knowledge_graph)
        self.validation_agent = ValidationAgent(self.knowledge_graph)
        
        # Workflow state
        self.processed_standards = []
        self.processed_standards_ids = []
        self.enhancement_proposals = []
        self.validation_results = []
        
        # Add a counter to prevent infinite loops
        self.max_iterations = 10
        self.current_iteration = 0
        
        # Initialize audit logger
        self.audit_logger = AuditLogger()
        
        # Configure event-based communication
        self._setup_event_subscriptions()
    
    def _setup_event_subscriptions(self):
        """Set up event subscriptions for inter-agent communication"""
        # Document agent produces events, doesn't consume any
        
        # Enhancement agent consumes document processed events
        self.event_bus.subscribe(
            EventTopics.DOCUMENT_PROCESSED,
            self._handle_document_processed
        )
        
        # Validation agent consumes enhancement proposed events
        self.event_bus.subscribe(
            EventTopics.ENHANCEMENT_PROPOSED,
            self._handle_enhancement_proposed
        )
        
        # Coordinator consumes validation completed events
        self.event_bus.subscribe(
            EventTopics.VALIDATION_COMPLETED,
            self._handle_validation_completed
        )
        
        self.logger.info("Event subscriptions established")
    
    def process_document(self, document_path: str) -> Dict:
        """Process a document with the document agent and publish an event"""
        self.logger.info(f"Processing document: {document_path}")
        
        try:
            # Document agent processes the document
            standard_doc = self.document_agent.process_document(document_path)
            
            # Find the standard in the knowledge graph
            standards = self.knowledge_graph.search_nodes(
                label="Standard",
                properties={
                    "title": standard_doc.title
                }
            )
            
            if not standards:
                raise ValueError(f"Standard not found in knowledge graph: {standard_doc.title}")
            
            standard_id = standards[0]["id"]
            standard_info = {
                "id": standard_id,
                "title": standard_doc.title,
                "standard_type": standard_doc.standard_type,
                "standard_number": standard_doc.standard_number,
                "definitions_count": len(standard_doc.definitions),
                "accounting_treatments_count": len(standard_doc.accounting_treatments),
                "transaction_structures_count": len(standard_doc.transaction_structures),
                "ambiguities_count": len(standard_doc.ambiguities)
            }
            
            self.processed_standards.append(standard_info)
            self.processed_standards_ids.append(standard_id)
            self.logger.info(f"Document processed: {standard_doc.title}")
            
            # Publish document processed event
            event = Event(
                topic=EventTopics.DOCUMENT_PROCESSED,
                data={
                    "standard_id": standard_id,
                    "standard_info": standard_info,
                    "file_path": document_path
                },
                metadata={
                    "agent": "document_agent",
                    "timestamp": datetime.now().isoformat()
                }
            )
            self.event_bus.publish(event)
            
            return standard_info
            
        except Exception as e:
            self.logger.error(f"Error processing document: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise
    
    def _handle_document_processed(self, event: Event) -> None:
        """Handle document processed event by generating enhancements"""
        self.logger.info(f"Handling document processed event: {event.id}")
        
        standard_id = event.data["standard_id"]
        standard_info = event.data["standard_info"]
        
        try:
            # Enhancement agent generates proposals asynchronously
            self.logger.info(f"Triggering enhancement generation for standard: {standard_info['title']}")
            self._generate_enhancements_async(standard_id, standard_info)
        except Exception as e:
            self.logger.error(f"Error handling document processed event: {str(e)}")
            self.logger.error(traceback.format_exc())
    
    def _generate_enhancements_async(self, standard_id: str, standard_info: Dict) -> None:
        """Generate enhancements asynchronously and publish an event"""
        try:
            # Enhancement agent generates proposals
            proposals = self.enhancement_agent.generate_enhancements(standard_id)
            
            # Log the proposals
            self.logger.info(f"Generated {len(proposals)} enhancement proposals for {standard_info['title']}")
            
            self.enhancement_proposals.extend(proposals)
            
            # Find proposal IDs in the knowledge graph
            proposal_ids = []
            for proposal in proposals:
                # Search for the proposal
                found_proposals = self.knowledge_graph.search_nodes(
                    label="EnhancementProposal",
                    properties={
                        "standard_id": standard_id,
                        "enhancement_type": proposal.enhancement_type
                    }
                )
                
                if found_proposals:
                    proposal_ids.append(found_proposals[0]["id"])
            
            # Publish enhancement proposed event
            event = Event(
                topic=EventTopics.ENHANCEMENT_PROPOSED,
                data={
                    "standard_id": standard_id,
                    "standard_info": standard_info,
                    "proposal_ids": proposal_ids,
                    "proposal_count": len(proposals)
                },
                metadata={
                    "agent": "enhancement_agent",
                    "timestamp": datetime.now().isoformat()
                }
            )
            self.event_bus.publish(event)
            
        except Exception as e:
            self.logger.error(f"Error generating enhancements: {str(e)}")
            self.logger.error(traceback.format_exc())
    
    def _handle_enhancement_proposed(self, event: Event) -> None:
        """Handle enhancement proposed event by validating proposals"""
        self.logger.info(f"Handling enhancement proposed event: {event.id}")
        
        standard_id = event.data["standard_id"]
        standard_info = event.data["standard_info"]
        proposal_ids = event.data["proposal_ids"]
        
        try:
            # Validation agent validates proposals asynchronously
            self.logger.info(f"Triggering validation for {len(proposal_ids)} proposals")
            self._validate_proposals_async(standard_id, standard_info, proposal_ids)
        except Exception as e:
            self.logger.error(f"Error handling enhancement proposed event: {str(e)}")
            self.logger.error(traceback.format_exc())
    
    def _validate_proposals_async(self, standard_id: str, standard_info: Dict, proposal_ids: List[str]) -> None:
        """Validate proposals asynchronously and publish an event"""
        try:
            validation_results = []
            
            for proposal_id in proposal_ids:
                # Validation agent validates the proposal
                result = self.validation_agent.validate_proposal(proposal_id)
                validation_results.append(result)
                
                # Log the validation result
                self.logger.info(f"Validation result for proposal {proposal_id}: {result.status.value} (score: {result.overall_score:.2f})")
            
            self.validation_results.extend(validation_results)
            
            # Publish validation completed event
            event = Event(
                topic=EventTopics.VALIDATION_COMPLETED,
                data={
                    "standard_id": standard_id,
                    "standard_info": standard_info,
                    "validation_results": [
                        {
                            "proposal_id": result.proposal_id,
                            "status": result.status.value,
                            "overall_score": result.overall_score,
                            "has_modified_content": bool(result.modified_content)
                        }
                        for result in validation_results
                    ],
                    "validation_count": len(validation_results)
                },
                metadata={
                    "agent": "validation_agent",
                    "timestamp": datetime.now().isoformat()
                }
            )
            self.event_bus.publish(event)
            
            # Only simulate ambiguity flag once per standard and only if we haven't reached max iterations
            if standard_id in self.processed_standards_ids and self.current_iteration < self.max_iterations:
                # Create the ambiguity node but don't trigger a new document processing event
                self.process_ambiguity_flag(
                    standard_id=standard_id,
                    ambiguity_text="Ambiguity in profit distribution mechanism for diminishing Musharaka",
                    confidence_score=0.85
                )
                
                # After processing all standards and validations, publish workflow completed
                if len(self.validation_results) >= len(self.processed_standards):
                    self._publish_workflow_completed_event()
            
        except Exception as e:
            self.logger.error(f"Error validating proposals: {str(e)}")
            self.logger.error(traceback.format_exc())
            
            # Publish workflow completed event to avoid hanging
            self._publish_workflow_completed_event()
    
    def _handle_validation_completed(self, event: Event) -> None:
        """Handle validation completed event"""
        self.logger.info(f"Handling validation completed event: {event.id}")
        
        standard_id = event.data["standard_id"]
        standard_info = event.data["standard_info"]
        validation_results = event.data["validation_results"]
        
        # Log summary of validation results
        status_counts = {}
        for result in validation_results:
            status = result["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        self.logger.info(f"Validation completed for standard {standard_info['title']}")
        self.logger.info(f"Validation results: {json.dumps(status_counts)}")
        
        # If this was the last standard to process, publish workflow completed event
        if len(self.processed_standards) == len(self.validation_results):
            self._publish_workflow_completed_event()
    
    def _publish_workflow_completed_event(self):
        """Publish workflow completed event"""
        self.logger.info("Publishing workflow completed event")
        
        event = Event(
            topic=EventTopics.WORKFLOW_COMPLETED,
            data={
                "standards_processed": len(self.processed_standards),
                "enhancements_generated": len(self.enhancement_proposals),
                "validation_results": [
                    {
                        "standard_id": result.standard_id,
                        "status": result.status.value,
                        "overall_score": result.overall_score,
                        "has_modified_content": bool(result.modified_content)
                    }
                    for result in self.validation_results
                ]
            },
            metadata={
                "agent": "coordinator",
                "timestamp": datetime.now().isoformat()
            }
        )
        self.event_bus.publish(event)
    
    def process_ambiguity_flag(self, standard_id: str, ambiguity_text: str, confidence_score: float):
        """Process an ambiguity flag from the Reverse Transactions layer"""
        self.logger.info(f"Processing ambiguity flag for standard ID: {standard_id}")
        
        # Create ambiguity node in knowledge graph
        ambiguity_id = self.knowledge_graph.create_ambiguity_node(
            standard_id=standard_id,
            text=ambiguity_text,
            confidence_score=confidence_score,
            source="reverse_transactions"
        )
        
        # Log to audit trail
        self.audit_logger.log_event(
            event_type="AMBIGUITY_FLAGGED",
            data={
                "standard_id": standard_id,
                "ambiguity_id": ambiguity_id,
                "confidence_score": confidence_score
            }
        )
        
        # Instead of publishing a document-processed event (which would trigger the whole workflow again),
        # just log that we received the ambiguity flag
        self.logger.info(f"Ambiguity flag processed for standard ID: {standard_id}")
        
        # In a real implementation, we might want to trigger a targeted enhancement just for this ambiguity,
        # but for testing purposes, we'll skip to avoid infinite loops
        
    def analyze_workflow_results(self):
        """Analyze the results of the multi-agent workflow"""
        self.logger.info("Analyzing multi-agent workflow results")
        
        # Count approved, approved with modifications, and rejected proposals
        status_counts = {
            "APPROVED": 0,
            "APPROVED_WITH_MODIFICATIONS": 0,
            "REJECTED": 0
        }
        
        for result in self.validation_results:
            status_counts[result.status.value] = status_counts.get(result.status.value, 0) + 1
        
        # Analyze the collaboration patterns
        self.logger.info(f"Multi-agent workflow completed with the following results:")
        self.logger.info(f"Processed {len(self.processed_standards)} standards")
        self.logger.info(f"Generated {len(self.enhancement_proposals)} enhancement proposals")
        self.logger.info(f"Validation results: {json.dumps(status_counts)}")
        
        return {
            "standards_processed": len(self.processed_standards),
            "enhancements_generated": len(self.enhancement_proposals),
            "validation_results": status_counts
        }
    
    def run_full_workflow(self, document_paths: List[str], wait_for_completion: bool = True, timeout_seconds: int = 300):
        """Run the full multi-agent workflow on multiple documents using event-driven architecture"""
        self.logger.info("Starting full multi-agent workflow with event-driven architecture")
        
        try:
            # Add a counter to prevent infinite loops
            self.max_iterations = 10
            self.current_iteration = 0
            
            # Subscribe to workflow completed event if waiting for completion
            if wait_for_completion:
                workflow_completed = False
                
                def on_workflow_completed(event):
                    nonlocal workflow_completed
                    self.logger.info("Workflow completed event received")
                    workflow_completed = True
                
                self.event_bus.subscribe(EventTopics.WORKFLOW_COMPLETED, on_workflow_completed)
            
            # Step 1: Process documents (this will trigger the entire event chain)
            for document_path in document_paths:
                self.process_document(document_path)
            
            # Wait for workflow completion if requested
            if wait_for_completion:
                start_time = time.time()
                while not workflow_completed:
                    time.sleep(1)
                    elapsed = time.time() - start_time
                    
                    # Check for timeout
                    if elapsed > timeout_seconds:
                        self.logger.warning(f"Workflow timeout after {timeout_seconds} seconds")
                        break
                    
                    # Check if we have validation results for all standards
                    if len(self.validation_results) >= len(self.processed_standards):
                        self.logger.info("All standards processed and validated")
                        # Force workflow completion
                        self._publish_workflow_completed_event()
                        workflow_completed = True
                        break
                    
                    # Check if we've exceeded the maximum number of iterations
                    if self.current_iteration >= self.max_iterations:
                        self.logger.warning(f"Maximum iterations ({self.max_iterations}) reached. Forcing workflow completion.")
                        self._publish_workflow_completed_event()
                        workflow_completed = True
                        break
            
            # Analyze and return results
            results = self.analyze_workflow_results()
            return results
            
        except Exception as e:
            self.logger.error(f"Workflow failed: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise
        finally:
            # Close knowledge graph connection
            self.knowledge_graph.close()

def generate_results_report(coordinator, results):
    """Generate a detailed report of the workflow results"""
    report = []
    report.append("\n" + "=" * 80)
    report.append("ISLAMIC FINANCE STANDARDS AI - MULTI-AGENT WORKFLOW REPORT")
    report.append("=" * 80)
    
    # Summary statistics
    report.append(f"\nSUMMARY STATISTICS:")
    report.append(f"Documents processed: {len(coordinator.processed_standards)}")
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
    
    # Document details
    report.append("\nDOCUMENT DETAILS:")
    for doc in coordinator.processed_standards:
        report.append(f"\n  Standard: {doc['title']}")
        report.append(f"  Type: {doc['standard_type']}")
        report.append(f"  Number: {doc['standard_number']}")
        report.append(f"  Definitions: {doc.get('definitions_count', 0)}")
        report.append(f"  Accounting Treatments: {doc.get('accounting_treatments_count', 0)}")
        report.append(f"  Transaction Structures: {doc.get('transaction_structures_count', 0)}")
        report.append(f"  Ambiguities: {doc.get('ambiguities_count', 0)}")
    
    # Enhancement details
    report.append("\nENHANCEMENT DETAILS:")
    enhancement_types = {}
    for proposal in coordinator.enhancement_proposals:
        enhancement_types[proposal.enhancement_type] = enhancement_types.get(proposal.enhancement_type, 0) + 1
    
    for etype, count in enhancement_types.items():
        report.append(f"  {etype}: {count}")
    
    # Event statistics
    event_counts = {}
    for event in coordinator.event_bus.event_log:
        topic = event["topic"]
        event_counts[topic] = event_counts.get(topic, 0) + 1
    
    report.append("\nEVENT STATISTICS:")
    for topic, count in event_counts.items():
        report.append(f"  {topic}: {count}")
    
    report.append("\n" + "=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80 + "\n")
    
    return "\n".join(report)

def test_multi_agent_workflow(document_paths=None, timeout_seconds=120):
    """Test the multi-agent workflow with sample documents"""
    logger.info("Starting multi-agent workflow test with event-driven architecture")
    
    # Default sample documents to process if none provided
    if document_paths is None:
        document_paths = [
            "/Users/faycalamrouche/Desktop/IsDBI/Resources/FI5F55_1_Musharaka Financing(4).PDF"
        ]
    
    # Create agent coordinator
    coordinator = AgentCoordinator()
    
    # Run the full workflow with event-driven architecture
    # Reduced timeout to prevent long-running tests
    results = coordinator.run_full_workflow(document_paths, wait_for_completion=True, timeout_seconds=timeout_seconds)
    
    # Generate and log detailed report
    report = generate_results_report(coordinator, results)
    logger.info(report)
    print(report)
    
    # Save event log to file
    event_log_path = f"event_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(event_log_path, "w") as f:
        json.dump(coordinator.event_bus.event_log, f, indent=2, default=str)
    
    logger.info(f"Event log saved to {event_log_path}")
    logger.info("Multi-agent workflow test completed successfully")
    
    return results, coordinator

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
        parser = argparse.ArgumentParser(description="Test the multi-agent workflow for Islamic Finance Standards AI")
        parser.add_argument("--document", "-d", type=str, help="Path to document to process", action="append")
        parser.add_argument("--timeout", "-t", type=int, default=300, help="Timeout in seconds for workflow completion")
        args = parser.parse_args()
        
        # Run the test
        test_multi_agent_workflow(document_paths=args.document, timeout_seconds=args.timeout)
    else:
        print("Environment setup incomplete. Please fix the issues above and try again.")
