#!/usr/bin/env python3
"""
Full Workflow Test for Islamic Finance Standards Enhancement System

This script demonstrates the complete workflow through all agents with Gemini integration:
1. Document Agent: Processes the standard and extracts structured data
2. Enhancement Agent: Generates improvement proposals using Gemini or OpenAI
3. Validation Agent: Reviews proposals against Shariah principles using Gemini or OpenAI

The test uses mock implementations where needed to ensure the workflow runs end-to-end.
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
        logging.FileHandler('full_workflow_test.log')
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
from database.mock_knowledge_graph import MockKnowledgeGraph
from agents.document_agent.document_agent import DocumentAgent
from agents.enhancement_agent.enhancement_agent import EnhancementAgent
from agents.validation_agent.validation_agent import ValidationAgent
from utils.gemini_client import GeminiClient
from models.standard import Standard, StandardSection
from models.enhancement_proposal import EnhancementProposal
from models.document_schema import StandardDocument, Definition, AccountingTreatment, TransactionStructure
from models.validation_schema import ValidationResult, ValidationStatus, ValidationCriteria

class FullWorkflowTest:
    """Test the full workflow of the Islamic Finance Standards Enhancement System with Gemini integration"""
    
    def __init__(self):
        """Initialize the test environment"""
        # Initialize knowledge graph
        self.knowledge_graph = MockKnowledgeGraph()
        
        # Initialize agents
        self.document_agent = DocumentAgent(self.knowledge_graph)
        self.enhancement_agent = EnhancementAgent(self.knowledge_graph)
        self.validation_agent = ValidationAgent(self.knowledge_graph)
        
        # Initialize Gemini client
        self.gemini_client = GeminiClient(api_key=os.environ["GEMINI_API_KEY"])
        
        logger.info("Full workflow test initialized")
    
    def create_mock_standard(self):
        """Create a mock standard document for testing"""
        standard = StandardDocument(
            title="Musharaka Financing",
            standard_type="Financial Accounting Standard",
            standard_number="FAS 4",
            publication_date="2020-01-01",
            definitions=[
                Definition(
                    term="Musharaka",
                    definition="A form of partnership between the Islamic bank and its clients whereby each party contributes to the capital of partnership in equal or varying degrees to establish a new project or share in an existing one."
                ),
                Definition(
                    term="Permanent Musharaka",
                    definition="A partnership in which the Islamic bank participates in the capital of a project and receives a share of the profits in return. The participation remains as long as the project exists."
                ),
                Definition(
                    term="Diminishing Musharaka",
                    definition="A partnership in which the Islamic bank agrees to transfer gradually to the other partner its share in the Musharaka, so that the Islamic bank's share declines and the other partner's share increases until the latter becomes the sole proprietor of the venture."
                )
            ],
            accounting_treatments=[
                AccountingTreatment(
                    title="Profit Distribution",
                    description="Profits are distributed according to the agreement between the parties. It is permissible to agree on different profit-sharing ratios from the ratio of capital contribution."
                ),
                AccountingTreatment(
                    title="Loss Sharing",
                    description="Losses are shared in proportion to each partner's share in the capital. Any condition that contradicts this principle is void."
                )
            ],
            transaction_structures=[
                TransactionStructure(
                    title="Basic Musharaka Structure",
                    description="The basic structure of a Musharaka transaction",
                    steps=[
                        "1. Partners contribute capital",
                        "2. Partnership agreement is signed",
                        "3. Project is executed",
                        "4. Profits are distributed according to agreed ratios",
                        "5. Losses are shared in proportion to capital"
                    ]
                )
            ],
            ambiguities=[
                {
                    "text": "The standard does not address digital or online Musharaka arrangements.",
                    "context": "Modern financial technology applications",
                    "indicator": "missing_guidance"
                },
                {
                    "text": "There is no clear guidance on how to handle disputes in Musharaka contracts.",
                    "context": "Conflict resolution",
                    "indicator": "missing_guidance"
                },
                {
                    "text": "The standard lacks specific examples for modern applications of Musharaka in project financing.",
                    "context": "Application examples",
                    "indicator": "missing_examples"
                }
            ],
            raw_text="""
            Musharaka Financing (FAS 4)
            
            Definition:
            Musharaka is a form of partnership between the Islamic bank and its clients whereby each party contributes to the capital of partnership in equal or varying degrees to establish a new project or share in an existing one, and whereby each of the parties becomes an owner of the capital on a permanent or declining basis and shall have his due share of profits. However, losses are shared in proportion to the contributed capital. It is not permissible to stipulate otherwise.
            
            Types of Musharaka:
            1. Permanent Musharaka: A partnership in which the Islamic bank participates in the capital of a project and receives a share of the profits in return. The participation remains as long as the project exists, unless the bank decides to withdraw or transfer its share to another party.
            
            2. Diminishing Musharaka: A partnership in which the Islamic bank agrees to transfer gradually to the other partner its share in the Musharaka, so that the Islamic bank's share declines and the other partner's share increases until the latter becomes the sole proprietor of the venture.
            
            Profit Distribution:
            1. It is a requirement that the mechanism for profit distribution be clearly determined when the contract is concluded.
            
            2. Profits are distributed according to the agreement between the parties. It is permissible to agree on different profit-sharing ratios from the ratio of capital contribution.
            
            3. It is not permissible to fix a lump sum profit for any partner.
            
            Loss Sharing:
            1. Losses are shared in proportion to each partner's share in the capital.
            
            2. Any condition that contradicts the principle of sharing losses in proportion to capital contributions is void.
            """
        )
        
        return standard
    
    def process_document(self, standard_document):
        """Process a document using the Document Agent"""
        logger.info("Step 1: Processing document")
        
        try:
            # In a real scenario, this would process a PDF or DOCX file
            # For testing, we're using a pre-created StandardDocument
            
            # Store the document in the knowledge graph
            standard_id = self.knowledge_graph.create_node(
                label="Standard",
                properties={
                    "title": standard_document.title,
                    "standard_type": standard_document.standard_type,
                    "standard_number": standard_document.standard_number,
                    "publication_date": standard_document.publication_date
                }
            )
            
            # Store definitions
            for definition in standard_document.definitions:
                def_id = self.knowledge_graph.create_node(
                    label="Definition",
                    properties={
                        "term": definition.term,
                        "definition": definition.definition
                    }
                )
                self.knowledge_graph.create_relationship(
                    start_node_id=standard_id,
                    end_node_id=def_id,
                    relationship_type="HAS_DEFINITION"
                )
            
            # Store accounting treatments
            for treatment in standard_document.accounting_treatments:
                treatment_id = self.knowledge_graph.create_node(
                    label="AccountingTreatment",
                    properties={
                        "title": treatment.title,
                        "description": treatment.description
                    }
                )
                self.knowledge_graph.create_relationship(
                    start_node_id=standard_id,
                    end_node_id=treatment_id,
                    relationship_type="HAS_ACCOUNTING_TREATMENT"
                )
            
            # Store transaction structures
            for structure in standard_document.transaction_structures:
                structure_id = self.knowledge_graph.create_node(
                    label="TransactionStructure",
                    properties={
                        "title": structure.title,
                        "description": structure.description,
                        "steps": json.dumps(structure.steps)
                    }
                )
                self.knowledge_graph.create_relationship(
                    start_node_id=standard_id,
                    end_node_id=structure_id,
                    relationship_type="HAS_TRANSACTION_STRUCTURE"
                )
            
            # Store ambiguities
            for ambiguity in standard_document.ambiguities:
                ambiguity_id = self.knowledge_graph.create_node(
                    label="Ambiguity",
                    properties=ambiguity
                )
                self.knowledge_graph.create_relationship(
                    start_node_id=standard_id,
                    end_node_id=ambiguity_id,
                    relationship_type="HAS_AMBIGUITY"
                )
            
            logger.info(f"Document processed and stored with ID: {standard_id}")
            return standard_id
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def generate_enhancements(self, standard_id):
        """Generate enhancement proposals using the Enhancement Agent"""
        logger.info("Step 2: Generating enhancement proposals")
        
        try:
            # In a real scenario, this would use the enhancement agent
            # For testing with Gemini, we'll implement a simplified version
            
            # Get standard info from knowledge graph
            standard_info = self.knowledge_graph.get_node_by_id(standard_id)
            
            # Get related nodes
            related_nodes = self.knowledge_graph.get_related_nodes(standard_id)
            
            # Extract ambiguities
            ambiguity_nodes = [node for node in related_nodes if node["label"] == "Ambiguity"]
            ambiguities = [node["properties"]["text"] for node in ambiguity_nodes]
            
            # Create a standard object for the prompt
            standard = Standard(
                id=standard_id,
                name=standard_info["properties"]["title"],
                description=f"{standard_info['properties']['standard_type']} {standard_info['properties']['standard_number']}",
                version="1.0",
                publication_date=standard_info["properties"]["publication_date"],
                sections=[
                    StandardSection(
                        id="section-1",
                        title="Definition",
                        content="\n".join([node["properties"]["definition"] for node in related_nodes if node["label"] == "Definition"])
                    ),
                    StandardSection(
                        id="section-2",
                        title="Accounting Treatments",
                        content="\n".join([node["properties"]["description"] for node in related_nodes if node["label"] == "AccountingTreatment"])
                    ),
                    StandardSection(
                        id="section-3",
                        title="Transaction Structures",
                        content="\n".join([node["properties"]["description"] for node in related_nodes if node["label"] == "TransactionStructure"])
                    )
                ],
                ambiguities=ambiguities
            )
            
            # Generate enhancement using Gemini
            logger.info("Generating enhancement with Gemini")
            
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
                id=f"EP-{standard_id}-001",
                standard_id=standard_id,
                title=title,
                description=enhancement_text,
                status="DRAFT",
                created_by="Gemini AI",
                created_at=datetime.now().isoformat()
            )
            
            # Store the proposal in the knowledge graph
            proposal_id = self.knowledge_graph.create_node(
                label="EnhancementProposal",
                properties={
                    "id": proposal.id,
                    "standard_id": proposal.standard_id,
                    "title": proposal.title,
                    "description": proposal.description,
                    "status": proposal.status,
                    "created_by": proposal.created_by,
                    "created_at": proposal.created_at
                }
            )
            
            # Link the proposal to the standard
            self.knowledge_graph.create_relationship(
                start_node_id=standard_id,
                end_node_id=proposal_id,
                relationship_type="HAS_ENHANCEMENT_PROPOSAL"
            )
            
            logger.info(f"Enhancement proposal generated and stored with ID: {proposal_id}")
            return proposal
            
        except Exception as e:
            logger.error(f"Error generating enhancements: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def validate_proposal(self, proposal):
        """Validate an enhancement proposal using the Validation Agent"""
        logger.info("Step 3: Validating enhancement proposal")
        
        try:
            # Get standard info from knowledge graph
            standard_info = self.knowledge_graph.get_node_by_id(proposal.standard_id)
            
            # Get related nodes
            related_nodes = self.knowledge_graph.get_related_nodes(proposal.standard_id)
            
            # Create a standard object for the prompt
            standard = Standard(
                id=proposal.standard_id,
                name=standard_info["properties"]["title"],
                description=f"{standard_info['properties']['standard_type']} {standard_info['properties']['standard_number']}",
                version="1.0",
                publication_date=standard_info["properties"]["publication_date"],
                sections=[
                    StandardSection(
                        id="section-1",
                        title="Definition",
                        content="\n".join([node["properties"]["definition"] for node in related_nodes if node["label"] == "Definition"])
                    ),
                    StandardSection(
                        id="section-2",
                        title="Accounting Treatments",
                        content="\n".join([node["properties"]["description"] for node in related_nodes if node["label"] == "AccountingTreatment"])
                    ),
                    StandardSection(
                        id="section-3",
                        title="Transaction Structures",
                        content="\n".join([node["properties"]["description"] for node in related_nodes if node["label"] == "TransactionStructure"])
                    )
                ]
            )
            
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
            
            # Generate the validation report using Gemini
            validation_text = self.gemini_client.generate_text(
                prompt=prompt,
                temperature=0.3,  # Lower temperature for more consistent validation
                max_tokens=2000,
                system_prompt="You are an expert in Islamic finance and Shariah standards."
            )
            
            logger.info("Successfully generated validation report with Gemini")
            
            # Parse the validation report
            overall_score = self._extract_score(validation_text, "Overall Score:")
            shariah_compliance_score = self._extract_score(validation_text, "Shariah Compliance Score:")
            practicality_score = self._extract_score(validation_text, "Practicality Score:")
            clarity_score = self._extract_score(validation_text, "Clarity Score:")
            
            # Extract verified and unverified claims
            verified_claims = self._extract_claims(validation_text, "Verified Claims:")
            unverified_claims = self._extract_claims(validation_text, "Unverified Claims:")
            
            # Extract feedback
            feedback = self._extract_section(validation_text, "Feedback:")
            
            # Determine validation status
            status = ValidationStatus.APPROVED if overall_score >= 7.0 else ValidationStatus.REJECTED
            
            # Create validation result
            validation_result = ValidationResult(
                proposal_id=proposal.id,
                validation_date=datetime.now().isoformat(),
                validation_scores={
                    "SHARIAH_COMPLIANCE": shariah_compliance_score,
                    "TECHNICAL_ACCURACY": 8.0,  # Default value
                    "CLARITY_AND_PRECISION": clarity_score,
                    "PRACTICAL_IMPLEMENTATION": practicality_score,
                    "CONSISTENCY": 7.0  # Default value
                },
                overall_score=overall_score,
                status=status,
                feedback=feedback,
                modified_content=None
            )
            
            # Update proposal status
            proposal.status = status.value
            proposal.validation_score = overall_score
            proposal.validation_feedback = feedback
            
            # Store validation result in knowledge graph
            validation_id = self.knowledge_graph.create_node(
                label="ValidationResult",
                properties={
                    "proposal_id": proposal.id,
                    "validation_date": validation_result.validation_date,
                    "overall_score": validation_result.overall_score,
                    "shariah_compliance_score": validation_result.validation_scores['SHARIAH_COMPLIANCE'],
                    "practicality_score": validation_result.validation_scores['PRACTICAL_IMPLEMENTATION'],
                    "clarity_score": validation_result.validation_scores['CLARITY_AND_PRECISION'],
                    "status": validation_result.status.value,
                    "feedback": validation_result.feedback
                }
            )
            
            # Link validation result to proposal
            self.knowledge_graph.create_relationship(
                start_node_id=proposal.id,
                end_node_id=validation_id,
                relationship_type="HAS_VALIDATION"
            )
            
            logger.info(f"Validation completed with status: {status.value}")
            return validation_result, verified_claims, unverified_claims
            
        except Exception as e:
            logger.error(f"Error validating proposal: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _extract_title(self, text):
        """Extract the title from the generated text"""
        if "Title:" in text:
            title_line = [line for line in text.split('\n') if "Title:" in line][0]
            return title_line.replace("Title:", "").strip()
        else:
            return "Comprehensive Musharaka Standard Enhancement"
    
    def _extract_score(self, text, score_label):
        """Extract a score from the validation text"""
        try:
            if score_label in text:
                score_line = [line for line in text.split('\n') if score_label in line][0]
                score_str = score_line.replace(score_label, "").strip()
                return float(score_str)
            return 0.0
        except:
            return 0.0
    
    def _extract_claims(self, text, claims_label):
        """Extract claims from the validation text"""
        claims = []
        
        if claims_label not in text:
            return claims
        
        # Get the section with claims
        start_idx = text.find(claims_label) + len(claims_label)
        end_idx = text.find("Unverified Claims:") if "Unverified Claims:" in text[start_idx:] else text.find("Feedback:")
        
        if end_idx == -1:
            claims_section = text[start_idx:].strip()
        else:
            claims_section = text[start_idx:start_idx + end_idx].strip()
        
        # Extract individual claims
        for line in claims_section.split('\n'):
            line = line.strip()
            if line.startswith('-'):
                claim_text = line[1:].strip()
                
                # Split into claim and evidence/reason
                if ' - Evidence: ' in claim_text:
                    claim, evidence = claim_text.split(' - Evidence: ', 1)
                    claims.append({"claim": claim.strip(), "evidence": evidence.strip(), "confidence": 0.9})
                elif ' - Reason: ' in claim_text:
                    claim, reason = claim_text.split(' - Reason: ', 1)
                    claims.append({"claim": claim.strip(), "evidence": reason.strip(), "confidence": 0.1})
                else:
                    claims.append({"claim": claim_text, "evidence": "", "confidence": 0.5})
        
        return claims
    
    def _extract_section(self, text, section_label):
        """Extract a section from the validation text"""
        if section_label not in text:
            return ""
        
        start_idx = text.find(section_label) + len(section_label)
        next_section_idx = float('inf')
        
        # Find the next section
        for label in ["Overall Score:", "Shariah Compliance Score:", "Practicality Score:", 
                     "Clarity Score:", "Verified Claims:", "Unverified Claims:", "Feedback:"]:
            if label == section_label:
                continue
            
            idx = text.find(label, start_idx)
            if idx != -1 and idx < next_section_idx:
                next_section_idx = idx
        
        if next_section_idx == float('inf'):
            section_content = text[start_idx:].strip()
        else:
            section_content = text[start_idx:next_section_idx].strip()
        
        return section_content
    
    def run_test(self):
        """Run the full workflow test"""
        logger.info("Starting full workflow test with Gemini integration")
        
        # Step 1: Create and process a mock standard
        standard_document = self.create_mock_standard()
        standard_id = self.process_document(standard_document)
        
        if not standard_id:
            logger.error("Document processing failed")
            return
        
        # Step 2: Generate enhancement proposals
        proposal = self.generate_enhancements(standard_id)
        
        if not proposal:
            logger.error("Enhancement generation failed")
            return
        
        # Step 3: Validate the proposal
        validation_result, verified_claims, unverified_claims = self.validate_proposal(proposal)
        
        if not validation_result:
            logger.error("Validation failed")
            return
        
        # Display the results
        self._display_results(standard_document, proposal, validation_result, verified_claims, unverified_claims)
        
        logger.info("Full workflow test completed successfully")
    
    def _display_results(self, standard_document, proposal, validation_result, verified_claims, unverified_claims):
        """Display the results of the full workflow test"""
        print("\n" + "="*80)
        print("ISLAMIC FINANCE STANDARDS ENHANCEMENT SYSTEM - FULL WORKFLOW RESULTS")
        print("="*80)
        
        # Standard information
        print(f"\nSTANDARD: {standard_document.standard_number} - {standard_document.title}")
        print(f"Type: {standard_document.standard_type}")
        print(f"Publication Date: {standard_document.publication_date}")
        print(f"Ambiguities identified: {len(standard_document.ambiguities)}")
        for i, ambiguity in enumerate(standard_document.ambiguities, 1):
            print(f"  {i}. {ambiguity['text']}")
        
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
        print("VALIDATION RESULTS:")
        print(f"Overall Score: {validation_result.overall_score:.2f}/10.0")
        print(f"Shariah Compliance: {validation_result.validation_scores['SHARIAH_COMPLIANCE']:.2f}/10.0")
        print(f"Practicality: {validation_result.validation_scores['PRACTICAL_IMPLEMENTATION']:.2f}/10.0")
        print(f"Clarity: {validation_result.validation_scores['CLARITY_AND_PRECISION']:.2f}/10.0")
        print(f"Status: {validation_result.status.value}")
        
        # Since we're not storing verified_claims and unverified_claims in ValidationResult
        # We'll display the extracted claims from our processing
        print("\nVerified Claims:")
        for claim in verified_claims:
            print(f"  ✓ {claim['claim']} (Confidence: {claim['confidence']:.2f})")
            if claim['evidence']:
                print(f"    Evidence: {claim['evidence']}")
        
        print("\nUnverified Claims:")
        for claim in unverified_claims:
            print(f"  ✗ {claim['claim']} (Confidence: {claim['confidence']:.2f})")
            if claim['evidence']:
                print(f"    Reason: {claim['evidence']}")
        
        print("\nFeedback:")
        print(validation_result.feedback)
        
        print("="*80)

def main():
    """Main function to run the full workflow test"""
    workflow_test = FullWorkflowTest()
    workflow_test.run_test()

if __name__ == "__main__":
    main()
