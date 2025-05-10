#!/usr/bin/env python3
"""
Knowledge Graph Test Script

This script tests the core functionality of the knowledge graph component:
1. Creating nodes for standards, concepts, principles
2. Creating relationships between nodes
3. Querying the graph
"""

import os
import sys
import logging
from datetime import datetime

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the knowledge graph
from database.knowledge_graph import KnowledgeGraph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("test_knowledge_graph.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_knowledge_graph():
    """Test the core functionality of the knowledge graph"""
    logger.info("Starting Knowledge Graph Test")
    
    try:
        # Initialize the knowledge graph
        kg = KnowledgeGraph()
        logger.info("Initialized knowledge graph")
        
        # Test 1: Create a standard node
        logger.info("Test 1: Creating a standard node")
        standard_id = kg.create_node(
            label="Standard",
            properties={
                "title": "Ijarah and Ijarah Muntahia Bittamleek",
                "standard_type": "FAS",
                "standard_number": "8",
                "publication_date": "2020-01-01"
            }
        )
        logger.info(f"Created standard node with ID: {standard_id}")
        
        # Test 2: Create a concept node
        logger.info("Test 2: Creating a concept node")
        concept_id = kg.create_concept(
            name="Ijarah",
            description="A lease contract where the lessor transfers the usufruct of an asset to the lessee for an agreed period against an agreed consideration."
        )
        logger.info(f"Created concept node with ID: {concept_id}")
        
        # Test 3: Create a principle node
        logger.info("Test 3: Creating a principle node")
        principle_id = kg.create_principle(
            name="Asset Ownership",
            description="In Islamic finance, transactions must be backed by real assets, not just monetary exchanges."
        )
        logger.info(f"Created principle node with ID: {principle_id}")
        
        # Test 4: Link standard to concept
        logger.info("Test 4: Linking standard to concept")
        relationship_id = kg.link_standard_to_concept(standard_id, concept_id)
        logger.info(f"Created relationship with ID: {relationship_id}")
        
        # Test 5: Link concept to principle
        logger.info("Test 5: Linking concept to principle")
        relationship_id = kg.link_concept_to_principle(concept_id, principle_id)
        logger.info(f"Created relationship with ID: {relationship_id}")
        
        # Test 6: Query concepts for a standard
        logger.info("Test 6: Querying concepts for a standard")
        concepts = kg.get_concepts_for_standard(standard_id)
        logger.info(f"Found {len(concepts)} concepts for standard")
        
        # Test 7: Query principles for a concept
        logger.info("Test 7: Querying principles for a concept")
        principles = kg.get_principles_for_concept(concept_id)
        logger.info(f"Found {len(principles)} principles for concept")
        
        # Test 8: Create a transaction type
        logger.info("Test 8: Creating a transaction type")
        transaction_id = kg.create_transaction_type(
            name="Ijarah Muntahia Bittamleek",
            description="A lease ending with ownership, where the lessor transfers ownership of the leased asset to the lessee at the end of the lease term."
        )
        logger.info(f"Created transaction type with ID: {transaction_id}")
        
        # Test 9: Create a validation rule
        logger.info("Test 9: Creating a validation rule")
        rule_id = kg.create_validation_rule(
            name="Ownership Transfer Rule",
            description="The transfer of ownership in Ijarah Muntahia Bittamleek must be through a separate contract after the lease term ends.",
            rule_type="Shariah"
        )
        logger.info(f"Created validation rule with ID: {rule_id}")
        
        # Test 10: Create an amendment
        logger.info("Test 10: Creating an amendment")
        amendment_id = kg.create_amendment(
            standard_id=standard_id,
            amendment_type="CLARIFICATION",
            description="Clarification on the timing of ownership transfer in Ijarah Muntahia Bittamleek",
            content="The ownership transfer must occur through a separate contract after the lease term ends, not as part of the original lease contract.",
            effective_date="2022-01-01"
        )
        logger.info(f"Created amendment with ID: {amendment_id}")
        
        # Test 11: Search for nodes
        logger.info("Test 11: Searching for nodes")
        results = kg.search_nodes(
            label="Concept",
            properties={"name": "Ijarah"}
        )
        logger.info(f"Found {len(results)} nodes matching search criteria")
        
        # Test 12: Get related nodes
        logger.info("Test 12: Getting related nodes")
        related_nodes = kg.get_related_nodes(standard_id)
        logger.info(f"Found {len(related_nodes)} nodes related to standard")
        
        logger.info("All knowledge graph tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        # Close the knowledge graph connection
        if 'kg' in locals():
            kg.close()
        logger.info("Test script completed")

if __name__ == "__main__":
    test_knowledge_graph()
