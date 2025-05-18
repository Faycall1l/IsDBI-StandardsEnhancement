#!/usr/bin/env python
"""
Neo4j Database Reset Script for Islamic Finance Standards Enhancement System

This script resets and initializes the Neo4j database with the correct schema and sample data.
It attempts multiple connection configurations to ensure successful connection.
"""

import os
import sys
import logging
import time
from neo4j import GraphDatabase, basic_auth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Neo4j connection configurations to try
NEO4J_CONFIGS = [
    {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "neo4j"},
    {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "password"},
]

def try_connect():
    """Try different connection configurations until one works"""
    for config in NEO4J_CONFIGS:
        try:
            logger.info(f"Trying to connect to Neo4j with URI: {config['uri']}, user: {config['user']}")
            driver = GraphDatabase.driver(
                config['uri'],
                auth=basic_auth(config['user'], config['password'])
            )
            # Test connection
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                record = result.single()
                if record and record["test"] == 1:
                    logger.info(f"Successfully connected to Neo4j with config: {config}")
                    return driver, config
        except Exception as e:
            logger.warning(f"Failed to connect with config {config}: {str(e)}")
    
    return None, None

def reset_database(driver):
    """Reset the Neo4j database by deleting all nodes and relationships"""
    try:
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Successfully reset Neo4j database")
            return True
    except Exception as e:
        logger.error(f"Failed to reset Neo4j database: {str(e)}")
        return False

def initialize_schema(driver):
    """Initialize the Neo4j database schema with constraints and indexes"""
    try:
        with driver.session() as session:
            # Create constraints for unique standard numbers
            session.run("""
            CREATE CONSTRAINT standard_number_type_unique IF NOT EXISTS
            FOR (s:Standard) 
            REQUIRE (s.type, s.number) IS UNIQUE
            """)
            
            # Create indexes for faster lookups
            session.run("CREATE INDEX standard_name_idx IF NOT EXISTS FOR (s:Standard) ON (s.name)")
            session.run("CREATE INDEX concept_name_idx IF NOT EXISTS FOR (c:Concept) ON (c.name)")
            session.run("CREATE INDEX definition_term_idx IF NOT EXISTS FOR (d:Definition) ON (d.term)")
            
            logger.info("Successfully initialized Neo4j schema")
            return True
    except Exception as e:
        logger.error(f"Failed to initialize Neo4j schema: {str(e)}")
        return False

