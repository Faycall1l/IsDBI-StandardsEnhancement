#!/usr/bin/env python
"""
View Enhancement Proposals and Validation Results

This script displays the enhancement proposals and validation results stored in Neo4j
for the Islamic Finance Standards Enhancement system.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from tabulate import tabulate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set environment variables for Neo4j
os.environ["USE_NEO4J"] = "true"
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USER"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "password123"

# Add the IslamicFinanceStandardsAI directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'IslamicFinanceStandardsAI'))

# Import Neo4j driver
from neo4j import GraphDatabase

def view_enhancement_proposals():
    """View enhancement proposals and validation results stored in Neo4j"""
    try:
        # Initialize Neo4j connection
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "password123")
        
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        logger.info("Connected to Neo4j database")
        
        with driver.session() as session:
            # Get all standards
            standards = session.run("MATCH (s:Standard) RETURN ID(s) as id, s.title as title, s.standard_type as standard_type, s.standard_number as standard_number").data()
            logger.info(f"Found {len(standards)} standards")
            
            # Get all enhancement proposals
            proposals = session.run("""
                MATCH (p:EnhancementProposal) 
                RETURN ID(p) as id, p.enhancement_type as enhancement_type, p.standard_id as standard_id, 
                       p.enhanced_content as enhanced_content, p.reasoning as reasoning, p.status as status
            """).data()
            logger.info(f"Found {len(proposals)} enhancement proposals")
            
            # Get all validation results
            validation_results = session.run("""
                MATCH (v:ValidationResult) 
                RETURN ID(v) as id, v.proposal_id as proposal_id, v.status as status, 
                       v.overall_score as overall_score, v.feedback as feedback, v.modified_content as modified_content
            """).data()
            logger.info(f"Found {len(validation_results)} validation results")
        
        # Print standards
        print("\n=== Standards ===")
        standards_data = []
        for standard in standards:
            standards_data.append([
                standard.get("id", "N/A"),
                standard.get("title", "N/A"),
                standard.get("standard_type", "N/A"),
                standard.get("standard_number", "N/A")
            ])
        
        print(tabulate(standards_data, headers=["ID", "Title", "Type", "Number"]))
        
        # Print enhancement proposals
        print("\n=== Enhancement Proposals ===")
        proposals_data = []
        for proposal in proposals:
            # Find validation status for this proposal
            validation_status = "Not Validated"
            validation_score = "N/A"
            
            for validation in validation_results:
                if str(validation.get("proposal_id", "")) == str(proposal.get("id", "")):
                    validation_status = validation.get("status", "Unknown")
                    validation_score = validation.get("overall_score", "N/A")
                    break
            
            # Truncate enhanced content for display
            enhanced_content = proposal.get("enhanced_content", "")
            if enhanced_content and len(enhanced_content) > 100:
                enhanced_content = enhanced_content[:100] + "..."
            
            proposals_data.append([
                proposal.get("id", "N/A"),
                proposal.get("enhancement_type", "N/A"),
                proposal.get("standard_id", "N/A"),
                enhanced_content,
                validation_status,
                validation_score
            ])
        
        print(tabulate(proposals_data, headers=["ID", "Type", "Standard ID", "Enhanced Content", "Status", "Score"]))
        
        # Print validation results
        print("\n=== Validation Results ===")
        validation_data = []
        for result in validation_results:
            # Truncate feedback for display
            feedback = result.get("feedback", "")
            if feedback and len(feedback) > 100:
                feedback = feedback[:100] + "..."
            
            validation_data.append([
                result.get("id", "N/A"),
                result.get("proposal_id", "N/A"),
                result.get("status", "N/A"),
                result.get("overall_score", "N/A"),
                feedback
            ])
        
        print(tabulate(validation_data, headers=["ID", "Proposal ID", "Status", "Score", "Feedback"]))
        
        # View full content of a proposal
        while True:
            print("\nOptions:")
            print("1. View full content of an enhancement proposal")
            print("2. View full feedback for a validation result")
            print("3. Exit")
            
            choice = input("Enter your choice (1-3): ")
            
            if choice == "1":
                proposal_id = input("Enter proposal ID: ")
                # Find the proposal in our list
                proposal_details = None
                for p in proposals:
                    if str(p.get("id", "")) == proposal_id:
                        proposal_details = p
                        break
                
                if proposal_details:
                    print("\n=== Enhancement Proposal Details ===")
                    print(f"ID: {proposal_details.get('id', 'N/A')}")
                    print(f"Type: {proposal_details.get('enhancement_type', 'N/A')}")
                    print(f"Standard ID: {proposal_details.get('standard_id', 'N/A')}")
                    print(f"Status: {proposal_details.get('status', 'N/A')}")
                    print("\nEnhanced Content:")
                    print(proposal_details.get('enhanced_content', 'N/A'))
                    print("\nReasoning:")
                    print(proposal_details.get('reasoning', 'N/A'))
                else:
                    print(f"Proposal with ID {proposal_id} not found")
            
            elif choice == "2":
                validation_id = input("Enter validation result ID: ")
                # Find the validation result in our list
                validation_details = None
                for v in validation_results:
                    if str(v.get("id", "")) == validation_id:
                        validation_details = v
                        break
                
                if validation_details:
                    print("\n=== Validation Result Details ===")
                    print(f"ID: {validation_details.get('id', 'N/A')}")
                    print(f"Proposal ID: {validation_details.get('proposal_id', 'N/A')}")
                    print(f"Status: {validation_details.get('status', 'N/A')}")
                    print(f"Overall Score: {validation_details.get('overall_score', 'N/A')}")
                    print("\nFeedback:")
                    print(validation_details.get('feedback', 'N/A'))
                    print("\nModified Content:")
                    print(validation_details.get('modified_content', 'N/A'))
                else:
                    print(f"Validation result with ID {validation_id} not found")
            
            elif choice == "3":
                break
            
            else:
                print("Invalid choice. Please try again.")
        
    except Exception as e:
        logger.error(f"Error viewing enhancement proposals: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")
    finally:
        # Close Neo4j connection
        try:
            driver.close()
            logger.info("Closed Neo4j connection")
        except:
            pass

if __name__ == "__main__":
    try:
        view_enhancement_proposals()
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")
        sys.exit(1)
