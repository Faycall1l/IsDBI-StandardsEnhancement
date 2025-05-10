#!/usr/bin/env python3
"""
Neo4j Vector Store Test with Gemini Embeddings

This script tests the integration of Neo4j with the Gemini-powered RAG system
for the Islamic Finance Standards Enhancement system.
"""

import os
import sys
import logging
from datetime import datetime
import time

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the Neo4j vector store and related components
from database.neo4j_vector_store import Neo4jVectorStore
from utils.gemini_embeddings import GeminiEmbeddings
from utils.gemini_client import GeminiClient
from langchain.docstore.document import Document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("neo4j_rag_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set environment variables for testing
os.environ["USE_GEMINI"] = "true"

def test_neo4j_vector_store():
    """Test the Neo4j vector store with Gemini embeddings"""
    logger.info("Starting Neo4j Vector Store Test with Gemini Embeddings")
    
    try:
        # Check if Gemini API key is set
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            logger.error("GEMINI_API_KEY environment variable is not set")
            print("Please set the GEMINI_API_KEY environment variable")
            return
        
        # Use local Neo4j instance
        neo4j_uri = "bolt://localhost:7687"
        neo4j_user = "neo4j"
        neo4j_password = "password123"  # Updated password
        
        # Log the connection details
        logger.info(f"Using local Neo4j connection: {neo4j_uri}")
        print(f"\nConnecting to Neo4j at: {neo4j_uri}")
        
        # Initialize the Gemini client
        gemini_client = GeminiClient(api_key=gemini_api_key)
        logger.info("Initialized Gemini client")
        
        # Initialize Gemini embeddings
        embeddings = GeminiEmbeddings(api_key=gemini_api_key)
        logger.info("Initialized Gemini embeddings")
        
        # Initialize the Neo4j vector store
        vector_store = Neo4jVectorStore(
            embedding_function=embeddings,
            url=neo4j_uri,
            username=neo4j_user,
            password=neo4j_password,
            index_name="islamic_finance_vector",
            node_label="Document",
            text_node_property="text",
            embedding_node_property="embedding"
        )
        logger.info("Initialized Neo4j vector store")
        
        # Test 1: Add documents to the vector store
        logger.info("Test 1: Adding documents to the vector store")
        
        # Sample Islamic finance texts
        texts = [
            """
            Musharaka is a form of partnership where two or more persons combine either their capital or labor together, to share the profits, enjoying similar rights and liabilities.
            
            Key characteristics of Musharaka:
            1. All partners contribute capital and have the right to participate in management
            2. Profits are shared according to a pre-agreed ratio
            3. Losses are shared strictly in proportion to capital contributions
            4. The liability of partners is typically unlimited and joint
            """,
            
            """
            Diminishing Musharaka (Musharaka Mutanaqisah) is a form where one partner gradually buys out the other partner's share over time, eventually becoming the sole owner of the asset.
            
            In modern Islamic banking, Musharaka is used for:
            - Project financing
            - Real estate development
            - Working capital financing
            - Import financing
            """,
            
            """
            Mudaraba is a partnership where one partner (Rab-ul-Mal) provides the capital while the other (Mudarib) provides expertise and management.
            
            Key characteristics of Mudaraba:
            1. The capital provider does not have the right to participate in management
            2. Profits are shared according to a pre-agreed ratio
            3. Losses are borne entirely by the capital provider, while the manager loses their time and effort
            4. The liability of the capital provider is limited to their investment
            """,
            
            """
            Ijara is a lease contract where the lessor transfers the usufruct of an asset to the lessee for an agreed period against an agreed consideration.
            
            Key characteristics of Ijara:
            1. The lessor must own the asset throughout the lease period
            2. The asset must have a usufruct that can be enjoyed by the lessee
            3. The rental amount and period must be clearly specified
            4. The lessee is responsible for ordinary maintenance, while the lessor is responsible for major maintenance
            """
        ]
        
        # Add metadata to each text
        metadatas = [
            {
                "title": "Musharaka Financing",
                "source": "Islamic Finance Standards",
                "standard_type": "FAS",
                "standard_number": "4",
                "date": datetime.now().isoformat()
            },
            {
                "title": "Diminishing Musharaka",
                "source": "Islamic Finance Standards",
                "standard_type": "FAS",
                "standard_number": "4",
                "date": datetime.now().isoformat()
            },
            {
                "title": "Mudaraba Financing",
                "source": "Islamic Finance Standards",
                "standard_type": "FAS",
                "standard_number": "3",
                "date": datetime.now().isoformat()
            },
            {
                "title": "Ijara Financing",
                "source": "Islamic Finance Standards",
                "standard_type": "FAS",
                "standard_number": "8",
                "date": datetime.now().isoformat()
            }
        ]
        
        # Add documents to the vector store
        document_ids = vector_store.add_texts(texts, metadatas)
        logger.info(f"Added {len(document_ids)} documents to the vector store")
        print(f"\nAdded document IDs: {document_ids}")
        
        # Test 2: Perform similarity search
        logger.info("Test 2: Performing similarity search")
        query = "How are profits and losses shared in Musharaka?"
        
        # Search for similar documents
        results = vector_store.similarity_search_with_score(query, k=2)
        logger.info(f"Found {len(results)} similar documents")
        
        # Display search results
        print("\nSimilarity Search Results:")
        for i, (doc, score) in enumerate(results):
            print(f"\nResult {i+1} (Score: {score}):")
            print(f"Title: {doc.metadata.get('title', 'Unknown')}")
            print(f"Source: {doc.metadata.get('source', 'Unknown')}")
            print(f"Standard: {doc.metadata.get('standard_type', '')} {doc.metadata.get('standard_number', '')}")
            print(f"Content: {doc.page_content[:150]}...")
        
        # Test 3: Create a standard node in Neo4j and link documents to it
        logger.info("Test 3: Creating a standard node and linking documents")
        
        # Create a standard node using the Neo4j driver directly
        with vector_store.driver.session() as session:
            # Create a standard node
            create_query = """
            CREATE (s:Standard {
                title: $title,
                standard_type: $standard_type,
                standard_number: $standard_number,
                publication_date: $publication_date,
                description: $description
            })
            RETURN id(s) AS standard_id
            """
            
            result = session.run(
                create_query,
                title="Musharaka Financing",
                standard_type="FAS",
                standard_number="4",
                publication_date="2020-01-01",
                description="Standard on Musharaka Financing"
            )
            
            standard_id = str(result.single()["standard_id"])
            logger.info(f"Created standard node with ID: {standard_id}")
            print(f"\nCreated standard node with ID: {standard_id}")
            
            # Link the first two documents (Musharaka-related) to the standard
            for i in range(2):
                relationship_id = vector_store.link_document_to_node(
                    document_id=document_ids[i],
                    node_id=standard_id,
                    relationship_type="DESCRIBES",
                    properties={"created_at": datetime.now().isoformat()}
                )
                logger.info(f"Created relationship with ID: {relationship_id}")
                print(f"Linked document {document_ids[i]} to standard {standard_id}")
        
        # Test 4: Get documents for a standard
        logger.info("Test 4: Getting documents for a standard")
        
        # Get documents for the standard
        documents = vector_store.get_documents_for_node(standard_id, relationship_type="DESCRIBES")
        logger.info(f"Found {len(documents)} documents for standard {standard_id}")
        
        # Display documents
        print(f"\nDocuments for Standard {standard_id}:")
        for i, doc in enumerate(documents):
            print(f"\nDocument {i+1}:")
            print(f"Title: {doc.metadata.get('title', 'Unknown')}")
            print(f"Content: {doc.page_content[:150]}...")
        
        # Test 5: Generate text with Gemini based on the retrieved documents
        logger.info("Test 5: Generating text with Gemini based on retrieved documents")
        
        # Combine document contents
        context = "\n\n".join([doc.page_content for doc in documents])
        
        # Generate text with Gemini
        prompt = f"""
        Based on the following information about Musharaka:
        
        {context}
        
        Explain how Musharaka differs from conventional partnerships in terms of profit and loss sharing.
        """
        
        response = gemini_client.generate_text(
            prompt=prompt,
            temperature=0.2,
            max_tokens=500
        )
        
        print("\nGemini Response on Musharaka vs. Conventional Partnerships:")
        print(response)
        
        logger.info("All Neo4j vector store tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Close the vector store connection
        if 'vector_store' in locals():
            vector_store.close()
        logger.info("Test script completed")

if __name__ == "__main__":
    test_neo4j_vector_store()