def create_sample_data(driver):
    """Create sample data in the Neo4j database"""
    try:
        with driver.session() as session:
            # Create FAS 7 (Salam) standard
            session.run("""
            CREATE (s:Standard {
                name: 'FAS 7: Salam and Parallel Salam',
                type: 'FAS',
                number: '7',
                effective_date: '1998-01-01',
                description: 'Standard for Salam and Parallel Salam transactions'
            })
            """)
            
            # Create FAS 28 (Murabaha) standard
            session.run("""
            CREATE (s:Standard {
                name: 'FAS 28: Murabaha and Other Deferred Payment Sales',
                type: 'FAS',
                number: '28',
                effective_date: '2004-01-01',
                description: 'Standard for Murabaha and other deferred payment sales'
            })
            """)
            
            # Create concepts and link to standards
            session.run("""
            MATCH (fas7:Standard {type: 'FAS', number: '7'})
            CREATE (c:Concept {
                name: 'Salam',
                description: 'A sale whereby the seller undertakes to supply specific goods to the buyer at a future date in exchange for an advanced price fully paid on spot.'
            })
            CREATE (fas7)-[:COVERS]->(c)
            """)
            
            session.run("""
            MATCH (fas28:Standard {type: 'FAS', number: '28'})
            CREATE (c:Concept {
                name: 'Murabaha',
                description: 'A sale of goods at cost plus an agreed profit markup, where the seller must disclose the cost of the goods and the markup to the buyer.'
            })
            CREATE (fas28)-[:COVERS]->(c)
            """)
            
            # Create definitions for FAS 7
            session.run("""
            MATCH (fas7:Standard {type: 'FAS', number: '7'})
            CREATE (d1:Definition {
                term: 'Salam',
                definition: 'A sale whereby the seller undertakes to supply specific goods to the buyer at a future date in exchange for an advanced price fully paid on spot.'
            })
            CREATE (d2:Definition {
                term: 'Salam Capital',
                definition: 'The amount paid by the buyer to the seller during the session of the contract.'
            })
            CREATE (d3:Definition {
                term: 'Parallel Salam',
                definition: 'A transaction where the bank enters into a second Salam contract with a third party to acquire goods with specifications similar to those specified in the first Salam contract.'
            })
            CREATE (fas7)-[:DEFINES]->(d1)
            CREATE (fas7)-[:DEFINES]->(d2)
            CREATE (fas7)-[:DEFINES]->(d3)
            """)
            
            # Create definitions for FAS 28
            session.run("""
            MATCH (fas28:Standard {type: 'FAS', number: '28'})
            CREATE (d1:Definition {
                term: 'Murabaha',
                definition: 'A sale of goods at cost plus an agreed profit markup, where the seller must disclose the cost of the goods and the markup to the buyer.'
            })
            CREATE (d2:Definition {
                term: 'Binding Promise',
                definition: 'A promise that is legally enforceable according to the applicable laws and regulations.'
            })
            CREATE (fas28)-[:DEFINES]->(d1)
            CREATE (fas28)-[:DEFINES]->(d2)
            """)
            
            # Create accounting treatments for FAS 7
            session.run("""
            MATCH (fas7:Standard {type: 'FAS', number: '7'})
            CREATE (t1:AccountingTreatment {
                title: 'Recognition of Salam Capital',
                treatment: 'Salam capital shall be recognized when it is paid to the seller, and shall be measured by the amount paid.'
            })
            CREATE (t2:AccountingTreatment {
                title: 'Measurement of Salam Receivables',
                treatment: 'Salam receivables shall be recognized at the end of the financial period at their cash equivalent value, i.e., the amount of cash that would be realized if the receivables were sold for cash.'
            })
            CREATE (fas7)-[:PRESCRIBES]->(t1)
            CREATE (fas7)-[:PRESCRIBES]->(t2)
            """)
            
            # Create accounting treatments for FAS 28
            session.run("""
            MATCH (fas28:Standard {type: 'FAS', number: '28'})
            CREATE (t1:AccountingTreatment {
                title: 'Recognition of Murabaha Assets',
                treatment: 'Assets available for Murabaha sale shall be recognized at the time of acquisition at their historical cost. Any decline in value before sale to the customer should be recognized as a loss.'
            })
            CREATE (t2:AccountingTreatment {
                title: 'Measurement of Murabaha Receivables',
                treatment: 'Murabaha receivables shall be recorded at their face value, and the profit on the transaction shall be recognized over the period of the contract using the effective profit rate method.'
            })
            CREATE (fas28)-[:PRESCRIBES]->(t1)
            CREATE (fas28)-[:PRESCRIBES]->(t2)
            """)
            
            # Create ambiguities for FAS 7
            session.run("""
            MATCH (fas7:Standard {type: 'FAS', number: '7'})
            CREATE (a1:Ambiguity {
                title: 'Delivery Risk',
                description: 'The standard does not clearly address how to handle situations where there is partial delivery or delivery of goods with different specifications than agreed upon.'
            })
            CREATE (a2:Ambiguity {
                title: 'Price Fluctuations',
                description: 'There is ambiguity regarding how to account for significant price fluctuations between the time of contract and the time of delivery.'
            })
            CREATE (fas7)-[:HAS_AMBIGUITY]->(a1)
            CREATE (fas7)-[:HAS_AMBIGUITY]->(a2)
            """)
            
            # Create ambiguities for FAS 28
            session.run("""
            MATCH (fas28:Standard {type: 'FAS', number: '28'})
            CREATE (a1:Ambiguity {
                title: 'Ownership Risk Period',
                description: 'The standard does not provide detailed guidance on accounting for risks during the period when the institution owns the asset before selling it to the customer.'
            })
            CREATE (a2:Ambiguity {
                title: 'Agency Arrangements',
                description: 'There is ambiguity regarding the accounting treatment when the customer acts as an agent for the institution in purchasing the asset, particularly regarding the timing of recognition of ownership.'
            })
            CREATE (fas28)-[:HAS_AMBIGUITY]->(a1)
            CREATE (fas28)-[:HAS_AMBIGUITY]->(a2)
            """)
            
            # Create relationship between standards
            session.run("""
            MATCH (fas7:Standard {type: 'FAS', number: '7'})
            MATCH (fas28:Standard {type: 'FAS', number: '28'})
            CREATE (fas7)-[:RELATED_TO]->(fas28)
            CREATE (fas28)-[:RELATED_TO]->(fas7)
            """)
            
            logger.info("Successfully created sample data in Neo4j database")
            return True
    except Exception as e:
        logger.error(f"Failed to create sample data: {str(e)}")
        return False

