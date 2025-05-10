#!/usr/bin/env python
"""
Hybrid Workflow Test

This script demonstrates the full workflow of the Islamic Finance Standards Enhancement system
using the hybrid storage approach that combines:
1. FAISS for efficient RAG operations
2. Neo4j for knowledge graph storage with semantic capabilities
3. The existing multi-agent architecture (Document, Enhancement, Validation agents)
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

# Set environment variables for Neo4j and Gemini
os.environ["USE_NEO4J"] = "true"
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USER"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "password123"
os.environ["USE_GEMINI"] = "true"
os.environ["USE_WEB_RETRIEVAL"] = "true"

# Make sure the Gemini API key is set
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    # This is a placeholder - you should use your actual Gemini API key
    os.environ["GEMINI_API_KEY"] = "AIzaSyC_P-2Dl1fo_gvD2EM43tRCOWv6aS-u5c4"
    print("Warning: Using placeholder Gemini API key. Please set your actual API key in the environment.")

# Import after setting environment variables
from database.knowledge_graph import KnowledgeGraph
from database.mock_knowledge_graph import MockKnowledgeGraph
from agents.document_agent.document_agent import DocumentAgent
from agents.enhancement_agent.enhancement_agent import EnhancementAgent
from agents.validation_agent.validation_agent import ValidationAgent
from utils.event_bus import EventBus, EventType
from integration.hybrid_storage_manager import get_hybrid_storage_manager

def test_hybrid_workflow():
    """Test the hybrid workflow with FAISS for RAG and Neo4j for knowledge graph"""
    logger.info("Starting hybrid workflow test")
    
    # Initialize event bus
    event_bus = EventBus()
    logger.info("Initialized event bus")
    
    # Initialize Neo4j knowledge graph
    try:
        knowledge_graph = KnowledgeGraph()
        logger.info("Initialized Neo4j knowledge graph")
    except Exception as e:
        logger.warning(f"Failed to initialize Neo4j knowledge graph: {str(e)}. Falling back to mock.")
        knowledge_graph = MockKnowledgeGraph()
        logger.info("Initialized mock knowledge graph as fallback")
    
    # Initialize hybrid storage manager
    hybrid_storage = get_hybrid_storage_manager(event_bus=event_bus)
    logger.info("Initialized hybrid storage manager")
    
    # Initialize agents
    document_agent = DocumentAgent(knowledge_graph)
    enhancement_agent = EnhancementAgent(knowledge_graph)
    validation_agent = ValidationAgent(knowledge_graph)
    
    logger.info("Initialized all agents")
    
    # Subscribe to events
    event_bus.subscribe(EventType.ENHANCEMENT_CREATED, lambda event: logger.info(f"Event received: {event['type']} - {event['payload']}"))
    event_bus.subscribe(EventType.VALIDATION_COMPLETED, lambda event: logger.info(f"Event received: {event['type']} - {event['payload']}"))
    
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
    
    # Store enhancements using hybrid storage
    logger.info("Storing enhancements using hybrid storage")
    storage_results = []
    for proposal in enhancement_proposals:
        result = hybrid_storage.store_enhancement(proposal, knowledge_graph)
        storage_results.append(result)
        logger.info(f"Stored proposal in hybrid storage: KG ID: {result['kg_id']}, Neo4j ID: {result['neo4j_id']}")
    
    # Validate enhancements
    logger.info("Validating enhancements")
    validation_results = []
    for result in storage_results:
        if result["kg_id"]:
            validation_result = validation_agent.validate_proposal(result["kg_id"])
            
            # Store validation result in hybrid storage
            validation_id = hybrid_storage.store_validation_result(validation_result, knowledge_graph)
            
            validation_results.append(validation_result)
            logger.info(f"Validated proposal {result['kg_id']}: {validation_result.status}")
    
    # Test semantic search with hybrid storage
    logger.info("Testing semantic search with hybrid storage")
    
    # Test query 1
    query = "How does Musharaka profit sharing work?"
    logger.info(f"Searching for: '{query}'")
    
    # Get similar documents
    docs = hybrid_storage.get_similar_documents(query)
    logger.info(f"Found {len(docs)} relevant documents")
    
    # Generate response
    response = hybrid_storage.generate_response(query)
    logger.info(f"Generated response for query: '{query}'")
    logger.info(f"Response: {response[:100]}..." if len(response) > 100 else f"Response: {response}")
    
    # Test query with web search enhancement
    logger.info("\nTesting semantic search with web retrieval enhancement")
    query = "What are the Shariah requirements for Diminishing Musharaka?"
    logger.info(f"Searching for: '{query}'")
    
    # Get similar documents with web search
    docs = hybrid_storage.get_similar_documents(query, use_web=True)
    logger.info(f"Found {len(docs)} relevant documents (including web results)")
    
    # Generate response
    response = hybrid_storage.generate_response(query, use_web=True)
    logger.info(f"Generated response for query: '{query}'")
    logger.info(f"Response: {response[:200]}..." if len(response) > 200 else f"Response: {response}")
    
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
    hybrid_storage.close()
    logger.info("Closed all connections")
    
    logger.info("Hybrid workflow test completed")
    
    return {
        "standard_id": standard_id,
        "enhancement_proposals": enhancement_proposals,
        "storage_results": storage_results,
        "validation_results": validation_results
    }

if __name__ == "__main__":
    try:
        test_results = test_hybrid_workflow()
        
        # Print enhancement proposals
        print("\nEnhancement Proposals:")
        for i, proposal in enumerate(test_results["enhancement_proposals"]):
            print(f"\nProposal {i+1}:")
            print(f"Type: {proposal.enhancement_type}")
            print(f"Standard ID: {proposal.standard_id}")
            print(f"Target ID: {proposal.target_id}")
            print(f"Enhanced Content: {proposal.enhanced_content[:200]}...")
        
        print("\nTest completed successfully!")
    except Exception as e:
        logger.error(f"Error in test workflow: {str(e)}", exc_info=True)
        print(f"\nTest failed with error: {str(e)}")
        sys.exit(1)
