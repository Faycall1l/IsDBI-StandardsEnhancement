#!/usr/bin/env python3
"""
Production-Ready System Test for Islamic Finance Standards Enhancement Pipeline

This script provides a comprehensive test suite for the Islamic Finance Standards
Enhancement system, ensuring all components function correctly in a production environment.
It includes robust error handling, performance monitoring, and detailed reporting.
"""

import os
import sys
import json
import time
import logging
import argparse
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import system components
from database.mock_knowledge_graph import MockKnowledgeGraph
from database.knowledge_graph import KnowledgeGraph
import neo4j
from agents.document_agent.document_agent import DocumentAgent
from agents.enhancement_agent.enhancement_agent import EnhancementAgent
from agents.validation_agent.validation_agent import ValidationAgent
from utils.enhanced_audit_logger import get_audit_logger
from utils.resilience import retry, CircuitBreaker, fallback, capture_exception
from utils.monitoring import metrics, performance_monitor, health_check, get_system_status
from extract_enhancements import extract_enhancements_from_logs, display_enhancements
from config.production import (
    LOGGING_CONFIG, 
    NEO4J_CONFIG, 
    DOCUMENT_PROCESSING_CONFIG,
    ENHANCEMENT_CONFIG,
    VALIDATION_CONFIG
)

# Configure logging with rotation
import logging.handlers
log_dir = LOGGING_CONFIG.get("file_path", "logs/")
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, "production_test_system.log")
log_level = getattr(logging, LOGGING_CONFIG.get("level", "INFO"))

logger = logging.getLogger()
logger.setLevel(log_level)

# Add rotating file handler
if LOGGING_CONFIG.get("rotate_logs", True):
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOGGING_CONFIG.get("max_log_size", 10 * 1024 * 1024),
        backupCount=LOGGING_CONFIG.get("backup_count", 5)
    )
else:
    file_handler = logging.FileHandler(log_file)

file_handler.setFormatter(logging.Formatter(LOGGING_CONFIG.get("format")))
logger.addHandler(file_handler)

# Add console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(LOGGING_CONFIG.get("format")))
logger.addHandler(console_handler)

# Initialize audit logger
audit_logger = get_audit_logger()

def get_knowledge_graph():
    """
    Get a knowledge graph instance with robust error handling
    
    Returns:
        KnowledgeGraph instance or MockKnowledgeGraph if connection fails
    """
    try:
        logger.info("Attempting to connect to Neo4j knowledge graph")
        # Try to create a connection with a short timeout
        kg = KnowledgeGraph()
        # Test the connection with a simple query to verify it works
        try:
            # Try a simple query to verify connection
            kg.run_query("MATCH (n) RETURN count(n) as count LIMIT 1")
            logger.info("Successfully connected to Neo4j knowledge graph")
            return kg
        except Exception as e:
            logger.warning(f"Neo4j query test failed: {str(e)}")
            raise
    except Exception as e:
        logger.warning(f"Neo4j connection failed: {str(e)}")
        logger.info("Falling back to MockKnowledgeGraph")
        mock_kg = MockKnowledgeGraph()
        logger.info("MockKnowledgeGraph initialized successfully")
        return mock_kg