def verify_data(driver):
    """Verify that the data was properly created in the Neo4j database"""
    try:
        with driver.session() as session:
            # Count standards
            result = session.run("MATCH (s:Standard) RETURN count(s) as count")
            standard_count = result.single()["count"]
            
            # Count concepts
            result = session.run("MATCH (c:Concept) RETURN count(c) as count")
            concept_count = result.single()["count"]
            
            # Count definitions
            result = session.run("MATCH (d:Definition) RETURN count(d) as count")
            definition_count = result.single()["count"]
            
            # Count accounting treatments
            result = session.run("MATCH (t:AccountingTreatment) RETURN count(t) as count")
            treatment_count = result.single()["count"]
            
            # Count ambiguities
            result = session.run("MATCH (a:Ambiguity) RETURN count(a) as count")
            ambiguity_count = result.single()["count"]
            
            logger.info(f"Data verification: {standard_count} standards, {concept_count} concepts, {definition_count} definitions, {treatment_count} treatments, {ambiguity_count} ambiguities")
            
            # Check if we have the expected number of nodes
            return standard_count >= 2 and concept_count >= 2 and definition_count >= 5 and treatment_count >= 4 and ambiguity_count >= 4
    except Exception as e:
        logger.error(f"Failed to verify data: {str(e)}")
        return False

def update_env_file(config):
    """Update the .env file with the correct Neo4j credentials"""
    try:
        env_content = f"""
# Neo4j Configuration
NEO4J_URI={config['uri']}
NEO4J_USER={config['user']}
NEO4J_PASSWORD={config['password']}

# Existing environment variables
"""
        
        # Read existing .env file if it exists
        if os.path.exists('/Users/faycalamrouche/Desktop/IsDBI/.env'):
            with open('/Users/faycalamrouche/Desktop/IsDBI/.env', 'r') as f:
                existing_content = f.read()
                
            # Extract lines that don't start with NEO4J
            lines = existing_content.split('\n')
            non_neo4j_lines = [line for line in lines if not line.strip().startswith('NEO4J_')]
            
            # Add non-Neo4j lines to our new content
            env_content += '\n'.join(non_neo4j_lines)
        
        # Write the updated .env file
        with open('/Users/faycalamrouche/Desktop/IsDBI/.env', 'w') as f:
            f.write(env_content)
            
        logger.info(f"Updated .env file with Neo4j credentials: {config}")
        return True
    except Exception as e:
        logger.error(f"Failed to update .env file: {str(e)}")
        return False

def main():
    """Main function to reset and initialize the Neo4j database"""
    # Try to connect to Neo4j
    driver, config = try_connect()
    if not driver:
        logger.error("Failed to connect to Neo4j with any configuration")
        return 1
    
    try:
        # Reset the database
        if not reset_database(driver):
            logger.error("Failed to reset the database")
            return 1
        
        # Initialize the schema
        if not initialize_schema(driver):
            logger.error("Failed to initialize the schema")
            return 1
        
        # Create sample data
        if not create_sample_data(driver):
            logger.error("Failed to create sample data")
            return 1
        
        # Verify the data
        if not verify_data(driver):
            logger.error("Data verification failed")
            return 1
        
        # Update the .env file with the correct Neo4j credentials
        if not update_env_file(config):
            logger.error("Failed to update .env file")
            return 1
        
        logger.info("Successfully reset and initialized Neo4j database")
        return 0
    finally:
        # Close the driver
        if driver:
            driver.close()

if __name__ == "__main__":
    sys.exit(main())
