#!/usr/bin/env python
"""
Test Dual Storage Workflow

This script tests the full workflow of the Islamic Finance Standards Enhancement system
using FAISS for RAG and Neo4j for storing enhancements.
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

# Set environment variables for the test
os.environ["USE_NEO4J"] = "true"
os.environ["USE_GEMINI"] = "true"

# Set Neo4j credentials - these should match what was used in test_neo4j_rag.py
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
from utils.gemini_client import GeminiClient
from database.neo4j_vector_store import Neo4jVectorStore
from utils.gemini_embeddings import GeminiEmbeddings

def test_full_workflow():
    """Test the full workflow with FAISS for RAG and Neo4j for enhancements"""
    logger.info("Starting full workflow test with dual storage")
    
    # Initialize event bus
    event_bus = EventBus()
    
    # Initialize knowledge graph (using mock for simplicity)
    knowledge_graph = MockKnowledgeGraph()
    logger.info("Initialized mock knowledge graph")
    
    # Initialize Neo4j vector store
    try:
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "password123")
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        if not gemini_api_key:
            logger.error("GEMINI_API_KEY environment variable is not set")
            sys.exit(1)
        
        # Initialize Gemini embeddings
        embeddings = GeminiEmbeddings(api_key=gemini_api_key)
        logger.info("Initialized Gemini embeddings")
        
        # Initialize Neo4j vector store
        vector_store = Neo4jVectorStore(
            embedding_function=embeddings,
            url=neo4j_uri,
            username=neo4j_user,
            password=neo4j_password,
            index_name="islamic_finance_vector",
            node_label="Document",
            text_node_property="content",
            embedding_node_property="embedding"
        )
        logger.info("Initialized Neo4j vector store")
    except Exception as e:
        logger.error(f"Failed to initialize Neo4j vector store: {str(e)}")
        logger.warning("Continuing without Neo4j vector store")
    
    # Initialize agents
    document_agent = DocumentAgent(knowledge_graph)
    enhancement_agent = EnhancementAgent(knowledge_graph)
    validation_agent = ValidationAgent(knowledge_graph)
    
    logger.info("Initialized all agents")
    
    # Test document processing
    logger.info("Testing document processing")
    
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
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as temp_file:
        temp_file.write(sample_content)
        temp_file_path = temp_file.name
    
    # Process document
    document = document_agent.process_document(temp_file_path)
    
    # Get the standard ID from the knowledge graph (it's "0" in the mock knowledge graph)
    # In a real implementation, we would need to query the knowledge graph to find the standard ID
    standard_id = "0"
    
    # Clean up temporary file
    os.unlink(temp_file_path)
    logger.info(f"Processed document and created standard with ID: {standard_id}")
    
    # Generate enhancements
    logger.info("Generating enhancements")
    enhancement_proposals = enhancement_agent.generate_enhancements(standard_id)
    logger.info(f"Generated {len(enhancement_proposals)} enhancement proposals")
    
    # Store proposals in the knowledge graph for validation
    logger.info("Storing proposals in knowledge graph for validation")
    proposal_ids = []
    for i, proposal in enumerate(enhancement_proposals):
        # In a real implementation, the proposal would already be stored in the knowledge graph
        # by the enhancement agent. For this test, we'll store it manually.
        proposal_node_id = knowledge_graph.create_node(
            label="EnhancementProposal",
            properties={
                "standard_id": proposal.standard_id,
                "enhancement_type": proposal.enhancement_type,
                "target_id": proposal.target_id,
                "original_content": proposal.original_content,
                "enhanced_content": proposal.enhanced_content,
                "reasoning": proposal.reasoning,
                "references": proposal.references,
                "status": proposal.status,
                "proposal_id": f"proposal-{i}"
            }
        )
        proposal_ids.append(proposal_node_id)
        logger.info(f"Stored proposal in knowledge graph with ID: {proposal_node_id}")
    
    # Validate enhancements
    logger.info("Validating enhancements")
    validation_results = []
    for proposal_id in proposal_ids:
        validation_result = validation_agent.validate_proposal(proposal_id)
        validation_results.append(validation_result)
        logger.info(f"Validated proposal {proposal_id}: {validation_result.status}")
    
    # Print summary
    logger.info("=== Workflow Summary ===")
    logger.info(f"Standard ID: {standard_id}")
    logger.info(f"Total enhancement proposals: {len(enhancement_proposals)}")
    logger.info(f"Approved proposals: {sum(1 for r in validation_results if r.status == 'APPROVED')}")
    logger.info(f"Rejected proposals: {sum(1 for r in validation_results if r.status == 'REJECTED')}")
    logger.info(f"Proposals requiring revision: {sum(1 for r in validation_results if r.status == 'NEEDS_REVISION')}")
    
    # Close Neo4j connection if it was initialized
    if 'vector_store' in locals():
        vector_store.close()
        logger.info("Closed Neo4j connection")
    
    logger.info("Dual storage workflow test completed")
    
    return {
        "standard_id": standard_id,
        "enhancement_proposals": enhancement_proposals,
        "validation_results": validation_results
    }

if __name__ == "__main__":
    try:
        test_results = test_full_workflow()
        
        # Print enhancement proposals
        print("\nEnhancement Proposals:")
        for i, proposal in enumerate(test_results["enhancement_proposals"]):
            print(f"\nProposal {i+1}:")
            print(f"Type: {proposal.enhancement_type}")
            print(f"Standard ID: {proposal.standard_id}")
            print(f"Target ID: {proposal.target_id}")
            print(f"Enhanced Content: {proposal.enhanced_content[:200]}...")
        
        # Print validation results
        print("\nValidation Results:")
        for i, result in enumerate(test_results["validation_results"]):
            print(f"\nResult {i+1} for proposal: {result.proposal_id}")
            print(f"Status: {result.status}")
            if hasattr(result, 'feedback') and result.feedback:
                print(f"Feedback: {result.feedback[:200]}...")
            else:
                print("Feedback: Not available")
        
        print("\nTest completed successfully!")
    except Exception as e:
        logger.error(f"Error in test workflow: {str(e)}", exc_info=True)
        print(f"\nTest failed with error: {str(e)}")
        sys.exit(1)
