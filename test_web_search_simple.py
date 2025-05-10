#!/usr/bin/env python
"""
Simple Test for Web Search Functionality

This script tests the web retriever's ability to search for and retrieve
relevant Shariah standards from the internet.
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

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the web retriever directly
from IslamicFinanceStandardsAI.utils.web_retriever import WebRetriever

def test_web_search():
    """Test web search functionality"""
    try:
        # Initialize web retriever
        web_retriever = WebRetriever()
        logger.info("Initialized web retriever")
        
        # Test queries
        test_queries = [
            "What are the key principles of Musharaka in Islamic finance?",
            "How does AAOIFI define Sukuk?",
            "What are the Shariah requirements for Murabaha contracts?",
            "How are Diminishing Musharaka transactions structured according to Islamic standards?",
            "What are the accounting treatments for Ijarah according to FAS 8?"
        ]
        
        logger.info("Testing web search functionality")
        
        for query in test_queries:
            logger.info(f"\n\n===== Testing query: {query} =====")
            
            # Search for standards
            standards = web_retriever.search_standards(query, max_results=3)
            
            if standards:
                logger.info(f"Found {len(standards)} standards from web search")
                for i, standard in enumerate(standards):
                    logger.info(f"Standard {i+1}:")
                    logger.info(f"Title: {standard.get('title', 'N/A')}")
                    logger.info(f"Source: {standard.get('source', 'N/A')}")
                    logger.info(f"URL: {standard.get('url', 'N/A')}")
                    logger.info(f"Snippet: {standard.get('snippet', 'N/A')[:200]}...")
                    
                    # Try to retrieve content if URL is available
                    if "url" in standard and standard["url"]:
                        try:
                            logger.info(f"Retrieving content from {standard['url']}...")
                            content = web_retriever.retrieve_standard_content(standard["url"])
                            logger.info(f"Retrieved content length: {len(content)} characters")
                            logger.info(f"Content preview: {content[:200]}...")
                        except Exception as e:
                            logger.error(f"Error retrieving content from {standard['url']}: {str(e)}")
            else:
                logger.warning("No standards found from web search")
            
            logger.info("\n" + "="*50)
        
        logger.info("Web search test completed")
        
    except Exception as e:
        logger.error(f"Error testing web search: {str(e)}", exc_info=True)

if __name__ == "__main__":
    test_web_search()
