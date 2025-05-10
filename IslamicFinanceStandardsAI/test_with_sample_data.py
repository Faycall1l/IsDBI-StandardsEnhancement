#!/usr/bin/env python3
"""
Test Script with Sample Data

This script tests the Islamic Finance Standards AI system with a sample PDF document
using the mock knowledge graph to avoid Neo4j dependency.
"""

import os
import sys
import logging
from datetime import datetime

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import system components
from database.mock_knowledge_graph import MockKnowledgeGraph
from agents.document_agent.document_agent import DocumentAgent
from utils.document_parser import PDFParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("test_with_sample_data.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Monkey patch the document agent to use our mock knowledge graph
import types
from database.knowledge_graph import KnowledgeGraph
original_init = KnowledgeGraph.__init__

def mock_init(self):
    """Mock initialization that doesn't require Neo4j"""
    self.logger = logging.getLogger(__name__)
    self.logger.info("Using mock knowledge graph implementation")
    
    # Use the mock implementation
    mock_kg = MockKnowledgeGraph()
    
    # Copy all attributes and methods from mock to self
    for attr_name in dir(mock_kg):
        if not attr_name.startswith('__'):
            attr = getattr(mock_kg, attr_name)
            if callable(attr):
                setattr(self, attr_name, types.MethodType(attr.__func__, self))
            else:
                setattr(self, attr_name, attr)

# Apply the monkey patch
KnowledgeGraph.__init__ = mock_init

def test_with_sample_document():
    """Test the system with a sample document"""
    logger.info("Starting test with sample document")
    
    try:
        # Initialize the knowledge graph
        kg = KnowledgeGraph()
        logger.info("Initialized knowledge graph (mock)")
        
        # Initialize document agent
        document_agent = DocumentAgent(kg)
        logger.info("Initialized document agent")
        
        # Process a sample document
        sample_doc_path = "/Users/faycalamrouche/Desktop/IsDBI/Resources/FI5F55_1_Musharaka Financing(4).PDF"
        logger.info(f"Processing sample document: {sample_doc_path}")
        
        # Process the document
        standard_doc = document_agent.process_document(sample_doc_path)
        
        # Log the results
        logger.info(f"Successfully processed document: {standard_doc.title}")
        logger.info(f"Standard type: {standard_doc.standard_type}")
        logger.info(f"Standard number: {standard_doc.standard_number}")
        logger.info(f"Extracted {len(standard_doc.definitions)} definitions")
        logger.info(f"Extracted {len(standard_doc.accounting_treatments)} accounting treatments")
        logger.info(f"Extracted {len(standard_doc.transaction_structures)} transaction structures")
        logger.info(f"Identified {len(standard_doc.ambiguities)} ambiguities")
        
        # Print some examples of extracted information
        if standard_doc.definitions:
            logger.info("\nSample definitions:")
            for i, definition in enumerate(standard_doc.definitions[:3]):
                logger.info(f"{i+1}. {definition.term}: {definition.definition[:100]}...")
        
        if standard_doc.accounting_treatments:
            logger.info("\nSample accounting treatments:")
            for i, treatment in enumerate(standard_doc.accounting_treatments[:3]):
                logger.info(f"{i+1}. {treatment.title}: {treatment.description[:100]}...")
        
        if standard_doc.transaction_structures:
            logger.info("\nSample transaction structures:")
            for i, structure in enumerate(standard_doc.transaction_structures[:3]):
                logger.info(f"{i+1}. {structure.title}: {structure.description[:100]}...")
        
        logger.info("Test completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise
    finally:
        logger.info("Test script completed")

if __name__ == "__main__":
    test_with_sample_document()
