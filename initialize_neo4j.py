#!/usr/bin/env python
"""
Neo4j Database Initialization Script for Islamic Finance Standards Enhancement System

This script initializes the Neo4j database with sample data for Islamic finance standards,
including FAS 7 (Salam) and FAS 28 (Murabaha).
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import knowledge graph
from IslamicFinanceStandardsAI.database.knowledge_graph import KnowledgeGraph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize Neo4j database with sample data for Islamic finance standards"""
    try:
        # Connect to Neo4j
        kg = KnowledgeGraph()
        logger.info(f"Successfully connected to Neo4j at {kg.uri}")
        
        # Check if standards already exist
        existing_standards = kg.get_standards()
        if existing_standards:
            logger.info(f"Database already contains {len(existing_standards)} standards")
            for std in existing_standards:
                logger.info(f"  - {std.get('properties', {}).get('name', 'Unknown')}")
            return True
        
        # Create FAS 7 (Salam) standard
        fas7_id = kg.create_node("Standard", {
            "name": "FAS 7: Salam and Parallel Salam",
            "type": "FAS",
            "number": "7",
            "effective_date": "1998-01-01",
            "description": "Standard for Salam and Parallel Salam transactions"
        })
        logger.info(f"Created FAS 7 standard with ID: {fas7_id}")
        
        # Create FAS 28 (Murabaha) standard
        fas28_id = kg.create_node("Standard", {
            "name": "FAS 28: Murabaha and Other Deferred Payment Sales",
            "type": "FAS",
            "number": "28",
            "effective_date": "2004-01-01",
            "description": "Standard for Murabaha and other deferred payment sales"
        })
        logger.info(f"Created FAS 28 standard with ID: {fas28_id}")
        
        # Create related concepts
        salam_concept_id = kg.create_node("Concept", {
            "name": "Salam",
            "description": "A sale whereby the seller undertakes to supply specific goods to the buyer at a future date in exchange for an advanced price fully paid on spot."
        })
        logger.info(f"Created Salam concept with ID: {salam_concept_id}")
        
        murabaha_concept_id = kg.create_node("Concept", {
            "name": "Murabaha",
            "description": "A sale of goods at cost plus an agreed profit markup, where the seller must disclose the cost of the goods and the markup to the buyer."
        })
        logger.info(f"Created Murabaha concept with ID: {murabaha_concept_id}")
        
        # Create relationships between standards and concepts
        kg.create_relationship(fas7_id, salam_concept_id, "COVERS")
        kg.create_relationship(fas28_id, murabaha_concept_id, "COVERS")
        logger.info("Created relationships between standards and concepts")
        
        # Create definitions for FAS 7
        salam_def_id = kg.create_node("Definition", {
            "term": "Salam",
            "definition": "A sale whereby the seller undertakes to supply specific goods to the buyer at a future date in exchange for an advanced price fully paid on spot."
        })
        
        salam_capital_def_id = kg.create_node("Definition", {
            "term": "Salam Capital",
            "definition": "The amount paid by the buyer to the seller during the session of the contract."
        })
        
        parallel_salam_def_id = kg.create_node("Definition", {
            "term": "Parallel Salam",
            "definition": "A transaction where the bank enters into a second Salam contract with a third party to acquire goods with specifications similar to those specified in the first Salam contract."
        })
        
        # Link definitions to FAS 7
        kg.create_relationship(fas7_id, salam_def_id, "DEFINES")
        kg.create_relationship(fas7_id, salam_capital_def_id, "DEFINES")
        kg.create_relationship(fas7_id, parallel_salam_def_id, "DEFINES")
        logger.info("Created definitions for FAS 7")
        
        # Create definitions for FAS 28
        murabaha_def_id = kg.create_node("Definition", {
            "term": "Murabaha",
            "definition": "A sale of goods at cost plus an agreed profit markup, where the seller must disclose the cost of the goods and the markup to the buyer."
        })
        
        binding_promise_def_id = kg.create_node("Definition", {
            "term": "Binding Promise",
            "definition": "A promise that is legally enforceable according to the applicable laws and regulations."
        })
        
        # Link definitions to FAS 28
        kg.create_relationship(fas28_id, murabaha_def_id, "DEFINES")
        kg.create_relationship(fas28_id, binding_promise_def_id, "DEFINES")
        logger.info("Created definitions for FAS 28")
        
        # Create accounting treatments for FAS 7
        salam_capital_treatment_id = kg.create_node("AccountingTreatment", {
            "title": "Recognition of Salam Capital",
            "treatment": "Salam capital shall be recognized when it is paid to the seller, and shall be measured by the amount paid."
        })
        
        salam_receivables_treatment_id = kg.create_node("AccountingTreatment", {
            "title": "Measurement of Salam Receivables",
            "treatment": "Salam receivables shall be recognized at the end of the financial period at their cash equivalent value, i.e., the amount of cash that would be realized if the receivables were sold for cash."
        })
        
        # Link accounting treatments to FAS 7
        kg.create_relationship(fas7_id, salam_capital_treatment_id, "PRESCRIBES")
        kg.create_relationship(fas7_id, salam_receivables_treatment_id, "PRESCRIBES")
        logger.info("Created accounting treatments for FAS 7")
        
        # Create accounting treatments for FAS 28
        murabaha_recognition_treatment_id = kg.create_node("AccountingTreatment", {
            "title": "Recognition of Murabaha Assets",
            "treatment": "Assets available for Murabaha sale shall be recognized at the time of acquisition at their historical cost. Any decline in value before sale to the customer should be recognized as a loss."
        })
        
        murabaha_receivables_treatment_id = kg.create_node("AccountingTreatment", {
            "title": "Measurement of Murabaha Receivables",
            "treatment": "Murabaha receivables shall be recorded at their face value, and the profit on the transaction shall be recognized over the period of the contract using the effective profit rate method."
        })
        
        # Link accounting treatments to FAS 28
        kg.create_relationship(fas28_id, murabaha_recognition_treatment_id, "PRESCRIBES")
        kg.create_relationship(fas28_id, murabaha_receivables_treatment_id, "PRESCRIBES")
        logger.info("Created accounting treatments for FAS 28")
        
        # Create ambiguities for FAS 7
        delivery_risk_ambiguity_id = kg.create_node("Ambiguity", {
            "title": "Delivery Risk",
            "description": "The standard does not clearly address how to handle situations where there is partial delivery or delivery of goods with different specifications than agreed upon."
        })
        
        price_fluctuations_ambiguity_id = kg.create_node("Ambiguity", {
            "title": "Price Fluctuations",
            "description": "There is ambiguity regarding how to account for significant price fluctuations between the time of contract and the time of delivery."
        })
        
        # Link ambiguities to FAS 7
        kg.create_relationship(fas7_id, delivery_risk_ambiguity_id, "HAS_AMBIGUITY")
        kg.create_relationship(fas7_id, price_fluctuations_ambiguity_id, "HAS_AMBIGUITY")
        logger.info("Created ambiguities for FAS 7")
        
        # Create ambiguities for FAS 28
        ownership_risk_ambiguity_id = kg.create_node("Ambiguity", {
            "title": "Ownership Risk Period",
            "description": "The standard does not provide detailed guidance on accounting for risks during the period when the institution owns the asset before selling it to the customer."
        })
        
        agency_arrangements_ambiguity_id = kg.create_node("Ambiguity", {
            "title": "Agency Arrangements",
            "description": "There is ambiguity regarding the accounting treatment when the customer acts as an agent for the institution in purchasing the asset, particularly regarding the timing of recognition of ownership."
        })
        
        # Link ambiguities to FAS 28
        kg.create_relationship(fas28_id, ownership_risk_ambiguity_id, "HAS_AMBIGUITY")
        kg.create_relationship(fas28_id, agency_arrangements_ambiguity_id, "HAS_AMBIGUITY")
        logger.info("Created ambiguities for FAS 28")
        
        # Create relationship between FAS 7 and FAS 28 (they are related standards)
        kg.create_relationship(fas7_id, fas28_id, "RELATED_TO")
        kg.create_relationship(fas28_id, fas7_id, "RELATED_TO")
        logger.info("Created relationships between standards")
        
        logger.info("Successfully initialized Neo4j database with sample data")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Neo4j database: {str(e)}")
        return False
    finally:
        # Close Neo4j connection
        if 'kg' in locals():
            kg.close()

if __name__ == "__main__":
    success = initialize_database()
    sys.exit(0 if success else 1)
