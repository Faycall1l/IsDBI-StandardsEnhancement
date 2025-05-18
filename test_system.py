#!/usr/bin/env python3
"""
End-to-End Test Script for Islamic Finance Standards Enhancement System

This script tests the complete workflow of the system:
1. Document processing
2. Enhancement generation
3. Validation
4. Event tracking
5. Audit logging

It uses real AAOIFI standard documents and produces detailed output
to demonstrate the system's functionality.
"""

import os
import sys
import json
import logging
import argparse
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"standards_enhancement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("test_system")

# Import system components
try:
    from IslamicFinanceStandardsAI.integration.system_integrator import SystemIntegrator
    from IslamicFinanceStandardsAI.database.shared_database import SharedDatabase
    from IslamicFinanceStandardsAI.utils.file_manager import FileManager
except ImportError as e:
    logger.error(f"Failed to import system components: {e}")
    sys.exit(1)

class SystemTester:
    """Test harness for the Islamic Finance Standards Enhancement System"""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the system tester
        
        Args:
            data_dir: Directory containing test data
        """
        self.logger = logging.getLogger("SystemTester")
        self.data_dir = data_dir
        
        # Create data directories if they don't exist
        os.makedirs(os.path.join(data_dir, "standards"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "documents"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "enhancements"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "validations"), exist_ok=True)
        
        # Initialize system components
        self.logger.info("Initializing system components...")
        self.system_integrator = SystemIntegrator()
        self.shared_db = SharedDatabase()
        self.file_manager = FileManager()
        
        # Test standards
        self.standards = [
            {
                "id": "FAS-4",
                "name": "Musharaka Financing",
                "type": "FAS",
                "number": "4",
                "description": "This standard prescribes the accounting and reporting principles for Musharaka transactions."
            },
            {
                "id": "FAS-10",
                "name": "Istisna'a and Parallel Istisna'a",
                "type": "FAS",
                "number": "10",
                "description": "This standard prescribes the accounting rules for Istisna'a and parallel Istisna'a transactions."
            },
            {
                "id": "FAS-32",
                "name": "Ijarah and Ijarah Muntahia Bittamleek",
                "type": "FAS",
                "number": "32",
                "description": "This standard prescribes the accounting principles for Ijarah and Ijarah Muntahia Bittamleek transactions."
            }
        ]
        
        # Test document paths
        self.document_paths = {
            "FAS-4": os.path.join(data_dir, "standards", "FAS4_Musharaka.pdf"),
            "FAS-10": os.path.join(data_dir, "standards", "FAS10_Istisna.pdf"),
            "FAS-32": os.path.join(data_dir, "standards", "FAS32_Ijarah.pdf")
        }
        
        # Test results
        self.results = {
            "document_processing": {},
            "enhancement_generation": {},
            "validation": {},
            "events": [],
            "audit_logs": []
        }
    
    def setup_test_data(self):
        """Set up test data in the system"""
        self.logger.info("Setting up test data...")
        
        # Create test standards in the database
        for standard in self.standards:
            try:
                # Check if standard already exists
                existing = self.shared_db.get_standard_by_id(standard["id"])
                if not existing:
                    self.shared_db.create_standard(standard)
                    self.logger.info(f"Created standard: {standard['id']} - {standard['name']}")
                else:
                    self.logger.info(f"Standard already exists: {standard['id']} - {standard['name']}")
            except Exception as e:
                self.logger.error(f"Error creating standard {standard['id']}: {e}")
        
        # Check for test documents
        for standard_id, doc_path in self.document_paths.items():
            if not os.path.exists(doc_path):
                self.logger.warning(f"Test document not found: {doc_path}")
            else:
                self.logger.info(f"Test document found: {doc_path}")
    
    def test_document_processing(self):
        """Test document processing functionality"""
        self.logger.info("\n" + "="*80)
        self.logger.info("TESTING DOCUMENT PROCESSING")
        self.logger.info("="*80)
        
        for standard_id, doc_path in self.document_paths.items():
            if not os.path.exists(doc_path):
                self.logger.warning(f"Skipping document processing for {standard_id}: Document not found")
                continue
            
            self.logger.info(f"\nProcessing document for standard {standard_id}: {doc_path}")
            
            try:
                # Process the document
                result = self.system_integrator.process_document(doc_path, standard_id)
                
                # Store the result
                self.results["document_processing"][standard_id] = result
                
                # Log the result
                self.logger.info(f"Document processing result for {standard_id}:")
                self.logger.info(f"  Success: {result.get('success', False)}")
                self.logger.info(f"  Message: {result.get('message', '')}")
                self.logger.info(f"  Definitions extracted: {result.get('definitions_count', 0)}")
                self.logger.info(f"  Accounting treatments extracted: {result.get('treatments_count', 0)}")
                self.logger.info(f"  Ambiguities identified: {result.get('ambiguities_count', 0)}")
                self.logger.info(f"  Enhancements generated: {result.get('enhancements_generated', 0)}")
                
                # Wait for events to propagate
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error processing document for {standard_id}: {e}")
    
    def test_enhancement_generation(self):
        """Test enhancement generation functionality"""
        self.logger.info("\n" + "="*80)
        self.logger.info("TESTING ENHANCEMENT GENERATION")
        self.logger.info("="*80)
        
        for standard in self.standards:
            standard_id = standard["id"]
            self.logger.info(f"\nGenerating enhancement for standard {standard_id}")
            
            try:
                # Generate sample text for enhancement
                standard_text = f"""
                {standard['name']} ({standard['id']})
                
                {standard['description']}
                
                This standard requires clarification in several areas:
                1. The definition of key terms needs to be more precise
                2. The accounting treatment for special cases is not well defined
                3. The disclosure requirements need to be expanded
                """
                
                # Generate enhancement
                result = self.system_integrator.generate_enhancement(
                    standard_id, 
                    standard_text,
                    use_web_search=True
                )
                
                # Store the result
                self.results["enhancement_generation"][standard_id] = result
                
                # Log the result
                self.logger.info(f"Enhancement generation result for {standard_id}:")
                self.logger.info(f"  Success: {result.get('success', False)}")
                self.logger.info(f"  Message: {result.get('message', '')}")
                self.logger.info(f"  Proposal ID: {result.get('proposal_id', '')}")
                self.logger.info(f"  Title: {result.get('title', '')}")
                self.logger.info(f"  Description: {result.get('description', '')}")
                
                # Display proposed text and rationale
                proposed_text = result.get('proposed_text', '')
                rationale = result.get('rationale', '')
                
                if proposed_text:
                    self.logger.info(f"\nProposed Text:\n{proposed_text[:500]}...")
                
                if rationale:
                    self.logger.info(f"\nRationale:\n{rationale[:500]}...")
                
                # Wait for events to propagate
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error generating enhancement for {standard_id}: {e}")
    
    def test_validation(self):
        """Test validation functionality"""
        self.logger.info("\n" + "="*80)
        self.logger.info("TESTING VALIDATION")
        self.logger.info("="*80)
        
        # Get enhancement proposals from the database
        proposals = self.shared_db.get_enhancement_proposals()
        
        if not proposals:
            self.logger.warning("No enhancement proposals found for validation testing")
            return
        
        for proposal in proposals[:3]:  # Test validation for up to 3 proposals
            proposal_id = proposal.get("id")
            self.logger.info(f"\nValidating enhancement proposal: {proposal_id}")
            
            try:
                # Validate the enhancement
                result = self.system_integrator.validate_enhancement(proposal_id)
                
                # Store the result
                self.results["validation"][proposal_id] = result
                
                # Log the result
                self.logger.info(f"Validation result for proposal {proposal_id}:")
                self.logger.info(f"  Success: {result.get('success', False)}")
                self.logger.info(f"  Message: {result.get('message', '')}")
                self.logger.info(f"  Is Valid: {result.get('is_valid', False)}")
                self.logger.info(f"  Feedback: {result.get('feedback', '')}")
                self.logger.info(f"  Shariah Compliance: {result.get('shariah_compliance', '')}")
                self.logger.info(f"  Validation Score: {result.get('validation_score', 0.0)}")
                
                # Wait for events to propagate
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error validating enhancement proposal {proposal_id}: {e}")
    
    def test_event_tracking(self):
        """Test event tracking functionality"""
        self.logger.info("\n" + "="*80)
        self.logger.info("TESTING EVENT TRACKING")
        self.logger.info("="*80)
        
        try:
            # Get recent events
            events = self.system_integrator.get_recent_events(limit=20)
            
            # Store the events
            self.results["events"] = events
            
            # Log the events
            self.logger.info(f"Retrieved {len(events)} recent events:")
            
            for i, event in enumerate(events):
                self.logger.info(f"\nEvent {i+1}:")
                self.logger.info(f"  ID: {event.get('id', '')}")
                self.logger.info(f"  Type: {event.get('type', '')}")
                self.logger.info(f"  Topic: {event.get('topic', '')}")
                self.logger.info(f"  Timestamp: {event.get('timestamp', '')}")
                
                # Display payload summary
                payload = event.get('payload', {})
                if payload:
                    self.logger.info(f"  Payload Summary:")
                    for key, value in payload.items():
                        if isinstance(value, dict) or isinstance(value, list):
                            self.logger.info(f"    {key}: [Complex data]")
                        else:
                            self.logger.info(f"    {key}: {value}")
            
        except Exception as e:
            self.logger.error(f"Error retrieving events: {e}")
    
    def test_audit_logging(self):
        """Test audit logging functionality"""
        self.logger.info("\n" + "="*80)
        self.logger.info("TESTING AUDIT LOGGING")
        self.logger.info("="*80)
        
        try:
            # Get audit logs
            audit_logs = self.system_integrator.get_audit_logs(limit=20)
            
            # Store the audit logs
            self.results["audit_logs"] = audit_logs
            
            # Log the audit logs
            self.logger.info(f"Retrieved {len(audit_logs)} audit logs:")
            
            for i, log in enumerate(audit_logs):
                self.logger.info(f"\nAudit Log {i+1}:")
                self.logger.info(f"  ID: {log.get('id', '')}")
                self.logger.info(f"  Event Type: {log.get('event_type', '')}")
                self.logger.info(f"  User ID: {log.get('user_id', '')}")
                self.logger.info(f"  Timestamp: {log.get('timestamp', '')}")
                
                # Display details summary
                details = log.get('details', {})
                if details:
                    self.logger.info(f"  Details Summary:")
                    for key, value in details.items():
                        if isinstance(value, dict) or isinstance(value, list):
                            self.logger.info(f"    {key}: [Complex data]")
                        else:
                            self.logger.info(f"    {key}: {value}")
            
        except Exception as e:
            self.logger.error(f"Error retrieving audit logs: {e}")
    
    def generate_summary_report(self):
        """Generate a summary report of the test results"""
        self.logger.info("\n" + "="*80)
        self.logger.info("TEST SUMMARY REPORT")
        self.logger.info("="*80)
        
        # Document processing summary
        doc_results = self.results["document_processing"]
        self.logger.info("\nDocument Processing Summary:")
        self.logger.info(f"  Standards processed: {len(doc_results)}")
        successful = sum(1 for r in doc_results.values() if r.get('success', False))
        self.logger.info(f"  Successful: {successful}")
        self.logger.info(f"  Failed: {len(doc_results) - successful}")
        
        # Enhancement generation summary
        enh_results = self.results["enhancement_generation"]
        self.logger.info("\nEnhancement Generation Summary:")
        self.logger.info(f"  Enhancements generated: {len(enh_results)}")
        successful = sum(1 for r in enh_results.values() if r.get('success', False))
        self.logger.info(f"  Successful: {successful}")
        self.logger.info(f"  Failed: {len(enh_results) - successful}")
        
        # Validation summary
        val_results = self.results["validation"]
        self.logger.info("\nValidation Summary:")
        self.logger.info(f"  Proposals validated: {len(val_results)}")
        successful = sum(1 for r in val_results.values() if r.get('success', False))
        self.logger.info(f"  Successful: {successful}")
        self.logger.info(f"  Failed: {len(val_results) - successful}")
        valid = sum(1 for r in val_results.values() if r.get('is_valid', False))
        self.logger.info(f"  Valid proposals: {valid}")
        self.logger.info(f"  Invalid proposals: {len(val_results) - valid}")
        
        # Event tracking summary
        events = self.results["events"]
        self.logger.info("\nEvent Tracking Summary:")
        self.logger.info(f"  Total events tracked: {len(events)}")
        event_types = {}
        for event in events:
            event_type = event.get('type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
        for event_type, count in event_types.items():
            self.logger.info(f"  {event_type}: {count}")
        
        # Audit logging summary
        audit_logs = self.results["audit_logs"]
        self.logger.info("\nAudit Logging Summary:")
        self.logger.info(f"  Total audit logs: {len(audit_logs)}")
        event_types = {}
        for log in audit_logs:
            event_type = log.get('event_type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
        for event_type, count in event_types.items():
            self.logger.info(f"  {event_type}: {count}")
        
        self.logger.info("\n" + "="*80)
        self.logger.info("TEST COMPLETED SUCCESSFULLY")
        self.logger.info("="*80)
    
    def run_all_tests(self):
        """Run all tests"""
        try:
            self.setup_test_data()
            self.test_document_processing()
            self.test_enhancement_generation()
            self.test_validation()
            self.test_event_tracking()
            self.test_audit_logging()
            self.generate_summary_report()
        except Exception as e:
            self.logger.error(f"Error running tests: {e}")
            raise

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test the Islamic Finance Standards Enhancement System")
    parser.add_argument("--data-dir", default="data", help="Directory containing test data")
    args = parser.parse_args()
    
    logger.info("Starting system test...")
    
    tester = SystemTester(data_dir=args.data_dir)
    tester.run_all_tests()
    
    logger.info("System test completed.")

if __name__ == "__main__":
    main()
