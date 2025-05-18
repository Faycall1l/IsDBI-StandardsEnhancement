#!/usr/bin/env python
"""
View Latest Enhancement Proposal and Validation Result

This script displays the latest enhancement proposal and its validation result from Neo4j.
"""

import os
import sys
import logging
from dotenv import load_dotenv

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

# Import Neo4j driver
from neo4j import GraphDatabase

def view_latest_proposal():
    """View the latest enhancement proposal and its validation result from Neo4j"""
    try:
        # Initialize Neo4j connection
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "password123")
        
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        logger.info("Connected to Neo4j database")
        
        with driver.session() as session:
            # Get the latest enhancement proposal (ID 24)
            proposal = session.run("""
                MATCH (p:EnhancementProposal) 
                WHERE ID(p) = 24
                RETURN ID(p) as id, p.enhancement_type as enhancement_type, p.standard_id as standard_id, 
                       p.enhanced_content as enhanced_content, p.reasoning as reasoning, p.status as status
            """).single()
            
            if not proposal:
                logger.error("Proposal with ID 24 not found")
                print("Proposal with ID 24 not found")
                return
            
            # Get the validation result for this proposal
            validation_result = session.run("""
                MATCH (v:ValidationResult) 
                WHERE toInteger(v.proposal_id) = 24
                RETURN ID(v) as id, v.proposal_id as proposal_id, v.status as status, 
                       v.overall_score as overall_score, v.feedback as feedback, v.modified_content as modified_content
                ORDER BY ID(v) DESC
                LIMIT 1
            """).single()
            
            # Display the enhancement proposal
            print("\n=== Enhancement Proposal ===")
            print(f"ID: {proposal['id']}")
            print(f"Type: {proposal.get('enhancement_type', 'N/A')}")
            print(f"Standard ID: {proposal.get('standard_id', 'N/A')}")
            print(f"Status: {proposal.get('status', 'N/A')}")
            
            print("\nEnhanced Content:")
            print(proposal.get('enhanced_content', 'N/A'))
            
            print("\nReasoning:")
            print(proposal.get('reasoning', 'N/A'))
            
            # Display the validation result
            if validation_result:
                print("\n=== Validation Result ===")
                print(f"ID: {validation_result['id']}")
                print(f"Proposal ID: {validation_result.get('proposal_id', 'N/A')}")
                print(f"Status: {validation_result.get('status', 'N/A')}")
                print(f"Overall Score: {validation_result.get('overall_score', 'N/A')}")
                
                print("\nFeedback:")
                print(validation_result.get('feedback', 'N/A'))
                
                print("\nModified Content:")
                print(validation_result.get('modified_content', 'N/A'))
            else:
                print("\nNo validation result found for this proposal")
            
    except Exception as e:
        logger.error(f"Error viewing latest proposal: {str(e)}", exc_info=True)
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
        view_latest_proposal()
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")
        sys.exit(1)
