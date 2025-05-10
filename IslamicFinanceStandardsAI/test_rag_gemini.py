#!/usr/bin/env python3
"""
RAG Engine Test with Gemini Embeddings

This script tests the Retrieval-Augmented Generation (RAG) engine using Gemini embeddings
for the Islamic Finance Standards Enhancement system.
"""

import os
import sys
import logging
from datetime import datetime
import time

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the RAG engine and related components
from utils.rag_engine import get_rag_engine, get_claim_verifier
from utils.gemini_client import GeminiClient
from utils.gemini_embeddings import GeminiEmbeddings
from models.document_schema import StandardDocument

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("gemini_rag_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set environment variables for testing
os.environ["USE_GEMINI"] = "true"

# Ensure we're using Gemini for embeddings
def create_direct_rag_engine():
    """Create a RAG engine directly with Gemini embeddings"""
    from langchain.vectorstores import FAISS
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    
    # Get Gemini API key
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        logger.error("GEMINI_API_KEY environment variable is not set")
        return None
    
    # Initialize Gemini embeddings
    embeddings = GeminiEmbeddings(api_key=gemini_api_key)
    
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    # Create an empty vector store
    vector_store = FAISS.from_texts(["Islamic finance test document"], embeddings)
    
    return {
        "embeddings": embeddings,
        "vector_store": vector_store,
        "text_splitter": text_splitter
    }

def test_rag_engine_with_gemini():
    """Test the RAG engine with Gemini embeddings"""
    logger.info("Starting RAG Engine Test with Gemini Embeddings")
    
    try:
        # Check if Gemini API key is set
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            logger.error("GEMINI_API_KEY environment variable is not set")
            print("Please set the GEMINI_API_KEY environment variable")
            return
        
        # Initialize the Gemini client
        gemini_client = GeminiClient(api_key=gemini_api_key)
        logger.info("Initialized Gemini client")
        
        # Initialize the RAG components directly
        rag_components = create_direct_rag_engine()
        if not rag_components:
            logger.error("Failed to initialize RAG components")
            return
        
        embeddings = rag_components["embeddings"]
        vector_store = rag_components["vector_store"]
        text_splitter = rag_components["text_splitter"]
        
        logger.info("Initialized RAG components with Gemini embeddings")
        
        # Test 1: Add a sample document to the vector store
        logger.info("Test 1: Adding sample document to vector store")
        
        # Sample Islamic finance text
        sample_text = """
        Musharaka is a form of partnership where two or more persons combine either their capital or labor together, to share the profits, enjoying similar rights and liabilities.

        Key characteristics of Musharaka:
        1. All partners contribute capital and have the right to participate in management
        2. Profits are shared according to a pre-agreed ratio
        3. Losses are shared strictly in proportion to capital contributions
        4. The liability of partners is typically unlimited and joint

        In modern Islamic banking, Musharaka is used for:
        - Project financing
        - Real estate development
        - Working capital financing
        - Import financing

        Diminishing Musharaka (Musharaka Mutanaqisah) is a form where one partner gradually buys out the other partner's share over time, eventually becoming the sole owner of the asset.

        Shariah requirements for valid Musharaka:
        - Clear agreement on profit-sharing ratios
        - No guaranteed returns for any partner
        - Capital should be known and specified at the time of contract
        - Partners must be capable of being agents for each other
        """
        
        # Add the sample text to the vector store
        metadata = {
            "title": "Musharaka Financing",
            "source": "Islamic Finance Standards",
            "date": datetime.now().isoformat()
        }
        
        # Split the text into chunks
        chunks = text_splitter.split_text(sample_text)
        
        # Add metadata to each chunk
        texts_with_metadata = [
            (chunk, metadata) for chunk in chunks
        ]
        
        # Add to vector store
        vector_store.add_texts([t[0] for t in texts_with_metadata], [t[1] for t in texts_with_metadata])
        logger.info(f"Added {len(chunks)} chunks to the vector store")
        
        # Test 2: Retrieve relevant documents for a query
        logger.info("Test 2: Retrieving relevant documents for a query")
        query = "How are profits and losses shared in Musharaka?"
        
        # Get query embedding
        query_embedding = embeddings.embed_query(query)
        
        # Search the vector store
        retrieved_docs = vector_store.similarity_search_by_vector(query_embedding, k=3)
        logger.info(f"Retrieved {len(retrieved_docs)} documents for the query")
        
        # Display retrieved documents
        print("\nRetrieved Documents:")
        for i, doc in enumerate(retrieved_docs):
            print(f"\nDocument {i+1}:")
            print(f"Content: {doc.page_content[:150]}...")
            print(f"Metadata: {doc.metadata}")
            print(f"Score: {doc.metadata.get('score', 'N/A')}")
        
        # Test 3: Format the retrieved documents into a context
        logger.info("Test 3: Formatting retrieved documents into context")
        
        context = "\n\n".join([f"Document {i+1}:\n{doc.page_content}" for i, doc in enumerate(retrieved_docs)])
        logger.info(f"Generated context with {len(context)} characters")
        
        print("\nFormatted Context:")
        print(context[:500] + "..." if len(context) > 500 else context)
        
        # Test 4: Verify claims using the Gemini client directly
        logger.info("Test 4: Verifying claims with Gemini")
        
        # We'll use the Gemini client directly instead of the claim verifier
        gemini_client = GeminiClient(api_key=gemini_api_key)
        
        # Sample claims to verify
        claims = [
            "In Musharaka, profits are shared according to a pre-agreed ratio.",
            "In Musharaka, losses are shared equally among all partners.",
            "Diminishing Musharaka is where one partner gradually buys out the other partner's share."
        ]
        
        print("\nClaim Verification Results:")
        for claim in claims:
            print(f"\nVerifying claim: {claim}")
            # Verify the claim against the context
            result = gemini_client.verify_claim(claim, context)
            print(f"Verified: {result['verified']}")
            print(f"Confidence: {result['confidence']}")
            print(f"Evidence: {result['evidence'][:200]}..." if len(result['evidence']) > 200 else result['evidence'])
        
        # Test 5: Generate text with Gemini
        logger.info("Test 5: Generating text with Gemini")
        prompt = f"""
        Based on the following information about Musharaka:
        
        {sample_text}
        
        Explain how Diminishing Musharaka can be used in home financing.
        """
        
        response = gemini_client.generate_text(
            prompt=prompt,
            temperature=0.2,
            max_tokens=500
        )
        
        print("\nGemini Response on Diminishing Musharaka in Home Financing:")
        print(response)
        
        logger.info("All RAG engine tests with Gemini completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("Test script completed")

if __name__ == "__main__":
    test_rag_engine_with_gemini()
