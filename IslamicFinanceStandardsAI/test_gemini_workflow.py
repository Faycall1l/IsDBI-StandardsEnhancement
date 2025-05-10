#!/usr/bin/env python3
"""
Gemini Workflow Test for Islamic Finance Standards Enhancement

This script demonstrates the use of Gemini for both enhancement generation
and validation in the Islamic Finance Standards Enhancement system.
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
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
from utils.gemini_client import GeminiClient
from models.standard import Standard, StandardSection
from models.enhancement_proposal import EnhancementProposal

class GeminiWorkflowTest:
    """Test the Gemini workflow for enhancement generation and validation"""
    
    def __init__(self):
        """Initialize the test environment"""
        self.gemini_client = GeminiClient(api_key=os.environ["GEMINI_API_KEY"])
        logger.info("Gemini workflow test initialized")
    
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
    
    def generate_enhancement(self, standard):
        """Generate an enhancement proposal using Gemini"""
        
        logger.info(f"Generating enhancement proposal for {standard.id} using Gemini...")
        
        # Prepare the prompt for enhancement generation
        prompt = f"""
        ISLAMIC FINANCE STANDARD: {standard.name} ({standard.id})
        
        STANDARD CONTENT:
        {standard.to_text()}
        
        IDENTIFIED AMBIGUITIES:
        {json.dumps(standard.ambiguities, indent=2)}
        
        TASK:
        As an expert in Islamic finance, generate a detailed enhancement proposal for this standard.
        The proposal should address the identified ambiguities and improve the standard.
        
        Your proposal should include:
        1. A clear title for the enhancement
        2. Detailed description of the proposed changes
        3. Justification for the enhancement based on Shariah principles
        4. Specific recommendations for implementation
        
        FORMAT:
        Title: [Enhancement Title]
        
        Description:
        [Detailed description of the proposed enhancement]
        
        Justification:
        [Explanation of why this enhancement is needed, referencing Shariah principles]
        
        Recommendations:
        [Specific recommendations for implementing the enhancement]
        """
        
        # Generate the enhancement proposal
        enhancement_text = self.gemini_client.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=2000,
            system_prompt="You are an expert in Islamic finance and Shariah standards."
        )
        
        logger.info("Successfully generated enhancement proposal with Gemini")
        
        # Extract title from the generated text
        title = self._extract_title(enhancement_text)
        
        # Create an enhancement proposal object
        proposal = EnhancementProposal(
            id="EP-GEMINI-FAS4-001",
            standard_id=standard.id,
            title=title,
            description=enhancement_text,
            status="DRAFT",
            created_by="Gemini AI",
            created_at="2025-05-10"
        )
        
        return proposal
    
    def validate_enhancement(self, standard, proposal):
        """Validate an enhancement proposal using Gemini"""
        
        logger.info(f"Validating enhancement proposal {proposal.id} using Gemini...")
        
        # Prepare the prompt for validation
        prompt = f"""
        ISLAMIC FINANCE STANDARD: {standard.name} ({standard.id})
        
        STANDARD CONTENT:
        {standard.to_text()}
        
        ENHANCEMENT PROPOSAL:
        {proposal.description}
        
        TASK:
        As an expert in Islamic finance, evaluate this enhancement proposal against Shariah principles and provide a detailed validation report.
        
        Your validation should assess:
        1. Shariah Compliance: Does the proposal align with Islamic principles?
        2. Practicality: Is the proposal practical to implement?
        3. Clarity: Is the proposal clear and well-structured?
        
        FORMAT YOUR RESPONSE AS FOLLOWS:
        
        VALIDATION REPORT:
        
        Overall Score: [0-10]
        Shariah Compliance Score: [0-10]
        Practicality Score: [0-10]
        Clarity Score: [0-10]
        
        Verified Claims:
        - [claim 1] - Evidence: [supporting evidence]
        - [claim 2] - Evidence: [supporting evidence]
        ...
        
        Unverified Claims:
        - [claim 1] - Reason: [reason for rejection]
        - [claim 2] - Reason: [reason for rejection]
        ...
        
        Feedback:
        [Detailed feedback on the proposal, including strengths, weaknesses, and suggestions for improvement]
        """
        
        # Generate the validation report
        validation_text = self.gemini_client.generate_text(
            prompt=prompt,
            temperature=0.3,  # Lower temperature for more consistent validation
            max_tokens=2000,
            system_prompt="You are an expert in Islamic finance and Shariah standards."
        )
        
        logger.info("Successfully generated validation report with Gemini")
        
        return validation_text
    
    def _extract_title(self, text):
        """Extract the title from the generated text"""
        if "Title:" in text:
            title_line = [line for line in text.split('\n') if "Title:" in line][0]
            return title_line.replace("Title:", "").strip()
        else:
            return "Comprehensive Musharaka Standard Enhancement"
    
    def run_test(self):
        """Run the Gemini workflow test"""
        logger.info("Starting Gemini workflow test")
        
        # Create a mock standard
        standard = self.create_mock_standard()
        logger.info(f"Created mock standard: {standard.id} - {standard.name}")
        
        # Generate enhancement proposal
        proposal = self.generate_enhancement(standard)
        
        # Validate the enhancement proposal
        validation_report = self.validate_enhancement(standard, proposal)
        
        # Display the results
        self._display_results(standard, proposal, validation_report)
        
        logger.info("Gemini workflow test completed")
    
    def _display_results(self, standard, proposal, validation_report):
        """Display the results of the Gemini workflow test"""
        print("\n" + "="*80)
        print("GEMINI WORKFLOW FOR ISLAMIC FINANCE STANDARDS ENHANCEMENT")
        print("="*80)
        
        # Standard information
        print(f"\nSTANDARD: {standard.id} - {standard.name}")
        print(f"Version: {standard.version}")
        print(f"Ambiguities identified: {len(standard.ambiguities)}")
        for i, ambiguity in enumerate(standard.ambiguities, 1):
            print(f"  {i}. {ambiguity}")
        
        # Enhancement proposal
        print("\n" + "-"*80)
        print(f"ENHANCEMENT PROPOSAL: {proposal.id}")
        print(f"Title: {proposal.title}")
        print(f"Status: {proposal.status}")
        print(f"Created by: {proposal.created_by}")
        print("\nProposal Text:")
        print("-"*40)
        print(proposal.description)
        
        # Validation results
        print("\n" + "-"*80)
        print("VALIDATION REPORT:")
        print("-"*40)
        print(validation_report)
        
        print("="*80)

def main():
    """Main function to run the Gemini workflow test"""
    workflow_test = GeminiWorkflowTest()
    workflow_test.run_test()

if __name__ == "__main__":
    main()
