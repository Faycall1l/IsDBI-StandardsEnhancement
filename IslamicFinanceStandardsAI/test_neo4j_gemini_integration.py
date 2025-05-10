#!/usr/bin/env python
"""
Neo4j Gemini Integration Test

This script tests the integration of Neo4j with Gemini for the Islamic Finance Standards Enhancement system.
It demonstrates using FAISS for RAG while storing enhancements in Neo4j.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

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
os.environ["GEMINI_API_KEY"] = "AIzaSyC_P-2Dl1fo_gvD2EM43tRCOWv6aS-u5c4"

# Import after setting environment variables
from utils.gemini_client import GeminiClient
from utils.gemini_embeddings import GeminiEmbeddings
from database.neo4j_vector_store import Neo4jVectorStore

class EnhancementProposal(BaseModel):
    """Simple model for an enhancement proposal"""
    standard_id: str
    enhancement_type: str
    title: str
    content: str
    reasoning: str

def test_neo4j_gemini_integration():
    """Test the integration of Neo4j with Gemini"""
    logger.info("Starting Neo4j Gemini integration test")
    
    # Initialize Gemini client
    gemini_client = GeminiClient(api_key=os.environ["GEMINI_API_KEY"])
    logger.info("Initialized Gemini client")
    
    # Initialize Gemini embeddings
    embeddings = GeminiEmbeddings(api_key=os.environ["GEMINI_API_KEY"])
    logger.info("Initialized Gemini embeddings")
    
    # Initialize Neo4j vector store
    try:
        vector_store = Neo4jVectorStore(
            embedding_function=embeddings,
            url=os.environ["NEO4J_URI"],
            username=os.environ["NEO4J_USER"],
            password=os.environ["NEO4J_PASSWORD"],
            index_name="islamic_finance_vector",
            node_label="EnhancementProposal",
            text_node_property="content",
            embedding_node_property="embedding"
        )
        logger.info("Initialized Neo4j vector store")
        
        # The vector index is created automatically during initialization
        logger.info("Vector store initialized with index: 'islamic_finance_vector'")
    except Exception as e:
        logger.error(f"Failed to initialize Neo4j vector store: {str(e)}")
        sys.exit(1)
    
    # Sample enhancement proposals
    proposals = [
        EnhancementProposal(
            standard_id="FAS-4",
            enhancement_type="DEFINITION",
            title="Enhanced Musharaka Definition",
            content="Musharaka is a form of partnership where two or more persons combine either their capital or labor together, to share the profits according to a pre-agreed ratio, while losses are shared strictly in proportion to capital contributions.",
            reasoning="The enhanced definition clarifies the profit and loss sharing mechanism, which is a key aspect of Musharaka that distinguishes it from conventional partnerships."
        ),
        EnhancementProposal(
            standard_id="FAS-4",
            enhancement_type="ACCOUNTING_TREATMENT",
            title="Improved Accounting Treatment for Diminishing Musharaka",
            content="In Diminishing Musharaka, the institution's share shall be recorded as a separate investment account and reduced periodically as per the agreed schedule of partner's purchase of the institution's share. Each reduction shall be recognized as a disposal of investment.",
            reasoning="This treatment provides clearer guidance on how to account for the gradual transfer of ownership in Diminishing Musharaka arrangements."
        ),
        EnhancementProposal(
            standard_id="FAS-4",
            enhancement_type="NEW_GUIDANCE",
            title="Digital Musharaka Arrangements",
            content="For Musharaka arrangements conducted through digital platforms, the same principles apply with additional documentation requirements to ensure the digital agreement constitutes a valid contract under Shariah. Smart contracts must include all essential elements of a traditional Musharaka agreement.",
            reasoning="This guidance addresses the emerging trend of digital Islamic finance products while ensuring Shariah compliance in the digital realm."
        )
    ]
    
    # Store proposals in Neo4j
    logger.info("Storing enhancement proposals in Neo4j")
    proposal_ids = []
    for proposal in proposals:
        # Prepare metadata
        metadata = {
            "standard_id": proposal.standard_id,
            "enhancement_type": proposal.enhancement_type,
            "title": proposal.title,
            "reasoning": proposal.reasoning
        }
        
        # Add to Neo4j
        ids = vector_store.add_texts([proposal.content], [metadata])
        proposal_id = ids[0] if ids else None
        
        if proposal_id:
            proposal_ids.append(proposal_id)
            logger.info(f"Stored proposal '{proposal.title}' with ID: {proposal_id}")
            
            # Create standard node if it doesn't exist
            with vector_store.driver.session() as session:
                # Check if standard exists
                query = """
                MATCH (s:Standard {id: $standard_id})
                RETURN id(s) AS standard_id
                """
                
                result = session.run(query, standard_id=proposal.standard_id)
                record = result.single()
                
                if record:
                    neo4j_standard_id = str(record["standard_id"])
                    logger.info(f"Found existing standard with ID: {neo4j_standard_id}")
                else:
                    # Create standard node
                    create_query = """
                    CREATE (s:Standard {
                        id: $standard_id,
                        type: $standard_type,
                        number: $standard_number
                    })
                    RETURN id(s) AS standard_id
                    """
                    
                    # Parse standard_id (e.g., "FAS-4" -> type="FAS", number="4")
                    parts = proposal.standard_id.split("-") if "-" in proposal.standard_id else [proposal.standard_id, "0"]
                    standard_type = parts[0]
                    standard_number = parts[1] if len(parts) > 1 else "0"
                    
                    result = session.run(
                        create_query,
                        standard_id=proposal.standard_id,
                        standard_type=standard_type,
                        standard_number=standard_number
                    )
                    
                    record = result.single()
                    neo4j_standard_id = str(record["standard_id"]) if record else None
                    logger.info(f"Created standard node with ID: {neo4j_standard_id}")
                
                # Link proposal to standard
                if neo4j_standard_id:
                    relationship_id = vector_store.link_document_to_node(
                        document_id=proposal_id,
                        node_id=neo4j_standard_id,
                        relationship_type="ENHANCES",
                        properties={"type": proposal.enhancement_type}
                    )
                    logger.info(f"Linked proposal {proposal_id} to standard {neo4j_standard_id}")
    
    # Test similarity search
    logger.info("Testing similarity search")
    search_query = "How does profit and loss sharing work in Musharaka?"
    search_results = vector_store.similarity_search_with_score(search_query, k=3)
    
    logger.info(f"Found {len(search_results)} similar documents for query: '{search_query}'")
    for i, (doc, score) in enumerate(search_results):
        logger.info(f"Result {i+1} (Score: {score}):")
        logger.info(f"Content: {doc.page_content}")
        logger.info(f"Metadata: {doc.metadata}")
    
    # Generate text with Gemini based on retrieved documents
    logger.info("Generating text with Gemini based on retrieved documents")
    
    if search_results:
        # Prepare context from search results
        context = "\n\n".join([doc.page_content for doc, _ in search_results])
        
        # Generate text
        prompt = f"""
        Context information:
        {context}
        
        Based on the above information, please explain how profit and loss sharing works in Musharaka arrangements 
        according to Islamic finance principles, and how this differs from conventional partnerships.
        """
        
        response = gemini_client.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=1000
        )
        
        logger.info("Gemini Response:")
        print("\n" + response + "\n")
    
    # Close Neo4j connection
    vector_store.close()
    logger.info("Closed Neo4j connection")
    
    logger.info("Neo4j Gemini integration test completed successfully")
    return proposal_ids, search_results

if __name__ == "__main__":
    try:
        proposal_ids, search_results = test_neo4j_gemini_integration()
        print("\nTest completed successfully!")
    except Exception as e:
        logger.error(f"Error in test: {str(e)}", exc_info=True)
        print(f"\nTest failed with error: {str(e)}")
        sys.exit(1)
