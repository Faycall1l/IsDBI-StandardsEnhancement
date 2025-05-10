#!/usr/bin/env python3
"""
Test script for Gemini integration in the Islamic Finance Standards Enhancement system.

This script tests the Gemini API integration as an alternative to OpenAI.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import system components
from utils.gemini_client import GeminiClient
from utils.web_retriever import get_web_retriever, get_claim_classifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gemini_test_log.txt'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Set environment variables for testing
os.environ["USE_GEMINI"] = "true"
os.environ["GEMINI_API_KEY"] = "AIzaSyAND61l0rHF-p2UQg28RSMe62DZgQOHsLE"

def test_gemini_text_generation():
    """Test basic text generation with Gemini"""
    logger.info("Testing Gemini text generation")
    
    try:
        client = GeminiClient(api_key=os.environ["GEMINI_API_KEY"])
        
        prompt = "Explain the concept of Musharaka in Islamic finance in 3-4 sentences."
        response = client.generate_text(prompt)
        
        logger.info(f"Gemini response: {response}")
        return response
    except Exception as e:
        logger.error(f"Error testing Gemini text generation: {str(e)}")
        return None

def test_claim_classification():
    """Test claim classification with Gemini"""
    logger.info("Testing claim classification with Gemini")
    
    try:
        claim_classifier = get_claim_classifier()
        
        text = """
        Musharaka contracts require that profits be distributed according to pre-agreed ratios, 
        while losses must be shared in proportion to capital contribution. This is a fundamental 
        principle in Islamic finance. I believe the standard could be improved by adding more 
        examples of modern applications of Musharaka in project financing.
        """
        
        classification = claim_classifier.classify_claims(text)
        
        logger.info(f"Classified {len(classification['verifiable'])} verifiable claims and "
                   f"{len(classification['subjective'])} subjective suggestions")
        
        if classification['verifiable']:
            logger.info(f"Sample verifiable claims: {classification['verifiable']}")
        
        if classification['subjective']:
            logger.info(f"Sample subjective suggestions: {classification['subjective']}")
            
        return classification
    except Exception as e:
        logger.error(f"Error testing claim classification: {str(e)}")
        return None

def test_claim_verification():
    """Test claim verification with Gemini"""
    logger.info("Testing claim verification with Gemini")
    
    try:
        client = GeminiClient(api_key=os.environ["GEMINI_API_KEY"])
        
        claim = "In Musharaka contracts, losses must be shared in proportion to capital contribution"
        context = """
        Musharaka (Partnership)
        
        1. Definition:
        Musharaka is a partnership contract between two or more parties where all partners contribute capital 
        and share profits according to agreed ratios, while losses are shared in proportion to capital contribution.
        
        2. Types of Musharaka:
        2.1 Permanent Musharaka: A partnership that continues for an extended period.
        2.2 Diminishing Musharaka: A partnership where one partner gradually buys the share of the other partner.
        
        3. Profit Distribution:
        3.1 Profits must be distributed according to pre-agreed ratios.
        3.2 It is not permissible to fix a lump sum profit for any partner.
        
        4. Loss Sharing:
        4.1 Losses must be shared in proportion to capital contribution.
        4.2 Any condition contrary to this principle is void in Shariah.
        """
        
        verification_result = client.verify_claim(claim, context)
        
        logger.info(f"Verification result: {verification_result['verified']} "
                   f"(Confidence: {verification_result['confidence']})")
        logger.info(f"Evidence: {verification_result['evidence']}")
        
        return verification_result
    except Exception as e:
        logger.error(f"Error testing claim verification: {str(e)}")
        return None

def main():
    """Main test function"""
    logger.info("Starting Gemini integration test")
    
    # Make sure environment variables are set
    logger.info(f"USE_GEMINI: {os.environ.get('USE_GEMINI')}")
    logger.info(f"GEMINI_API_KEY: {os.environ.get('GEMINI_API_KEY', 'Not set')[:10]}...")
    
    try:
        # Test basic text generation
        test_gemini_text_generation()
        
        # Test claim classification
        test_claim_classification()
        
        # Test claim verification
        test_claim_verification()
        
        logger.info("All Gemini integration tests completed")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    main()
