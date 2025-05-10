#!/usr/bin/env python3
"""
Full Pipeline Test for Islamic Finance Standards Enhancement System

This script demonstrates the complete workflow through all agents:
1. Document Agent: Processes the standard and extracts structured data
2. Enhancement Agent: Generates improvement proposals
3. Validation Agent: Reviews proposals against Shariah principles

Both OpenAI and Gemini are supported with automatic fallback.
"""

import os
import sys
import json
import logging
import time
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('full_pipeline_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set environment variables for testing
os.environ["USE_GEMINI"] = "true"
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "AIzaSyAND61l0rHF-p2UQg28RSMe62DZgQOHsLE")

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import system components
from agents.document_agent.document_agent import DocumentAgent
from agents.enhancement_agent.enhancement_agent import EnhancementAgent
from agents.validation_agent.validation_agent import ValidationAgent
from models.standard import Standard, StandardSection
from models.enhancement_proposal import EnhancementProposal
from utils.event_bus import EventBus
from utils.audit_logger import AuditLogger

class FullPipelineTest:
    """Test the full pipeline of the Islamic Finance Standards Enhancement System"""
    
    def __init__(self):
        """Initialize the test environment"""
        self.event_bus = EventBus()
        self.audit_logger = AuditLogger(self.event_bus)
        
        # Initialize agents
        self.document_agent = DocumentAgent(self.event_bus)
        self.enhancement_agent = EnhancementAgent(self.event_bus)
        self.validation_agent = ValidationAgent(self.event_bus)
        
        # Subscribe to events
        self._setup_event_handlers()
        
        # Test data
        self.standard = None
        self.proposal = None
        self.validation_result = None
        
        logger.info("Full pipeline test initialized")
    
    def _setup_event_handlers(self):
        """Set up event handlers for the event bus"""
        self.event_bus.subscribe("standard.processed", self._on_standard_processed)
        self.event_bus.subscribe("enhancement.generated", self._on_enhancement_generated)
        self.event_bus.subscribe("enhancement.validated", self._on_enhancement_validated)
    
    def _on_standard_processed(self, event_data):
        """Handle standard processed event"""
        logger.info(f"Standard processed: {event_data['standard_id']}")
        self.standard = event_data['standard']
        
        # Trigger enhancement generation
        self.enhancement_agent.generate_enhancement(self.standard)
    
    def _on_enhancement_generated(self, event_data):
        """Handle enhancement generated event"""
        logger.info(f"Enhancement generated: {event_data['proposal_id']}")
        self.proposal = event_data['proposal']
        
        # Trigger validation
        self.validation_agent.validate_proposal(self.proposal.id)
    
    def _on_enhancement_validated(self, event_data):
        """Handle enhancement validated event"""
        logger.info(f"Enhancement validated: {event_data['proposal_id']}")
        self.validation_result = event_data['validation_result']
        
        # Display the results
        self._display_results()
    
    def _display_results(self):
        """Display the results of the full pipeline"""
        print("\n" + "="*80)
        print("ISLAMIC FINANCE STANDARDS ENHANCEMENT SYSTEM - FULL PIPELINE RESULTS")
        print("="*80)
        
        # Standard information
        print(f"\nSTANDARD: {self.standard.id} - {self.standard.name}")
        print(f"Version: {self.standard.version}")
        print(f"Ambiguities identified: {len(self.standard.ambiguities)}")
        for i, ambiguity in enumerate(self.standard.ambiguities, 1):
            print(f"  {i}. {ambiguity}")
        
        # Enhancement proposal
        print("\n" + "-"*80)
        print(f"ENHANCEMENT PROPOSAL: {self.proposal.id}")
        print(f"Title: {self.proposal.title}")
        print(f"Status: {self.proposal.status}")
        print(f"Created by: {self.proposal.created_by}")
        print("\nProposal Text:")
        print("-"*40)
        print(self.proposal.description)
        
        # Validation results
        print("\n" + "-"*80)
        print("VALIDATION RESULTS:")
        print(f"Overall Score: {self.validation_result.overall_score:.2f}/10.0")
        print(f"Shariah Compliance: {self.validation_result.shariah_compliance_score:.2f}/10.0")
        print(f"Practicality: {self.validation_result.practicality_score:.2f}/10.0")
        print(f"Clarity: {self.validation_result.clarity_score:.2f}/10.0")
        
        print("\nVerified Claims:")
        for claim in self.validation_result.verified_claims:
            print(f"  ✓ {claim['claim']} (Confidence: {claim['confidence']:.2f})")
        
        print("\nUnverified Claims:")
        for claim in self.validation_result.unverified_claims:
            print(f"  ✗ {claim['claim']} (Confidence: {claim['confidence']:.2f})")
        
        print("\nFeedback:")
        print(self.validation_result.feedback)
        
        print("="*80)
    
    def create_mock_standard(self):
        """Create a mock standard for testing"""
        standard = Standard(
            id="FAS4",
            name="Musharaka Financing",
            description="Standard on Musharaka Financing",
            version="1.0",
            publication_date="2020-01-01",
            sections=[
                StandardSection(
                    id="FAS4-1",
                    title="Definition",
                    content="""
                    Musharaka is a form of partnership between the Islamic bank and its clients whereby each party contributes to the capital of partnership in equal or varying degrees to establish a new project or share in an existing one, and whereby each of the parties becomes an owner of the capital on a permanent or declining basis and shall have his due share of profits. However, losses are shared in proportion to the contributed capital. It is not permissible to stipulate otherwise.
                    """
                ),
                StandardSection(
                    id="FAS4-2",
                    title="Types of Musharaka",
                    content="""
                    2.1 Permanent Musharaka: A partnership in which the Islamic bank participates in the capital of a project and receives a share of the profits in return. The participation remains as long as the project exists, unless the bank decides to withdraw or transfer its share to another party.
                    
                    2.2 Diminishing Musharaka: A partnership in which the Islamic bank agrees to transfer gradually to the other partner its share in the Musharaka, so that the Islamic bank's share declines and the other partner's share increases until the latter becomes the sole proprietor of the venture.
                    """
                ),
                StandardSection(
                    id="FAS4-3",
                    title="Profit Distribution",
                    content="""
                    3.1 It is a requirement that the mechanism for profit distribution be clearly determined when the contract is concluded.
                    
                    3.2 Profits are distributed according to the agreement between the parties. It is permissible to agree on different profit-sharing ratios from the ratio of capital contribution.
                    
                    3.3 It is not permissible to fix a lump sum profit for any partner.
                    """
                ),
                StandardSection(
                    id="FAS4-4",
                    title="Loss Sharing",
                    content="""
                    4.1 Losses are shared in proportion to each partner's share in the capital.
                    
                    4.2 Any condition that contradicts the principle of sharing losses in proportion to capital contributions is void.
                    """
                )
            ],
            ambiguities=[
                "The standard does not address digital or online Musharaka arrangements.",
                "There is no clear guidance on how to handle disputes in Musharaka contracts.",
                "The standard lacks specific examples for modern applications of Musharaka in project financing."
            ]
        )
        
        return standard
    
    def run_test(self):
        """Run the full pipeline test"""
        logger.info("Starting full pipeline test")
        
        # Create a mock standard
        standard = self.create_mock_standard()
        logger.info(f"Created mock standard: {standard.id} - {standard.name}")
        
        # Simulate document processing
        self.document_agent.process_standard(standard)
        
        # Wait for the pipeline to complete
        timeout = 300  # 5 minutes
        start_time = time.time()
        
        while not self.validation_result and time.time() - start_time < timeout:
            time.sleep(1)
        
        if not self.validation_result:
            logger.error("Pipeline test timed out")
            print("Pipeline test timed out after 5 minutes")
        
        logger.info("Full pipeline test completed")

def main():
    """Main function to run the full pipeline test"""
    pipeline_test = FullPipelineTest()
    pipeline_test.run_test()

if __name__ == "__main__":
    main()
