#!/usr/bin/env python
"""
Test Web Search Integration with RAG Engine

This script tests the integration of web search functionality with the RAG engine
to retrieve relevant Shariah standards from the internet.
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

# Set environment variables for Neo4j and Gemini
os.environ["USE_NEO4J"] = "true"
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USER"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "password123"
os.environ["USE_GEMINI"] = "true"
os.environ["USE_WEB_RETRIEVAL"] = "true"

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the RAG engine and web retriever
from IslamicFinanceStandardsAI.utils.rag_engine import get_rag_engine
from IslamicFinanceStandardsAI.utils.web_retriever import get_web_retriever

def test_web_search():
    """Test web search integration with RAG engine"""
    try:
        # Get the RAG engine
        rag_engine = get_rag_engine()
        if not rag_engine:
            logger.error("Failed to get RAG engine")
            return
        
        # Get the web retriever
        web_retriever = get_web_retriever()
        if not web_retriever:
            logger.error("Failed to get web retriever")
            return
        
        # Test queries
        test_queries = [
            "What are the key principles of Musharaka in Islamic finance?",
            "How does AAOIFI define Sukuk?",
            "What are the Shariah requirements for Murabaha contracts?",
            "How are Diminishing Musharaka transactions structured according to Islamic standards?",
            "What are the accounting treatments for Ijarah according to FAS 8?"
        ]
        
        logger.info("Testing web search integration with RAG engine")
        
        for query in test_queries:
            logger.info(f"\n\n===== Testing query: {query} =====")
            
            # First, test direct web search
            logger.info("Testing direct web search:")
            standards = web_retriever.search_standards(query, max_results=3)
            
            if standards:
                logger.info(f"Found {len(standards)} standards from web search")
                for i, standard in enumerate(standards):
                    logger.info(f"Standard {i+1}:")
                    logger.info(f"Title: {standard.get('title', 'N/A')}")
                    logger.info(f"Source: {standard.get('source', 'N/A')}")
                    logger.info(f"URL: {standard.get('url', 'N/A')}")
                    logger.info(f"Snippet: {standard.get('snippet', 'N/A')[:200]}...")
            else:
                logger.warning("No standards found from direct web search")
            
            # Now, test RAG engine with web search
            logger.info("\nTesting RAG engine with web search:")
            context = rag_engine.get_retrieval_context(query, k=3, use_web=True)
            
            if context:
                logger.info("Retrieved context from RAG engine with web search:")
                logger.info(context[:500] + "..." if len(context) > 500 else context)
            else:
                logger.warning("No context retrieved from RAG engine with web search")
            
            # Generate a response using the RAG engine
            logger.info("\nGenerating response with RAG context:")
            
            # Prepare the prompt
            prompt = f"""
            Query: {query}
            
            Please provide a comprehensive answer to this query about Islamic finance, 
            focusing on Shariah compliance and standards. Base your answer on the 
            provided context and your knowledge of Islamic finance principles.
            
            Context:
            {context}
            """
            
            # Generate response
            try:
                if hasattr(rag_engine, "gemini_client") and rag_engine.gemini_client:
                    response = rag_engine.gemini_client.generate_text(prompt)
                    logger.info(f"Generated response: {response[:500]}..." if len(response) > 500 else response)
                else:
                    logger.error("Gemini client not initialized in RAG engine")
            except Exception as e:
                logger.error(f"Error generating response: {str(e)}")
            
            logger.info("\n" + "="*50)
        
        logger.info("Web search integration test completed")
        
    except Exception as e:
        logger.error(f"Error testing web search: {str(e)}", exc_info=True)

if __name__ == "__main__":
    test_web_search()