class ProductionSystemTestSuite:
    """Comprehensive test suite for the Islamic Finance Standards Enhancement system"""
    
    def __init__(self, config=None):
        """
        Initialize the production test suite
        
        Args:
            config: Optional configuration dictionary
        """
        self.start_time = datetime.now()
        self.config = config or {}
        
        logger.info("Initializing Production System Test Suite")
        
        # Initialize knowledge graph with resilience
        self.knowledge_graph = get_knowledge_graph()
        
        # Initialize agents
        self.document_agent = DocumentAgent(self.knowledge_graph)
        self.enhancement_agent = EnhancementAgent(self.knowledge_graph)
        self.validation_agent = ValidationAgent(self.knowledge_graph)
        
        # Register health checks
        health_check.register_check(
            "knowledge_graph",
            lambda: self._check_knowledge_graph_health(),
            "Check if knowledge graph is responsive"
        )
        
        # Initialize test results
        self.test_results = {
            "start_time": self.start_time.isoformat(),
            "end_time": None,
            "duration_seconds": None,
            "overall_status": "pending",
            "components": {
                "document_agent": {"status": "pending", "details": {}},
                "enhancement_agent": {"status": "pending", "details": {}},
                "validation_agent": {"status": "pending", "details": {}},
                "knowledge_graph": {"status": "pending", "details": {}}
            },
            "metrics": {},
            "errors": []
        }
        
        # Log initialization
        audit_logger.log_event(
            event_type="TEST_SUITE_INITIALIZED",
            data={"config": self.config}
        )
    
    def _check_knowledge_graph_health(self) -> bool:
        """Check if the knowledge graph is healthy"""
        try:
            # Simple query to check if the graph is responsive
            if hasattr(self.knowledge_graph, 'run_query'):
                self.knowledge_graph.run_query("MATCH (n) RETURN count(n) as count LIMIT 1")
            return True
        except Exception:
            return False
    
    @performance_monitor.measure_execution_time(category="document_agent")
    @capture_exception
    def test_document_processing(self, sample_document_path):
        """
        Test document processing and data extraction
        
        Args:
            sample_document_path: Path to the sample document
            
        Returns:
            Extracted data from the document
        """
        logger.info(f"Testing document processing for {sample_document_path}")
        
        # Record test start
        component_result = self.test_results["components"]["document_agent"]
        component_result["start_time"] = datetime.now().isoformat()
        
        try:
            # Process document
            extracted_data = self.document_agent.process_document(sample_document_path)
            
            # Validate extraction
            assert extracted_data is not None, "Document processing failed"
            
            # Update test results
            component_result["status"] = "passed"
            component_result["details"] = {
                "document_path": sample_document_path,
                "extracted_data_type": type(extracted_data).__name__,
                "definitions_count": len(extracted_data.definitions),
                "accounting_treatments_count": len(extracted_data.accounting_treatments),
                "transaction_structures_count": len(extracted_data.transaction_structures),
                "ambiguities_count": len(extracted_data.ambiguities)
            }
            
            # Log success event
            audit_logger.log_event(
                event_type="DOCUMENT_PROCESSING_SUCCEEDED",
                data={
                    "document_path": sample_document_path,
                    "metadata": {
                        "title": extracted_data.title,
                        "standard_type": extracted_data.standard_type,
                        "standard_number": extracted_data.standard_number
                    }
                }
            )
            
            logger.info("Document processing successful")
            return extracted_data
            
        except Exception as e:
            # Update test results
            component_result["status"] = "failed"
            component_result["details"] = {
                "document_path": sample_document_path,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            
            # Log failure event
            audit_logger.log_event(
                event_type="DOCUMENT_PROCESSING_FAILED",
                data={
                    "document_path": sample_document_path,
                    "error": str(e)
                }
            )
            
            logger.error(f"Document processing test failed: {e}")
            logger.error(traceback.format_exc())
            raise
        finally:
            # Record test end time and duration
            component_result["end_time"] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(component_result["start_time"])
            end_time = datetime.fromisoformat(component_result["end_time"])
            component_result["duration_seconds"] = (end_time - start_time).total_seconds()
    
    @performance_monitor.measure_execution_time(category="enhancement_agent")
    @capture_exception
    def test_enhancement_generation(self, standard_id):
        """
        Test enhancement proposal generation
        
        Args:
            standard_id: ID of the standard to enhance
            
        Returns:
            List of enhancement proposals
        """
        logger.info(f"Generating enhancements for standard ID: {standard_id}")
        
        # Record test start
        component_result = self.test_results["components"]["enhancement_agent"]
        component_result["start_time"] = datetime.now().isoformat()
        
        try:
            # Generate enhancement proposals
            proposals = self.enhancement_agent.generate_enhancements(standard_id)
            
            # Validate proposals
            assert proposals, "No enhancement proposals generated"
            
            # Update test results
            component_result["status"] = "passed"
            component_result["details"] = {
                "standard_id": standard_id,
                "proposals_count": len(proposals),
                "proposal_types": [p.enhancement_type for p in proposals] if hasattr(proposals[0], 'enhancement_type') else []
            }
            
            # Log proposals
            audit_logger.log_event(
                event_type="ENHANCEMENT_PROPOSED",
                data={"proposals": proposals}
            )
            
            logger.info(f"Generated {len(proposals)} enhancement proposals")
            return proposals
            
        except Exception as e:
            # Update test results
            component_result["status"] = "failed"
            component_result["details"] = {
                "standard_id": standard_id,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            
            # Log failure event
            audit_logger.log_event(
                event_type="ENHANCEMENT_GENERATION_FAILED",
                data={
                    "standard_id": standard_id,
                    "error": str(e)
                }
            )
            
            logger.error(f"Enhancement generation test failed: {e}")
            logger.error(traceback.format_exc())
            raise
        finally:
            # Record test end time and duration
            component_result["end_time"] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(component_result["start_time"])
            end_time = datetime.fromisoformat(component_result["end_time"])
            component_result["duration_seconds"] = (end_time - start_time).total_seconds()
    
    @performance_monitor.measure_execution_time(category="validation_agent")
    @capture_exception
    def test_validation(self, proposals):
        """
        Test validation of enhancement proposals
        
        Args:
            proposals: List of proposals to validate
            
        Returns:
            List of validated proposals
        """
        logger.info("Validating enhancement proposals")
        
        # Record test start
        component_result = self.test_results["components"]["validation_agent"]
        component_result["start_time"] = datetime.now().isoformat()
        
        try:
            validated_proposals = []
            validation_statuses = {}
            
            for proposal in proposals:
                validation_result = self.validation_agent.validate_proposal(proposal)
                
                # Update proposal status based on validation
                proposal['validation_status'] = validation_result['status']
                validated_proposals.append(proposal)
                
                # Track validation statuses for reporting
                status = validation_result['status']
                validation_statuses[status] = validation_statuses.get(status, 0) + 1
                
                # Log validation results
                audit_logger.log_event(
                    event_type="ENHANCEMENT_VALIDATED",
                    data={
                        "proposal_id": proposal.get('id'),
                        "status": validation_result['status'],
                        "feedback": validation_result.get('feedback', '')
                    }
                )
            
            # Update test results
            component_result["status"] = "passed"
            component_result["details"] = {
                "proposals_count": len(proposals),
                "validation_statuses": validation_statuses
            }
            
            logger.info(f"Validated {len(validated_proposals)} proposals")
            return validated_proposals
            
        except Exception as e:
            # Update test results
            component_result["status"] = "failed"
            component_result["details"] = {
                "proposals_count": len(proposals) if proposals else 0,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            
            # Log failure event
            audit_logger.log_event(
                event_type="VALIDATION_FAILED",
                data={"error": str(e)}
            )
            
            logger.error(f"Enhancement validation test failed: {e}")
            logger.error(traceback.format_exc())
            raise
        finally:
            # Record test end time and duration
            component_result["end_time"] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(component_result["start_time"])
            end_time = datetime.fromisoformat(component_result["end_time"])
            component_result["duration_seconds"] = (end_time - start_time).total_seconds()
    
    @performance_monitor.measure_execution_time()
    @capture_exception
    def run_full_pipeline(self, sample_document_path, standard_id):
        """
        Run the complete enhancement pipeline
        
        Args:
            sample_document_path: Path to the sample document
            standard_id: ID of the standard to enhance
            
        Returns:
            List of validated proposals
        """
        logger.info("Starting full enhancement pipeline test")
        
        # Log test start
        audit_logger.log_event(
            event_type="FULL_PIPELINE_TEST_STARTED",
            data={
                "document_path": sample_document_path,
                "standard_id": standard_id
            }
        )
        
        # Comprehensive test workflow
        try:
            # 1. Process Document
            extracted_data = self.test_document_processing(sample_document_path)
            
            # 2. Generate Enhancements
            proposals = self.test_enhancement_generation(standard_id)
            
            # 3. Validate Proposals
            validated_proposals = self.test_validation(proposals)
            
            # 4. Extract and Display Enhancements
            event_proposals = extract_enhancements_from_logs()
            display_enhancements(event_proposals)
            
            # Update overall test results
            self.test_results["overall_status"] = "passed"
            
            # Log test completion
            audit_logger.log_event(
                event_type="FULL_PIPELINE_TEST_COMPLETED",
                data={
                    "document_path": sample_document_path,
                    "standard_id": standard_id,
                    "proposals_count": len(validated_proposals),
                    "status": "success"
                }
            )
            
            logger.info("Full enhancement pipeline test completed successfully")
            return validated_proposals
        
        except Exception as e:
            # Update overall test results
            self.test_results["overall_status"] = "failed"
            self.test_results["errors"].append({
                "phase": "full_pipeline",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            
            # Log test failure
            audit_logger.log_event(
                event_type="FULL_PIPELINE_TEST_FAILED",
                data={
                    "document_path": sample_document_path,
                    "standard_id": standard_id,
                    "error": str(e)
                }
            )
            
            logger.error(f"Full pipeline test failed: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def generate_test_report(self):
        """
        Generate a comprehensive test report
        
        Returns:
            Dictionary with test results and metrics
        """
        # Update end time and duration
        self.test_results["end_time"] = datetime.now().isoformat()
        self.test_results["duration_seconds"] = (
            datetime.fromisoformat(self.test_results["end_time"]) - 
            datetime.fromisoformat(self.test_results["start_time"])
        ).total_seconds()
        
        # Add system metrics
        self.test_results["metrics"] = {
            "system": metrics.get_all_metrics()["system"],
            "function_stats": performance_monitor.get_function_stats()
        }
        
        # Add health check results
        self.test_results["health_check"] = health_check.run_all_checks()
        
        # Log report generation
        audit_logger.log_event(
            event_type="TEST_REPORT_GENERATED",
            data={"test_results": self.test_results}
        )
        
        return self.test_results
    
    def save_test_report(self, filepath=None):
        """
        Save the test report to a file
        
        Args:
            filepath: Optional filepath, defaults to timestamped file in reports directory
            
        Returns:
            Path to the saved report file
        """
        if filepath is None:
            # Create reports directory if it doesn't exist
            reports_dir = "reports"
            os.makedirs(reports_dir, exist_ok=True)
            
            # Generate timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(reports_dir, f"test_report_{timestamp}.json")
        
        # Generate report
        report = self.generate_test_report()
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Test report saved to {filepath}")
        return filepath

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Production Test for Islamic Finance Standards Enhancement System")
    
    parser.add_argument(
        "--document", 
        type=str, 
        default=None,
        help="Path to the document to process"
    )
    
    parser.add_argument(
        "--standard-id", 
        type=str, 
        default=None,
        help="ID of the standard to enhance"
    )
    
    parser.add_argument(
        "--report-file", 
        type=str, 
        default=None,
        help="Path to save the test report"
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()

def main():
    """Main test function"""
    args = parse_args()
    
    # Set log level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info("Starting Islamic Finance Standards AI Production System Test")
    
    # Log system information
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Operating system: {os.name} - {sys.platform}")
    
    try:
        # Initialize test suite
        test_suite = ProductionSystemTestSuite()
        
        # Determine sample document path
        if args.document:
            sample_document = args.document
        else:
            sample_document = os.path.join(
                os.path.dirname(__file__), 
                'sample_documents', 
                'sample_standard.txt'
            )
        
        # Determine standard ID
        standard_id = args.standard_id or '0'
        
        # Run full pipeline test
        test_suite.run_full_pipeline(sample_document, standard_id)
        
        # Save test report
        report_path = test_suite.save_test_report(args.report_file)
        
        # Display success message
        logger.info(f"All tests completed successfully. Report saved to {report_path}")
        
        # Flush audit logs
        audit_logger.flush()
        
    except Exception as e:
        logger.error(f"System test failed: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
    finally:
        # Export metrics for analysis
        metrics_path = os.path.join("reports", f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
        with open(metrics_path, 'w') as f:
            json.dump(metrics.get_all_metrics(), f, indent=2)
        
        logger.info(f"Metrics exported to {metrics_path}")
        logger.info("Test script completed")

if __name__ == '__main__':
    main()
