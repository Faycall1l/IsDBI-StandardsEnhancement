#!/usr/bin/env python3
"""
Mock System Test Script

This script tests the Islamic Finance Standards AI system using a mock knowledge graph.
It validates the core functionality without requiring a Neo4j database connection.
"""

import os
import sys
import logging
from datetime import datetime

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the mock knowledge graph
from database.mock_knowledge_graph import MockKnowledgeGraph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("test_mock_system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_islamic_finance_standards():
    """Test the Islamic Finance Standards system with mock data"""
    logger.info("Starting Islamic Finance Standards System Test with Mock Data")
    
    try:
        # Initialize the mock knowledge graph
        kg = MockKnowledgeGraph()
        logger.info("Initialized mock knowledge graph")
        
        # Test 1: Create AAOIFI standards
        logger.info("Test 1: Creating AAOIFI standards")
        
        # Create FAS standards
        fas_ijarah_id = kg.create_standard(
            title="Ijarah and Ijarah Muntahia Bittamleek",
            standard_type="FAS",
            standard_number="8",
            publication_date="2020-01-01",
            description="This standard prescribes the accounting rules for Ijarah and Ijarah Muntahia Bittamleek transactions."
        )
        
        fas_murabaha_id = kg.create_standard(
            title="Murabaha and Other Deferred Payment Sales",
            standard_type="FAS",
            standard_number="28",
            publication_date="2019-01-01",
            description="This standard prescribes the accounting rules for Murabaha and other deferred payment sales."
        )
        
        # Create SS standards
        ss_ijarah_id = kg.create_standard(
            title="Ijarah and Ijarah Muntahia Bittamleek",
            standard_type="SS",
            standard_number="9",
            publication_date="2018-01-01",
            description="This standard prescribes the Shariah rules for Ijarah and Ijarah Muntahia Bittamleek transactions."
        )
        
        ss_murabaha_id = kg.create_standard(
            title="Murabaha",
            standard_type="SS",
            standard_number="8",
            publication_date="2017-01-01",
            description="This standard prescribes the Shariah rules for Murabaha transactions."
        )
        
        logger.info(f"Created 4 standards: 2 FAS and 2 SS")
        
        # Test 2: Create Islamic finance concepts
        logger.info("Test 2: Creating Islamic finance concepts")
        
        ijarah_concept_id = kg.create_concept(
            name="Ijarah",
            description="A lease contract where the lessor transfers the usufruct of an asset to the lessee for an agreed period against an agreed consideration."
        )
        
        ijarah_muntahia_concept_id = kg.create_concept(
            name="Ijarah Muntahia Bittamleek",
            description="A lease ending with ownership, where the lessor transfers ownership of the leased asset to the lessee at the end of the lease term."
        )
        
        murabaha_concept_id = kg.create_concept(
            name="Murabaha",
            description="A sale contract where the seller discloses the cost and profit margin to the buyer."
        )
        
        logger.info(f"Created 3 Islamic finance concepts")
        
        # Test 3: Create Shariah principles
        logger.info("Test 3: Creating Shariah principles")
        
        asset_ownership_id = kg.create_principle(
            name="Asset Ownership",
            description="In Islamic finance, transactions must be backed by real assets, not just monetary exchanges."
        )
        
        riba_prohibition_id = kg.create_principle(
            name="Prohibition of Riba",
            description="Interest (riba) is prohibited in all forms of transactions."
        )
        
        gharar_prohibition_id = kg.create_principle(
            name="Prohibition of Gharar",
            description="Excessive uncertainty or ambiguity in contracts is prohibited."
        )
        
        logger.info(f"Created 3 Shariah principles")
        
        # Test 4: Link standards to concepts
        logger.info("Test 4: Linking standards to concepts")
        
        # Link FAS Ijarah to concepts
        kg.link_standard_to_concept(fas_ijarah_id, ijarah_concept_id)
        kg.link_standard_to_concept(fas_ijarah_id, ijarah_muntahia_concept_id)
        
        # Link SS Ijarah to concepts
        kg.link_standard_to_concept(ss_ijarah_id, ijarah_concept_id)
        kg.link_standard_to_concept(ss_ijarah_id, ijarah_muntahia_concept_id)
        
        # Link FAS Murabaha to concepts
        kg.link_standard_to_concept(fas_murabaha_id, murabaha_concept_id)
        
        # Link SS Murabaha to concepts
        kg.link_standard_to_concept(ss_murabaha_id, murabaha_concept_id)
        
        logger.info(f"Created 6 relationships between standards and concepts")
        
        # Test 5: Link concepts to principles
        logger.info("Test 5: Linking concepts to principles")
        
        # Link Ijarah to principles
        kg.link_concept_to_principle(ijarah_concept_id, asset_ownership_id)
        kg.link_concept_to_principle(ijarah_concept_id, gharar_prohibition_id)
        
        # Link Ijarah Muntahia Bittamleek to principles
        kg.link_concept_to_principle(ijarah_muntahia_concept_id, asset_ownership_id)
        kg.link_concept_to_principle(ijarah_muntahia_concept_id, gharar_prohibition_id)
        
        # Link Murabaha to principles
        kg.link_concept_to_principle(murabaha_concept_id, asset_ownership_id)
        kg.link_concept_to_principle(murabaha_concept_id, riba_prohibition_id)
        
        logger.info(f"Created 6 relationships between concepts and principles")
        
        # Test 6: Create transaction types
        logger.info("Test 6: Creating transaction types")
        
        operating_ijarah_id = kg.create_transaction_type(
            name="Operating Ijarah",
            description="A lease where the lessor retains ownership of the asset after the lease term."
        )
        
        finance_ijarah_id = kg.create_transaction_type(
            name="Finance Ijarah",
            description="A lease where the lessor transfers ownership of the asset to the lessee at the end of the lease term."
        )
        
        commodity_murabaha_id = kg.create_transaction_type(
            name="Commodity Murabaha",
            description="A Murabaha transaction involving commodities, often used for liquidity management."
        )
        
        logger.info(f"Created 3 transaction types")
        
        # Test 7: Create validation rules
        logger.info("Test 7: Creating validation rules")
        
        ownership_rule_id = kg.create_validation_rule(
            name="Ownership Transfer Rule",
            description="The transfer of ownership in Ijarah Muntahia Bittamleek must be through a separate contract after the lease term ends.",
            rule_type="Shariah"
        )
        
        maintenance_rule_id = kg.create_validation_rule(
            name="Maintenance Responsibility Rule",
            description="In Ijarah, the lessor is responsible for major maintenance of the leased asset.",
            rule_type="Shariah"
        )
        
        disclosure_rule_id = kg.create_validation_rule(
            name="Cost Disclosure Rule",
            description="In Murabaha, the seller must disclose the original cost and profit margin to the buyer.",
            rule_type="Shariah"
        )
        
        logger.info(f"Created 3 validation rules")
        
        # Test 8: Create amendments
        logger.info("Test 8: Creating amendments")
        
        ijarah_amendment_id = kg.create_amendment(
            standard_id=fas_ijarah_id,
            amendment_type="CLARIFICATION",
            description="Clarification on the timing of ownership transfer in Ijarah Muntahia Bittamleek",
            content="The ownership transfer must occur through a separate contract after the lease term ends, not as part of the original lease contract.",
            effective_date="2022-01-01"
        )
        
        murabaha_amendment_id = kg.create_amendment(
            standard_id=fas_murabaha_id,
            amendment_type="ADDITION",
            description="Addition of guidance on digital Murabaha transactions",
            content="Digital Murabaha transactions must follow the same principles as traditional Murabaha, including the requirement for the seller to own the asset before selling it.",
            effective_date="2023-01-01"
        )
        
        logger.info(f"Created 2 amendments")
        
        # Test 9: Query the knowledge graph
        logger.info("Test 9: Querying the knowledge graph")
        
        # Get concepts for a standard
        ijarah_concepts = kg.get_concepts_for_standard(fas_ijarah_id)
        logger.info(f"Found {len(ijarah_concepts)} concepts for FAS Ijarah standard")
        
        # Get principles for a concept
        murabaha_principles = kg.get_principles_for_concept(murabaha_concept_id)
        logger.info(f"Found {len(murabaha_principles)} principles for Murabaha concept")
        
        # Get amendments for a standard
        ijarah_amendments = kg.get_amendments_for_standard(fas_ijarah_id)
        logger.info(f"Found {len(ijarah_amendments)} amendments for FAS Ijarah standard")
        
        # Test 10: Link related standards
        logger.info("Test 10: Linking related standards")
        
        # Link FAS Ijarah to SS Ijarah
        kg.link_standard_to_standard(fas_ijarah_id, ss_ijarah_id)
        
        # Link FAS Murabaha to SS Murabaha
        kg.link_standard_to_standard(fas_murabaha_id, ss_murabaha_id)
        
        logger.info(f"Created 2 relationships between related standards")
        
        # Test 11: Find paths between standards
        logger.info("Test 11: Finding paths between standards")
        
        paths = kg.find_path_between_standards(fas_ijarah_id, ss_ijarah_id)
        logger.info(f"Found {len(paths)} paths between FAS Ijarah and SS Ijarah standards")
        
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        # Close the knowledge graph connection
        if 'kg' in locals():
            kg.close()
        logger.info("Test script completed")

if __name__ == "__main__":
    test_islamic_finance_standards()
