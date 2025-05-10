#!/usr/bin/env python
"""
Integrated Workflow Test

This script tests the full workflow of the Islamic Finance Standards Enhancement system
using both FAISS for RAG and Neo4j for storing enhancements.
"""

import os
import sys
import logging
import tempfile
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set environment variables for the test
os.environ["USE_NEO4J"] = "true"
os.environ["USE_GEMINI"] = "true"
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USER"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "password123"

# Import after setting environment variables
from database.knowledge_graph import KnowledgeGraph
from database.mock_knowledge_graph import MockKnowledgeGraph
from agents.document_agent.document_agent import DocumentAgent
from agents.enhancement_agent.enhancement_agent import EnhancementAgent
from agents.validation_agent.validation_agent import ValidationAgent
from utils.event_bus import EventBus
from integration.dual_storage_integration import get_dual_storage_manager

def test_integrated_workflow():
    """Test the integrated workflow with FAISS for RAG and Neo4j for enhancements"""
    logger.info("Starting integrated workflow test with dual storage")
    
    # Initialize event bus
    event_bus = EventBus()
    
    # Initialize knowledge graph (using mock for simplicity)
    knowledge_graph = MockKnowledgeGraph()
    logger.info("Initialized mock knowledge graph")
    
    # Initialize dual storage manager
    dual_storage = get_dual_storage_manager()
    logger.info("Initialized dual storage manager")
    
    # Initialize agents
    document_agent = DocumentAgent(knowledge_graph)
    enhancement_agent = EnhancementAgent(knowledge_graph)
    validation_agent = ValidationAgent(knowledge_graph)
    
    logger.info("Initialized all agents")
    
    # Test document processing
    logger.info("Processing document")
    
    # Sample FAS 4 (Musharaka) content
    sample_content = """
    Financial Accounting Standard 4
    Musharaka Financing
    
    1. Scope
    This standard applies to Musharaka financing transactions carried out by Islamic financial institutions.
    
    2. Definitions
    Musharaka is a form of partnership where two or more persons combine either their capital or labor together, to share the profits, enjoying similar rights and liabilities.
    
    3. Accounting Treatment
    3.1 The institution's share in Musharaka capital shall be recognized when it is paid to the partner or made available in the Musharaka account.
    3.2 Profits shall be recognized based on the agreed profit-sharing ratio.
    3.3 Losses shall be recognized strictly in proportion to the capital contributions.
    
    4. Transaction Structure
    4.1 Permanent Musharaka: Partners contribute capital with the intention of maintaining the partnership indefinitely.
    4.2 Diminishing Musharaka: One partner gradually purchases the other partner's share over time.
    """
    
    # Create a temporary file for the document
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as temp_file:
        temp_file.write(sample_content)
        temp_file_path = temp_file.name
    
    # Process document
    document = document_agent.process_document(temp_file_path)
    
    # Get the standard ID from the knowledge graph (it's "0" in the mock knowledge graph)
    standard_id = "0"
    
    # Clean up temporary file
    os.unlink(temp_file_path)
    logger.info(f"Processed document and created standard with ID: {standard_id}")
    
    # Generate enhancements
    logger.info("Generating enhancements")
    enhancement_proposals = enhancement_agent.generate_enhancements(standard_id)
    logger.info(f"Generated {len(enhancement_proposals)} enhancement proposals")
    
    # Store enhancements in both storage systems
    logger.info("Storing enhancements in both storage systems")
    storage_results = []
    for proposal in enhancement_proposals:
        result = dual_storage.store_enhancement(proposal, knowledge_graph)
        storage_results.append(result)
        logger.info(f"Stored proposal in knowledge graph with ID: {result['kg_id']} and Neo4j ID: {result['neo4j_id']}")
    
    # Validate enhancements
    logger.info("Validating enhancements")
    validation_results = []
    for result in storage_results:
        if result["kg_id"]:
            validation_result = validation_agent.validate_proposal(result["kg_id"])
            validation_results.append(validation_result)
            logger.info(f"Validated proposal {result['kg_id']}: {validation_result.status}")
    
    # Test semantic search using both FAISS and Neo4j
    logger.info("Testing semantic search with both FAISS and Neo4j")
    search_query = "How does Musharaka profit sharing work?"
    search_results = dual_storage.retrieve_similar_enhancements(search_query, top_k=3)
    
    logger.info(f"Found {len(search_results)} relevant documents for query: '{search_query}'")
    for i, result in enumerate(search_results):
        logger.info(f"Result {i+1} from {result['source']} (Score: {result['score']:.4f})")
        logger.info(f"Content: {result['content'][:100]}...")
    
    # Print summary
    logger.info("=== Workflow Summary ===")
    logger.info(f"Standard ID: {standard_id}")
    logger.info(f"Total enhancement proposals: {len(enhancement_proposals)}")
    logger.info(f"Proposals stored in knowledge graph: {sum(1 for r in storage_results if r['kg_id'])}")
    logger.info(f"Proposals stored in Neo4j: {sum(1 for r in storage_results if r['neo4j_id'])}")
    logger.info(f"Approved proposals: {sum(1 for r in validation_results if r.status == 'APPROVED')}")
    logger.info(f"Rejected proposals: {sum(1 for r in validation_results if r.status == 'REJECTED')}")
    logger.info(f"Proposals requiring revision: {sum(1 for r in validation_results if r.status == 'NEEDS_REVISION')}")
    
    # Close connections
    dual_storage.close()
    logger.info("Closed all connections")
    
    logger.info("Integrated workflow test completed")
    
    return {
        "standard_id": standard_id,
        "enhancement_proposals": enhancement_proposals,
        "storage_results": storage_results,
        "validation_results": validation_results,
        "search_results": search_results
    }

if __name__ == "__main__":
    try:
        test_results = test_integrated_workflow()
        
        # Print enhancement proposals
        print("\nEnhancement Proposals:")
        for i, proposal in enumerate(test_results["enhancement_proposals"]):
            print(f"\nProposal {i+1}:")
            print(f"Type: {proposal.enhancement_type}")
            print(f"Standard ID: {proposal.standard_id}")
            print(f"Target ID: {proposal.target_id}")
            print(f"Enhanced Content: {proposal.enhanced_content[:200]}...")
        
        # Print search results
        print("\nSearch Results:")
        for i, result in enumerate(test_results["search_results"]):
            print(f"\nResult {i+1} from {result['source']} (Score: {result['score']:.4f})")
            print(f"Content: {result['content'][:200]}...")
        
        print("\nTest completed successfully!")
    except Exception as e:
        logger.error(f"Error in test workflow: {str(e)}", exc_info=True)
        print(f"\nTest failed with error: {str(e)}")
        sys.exit(1)
