#!/usr/bin/env python3
"""
Generate Enhancement Example for Islamic Finance Standards

This script demonstrates the generation of enhancement proposals for Islamic finance standards
using both OpenAI and Gemini models, showing the actual enhancement text content.
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
from agents.enhancement_agent.enhancement_agent import EnhancementAgent
from models.standard import Standard, StandardSection
from models.enhancement_proposal import EnhancementProposal

def create_mock_standard():
    """Create a mock standard for demonstration purposes"""
    
    # Create a mock Musharaka standard (FAS 4)
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

def generate_enhancement_with_gemini(standard):
    """Generate enhancement proposal using Gemini"""
    
    logger.info("Generating enhancement proposal using Gemini...")
    
    try:
        gemini_client = GeminiClient(api_key=os.environ["GEMINI_API_KEY"])
        
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
        enhancement_text = gemini_client.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=2000,
            system_prompt="You are an expert in Islamic finance and Shariah standards."
        )
        
        logger.info("Successfully generated enhancement proposal with Gemini")
        
        # Create an enhancement proposal object
        proposal = EnhancementProposal(
            id="EP-GEMINI-FAS4-001",
            standard_id=standard.id,
            title=extract_title(enhancement_text),
            description=enhancement_text,
            status="DRAFT",
            created_by="Gemini AI",
            created_at="2025-05-10"
        )
        
        return proposal
        
    except Exception as e:
        logger.error(f"Error generating enhancement with Gemini: {str(e)}")
        return None

def extract_title(text):
    """Extract the title from the generated text"""
    if "Title:" in text:
        title_line = [line for line in text.split('\n') if "Title:" in line][0]
        return title_line.replace("Title:", "").strip()
    else:
        return "Comprehensive Musharaka Standard Enhancement"

def main():
    """Main function to demonstrate enhancement generation"""
    
    logger.info("Starting enhancement generation example")
    
    # Create a mock standard
    standard = create_mock_standard()
    logger.info(f"Created mock standard: {standard.id} - {standard.name}")
    
    # Generate enhancement proposal with Gemini
    proposal = generate_enhancement_with_gemini(standard)
    
    if proposal:
        # Display the enhancement proposal
        print("\n" + "="*80)
        print(f"ENHANCEMENT PROPOSAL: {proposal.id}")
        print("="*80)
        print(f"Title: {proposal.title}")
        print("\nFull Enhancement Text:")
        print("-"*80)
        print(proposal.description)
        print("="*80)
    else:
        logger.error("Failed to generate enhancement proposal")

if __name__ == "__main__":
    main()
