#!/usr/bin/env python
"""
Initialize Database

This script initializes the Neo4j database with sample data for the Islamic Finance
Standards Enhancement System. It creates standards, relationships, and other necessary
data structures for the system to work properly.
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from neo4j import GraphDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Neo4j connection parameters
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")

class DatabaseInitializer:
    """Initialize the Neo4j database with sample data."""
    
    def __init__(self):
        """Initialize the database initializer."""
        self.driver = None
        
    def connect(self):
        """Connect to Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD)
            )
            logger.info(f"Connected to Neo4j at {NEO4J_URI}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            return False
            
    def close(self):
        """Close the Neo4j connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
            
    def create_constraints(self):
        """Create necessary constraints in the database."""
        with self.driver.session() as session:
            # Create constraint on Standard.id
            try:
                session.run("CREATE CONSTRAINT standard_id IF NOT EXISTS FOR (s:Standard) REQUIRE s.id IS UNIQUE")
                logger.info("Created constraint on Standard.id")
            except Exception as e:
                logger.warning(f"Could not create constraint on Standard.id: {e}")
                
            # Create constraint on EnhancementProposal.id
            try:
                session.run("CREATE CONSTRAINT proposal_id IF NOT EXISTS FOR (p:EnhancementProposal) REQUIRE p.id IS UNIQUE")
                logger.info("Created constraint on EnhancementProposal.id")
            except Exception as e:
                logger.warning(f"Could not create constraint on EnhancementProposal.id: {e}")
                
            # Create constraint on ValidationResult.id
            try:
                session.run("CREATE CONSTRAINT validation_id IF NOT EXISTS FOR (v:ValidationResult) REQUIRE v.id IS UNIQUE")
                logger.info("Created constraint on ValidationResult.id")
            except Exception as e:
                logger.warning(f"Could not create constraint on ValidationResult.id: {e}")
                
            # Create constraint on RegulatoryUpdate.id
            try:
                session.run("CREATE CONSTRAINT update_id IF NOT EXISTS FOR (u:RegulatoryUpdate) REQUIRE u.id IS UNIQUE")
                logger.info("Created constraint on RegulatoryUpdate.id")
            except Exception as e:
                logger.warning(f"Could not create constraint on RegulatoryUpdate.id: {e}")
    
    def create_standards(self):
        """Create sample standards in the database."""
        standards = [
            {
                "id": "FAS28",
                "name": "Financial Accounting Standard 28",
                "title": "Murabaha and Other Deferred Payment Sales",
                "issuer": "AAOIFI",
                "issue_date": "2020-01-01",
                "effective_date": "2021-01-01",
                "status": "active",
                "description": "This standard prescribes the accounting rules for recognition, measurement, presentation, and disclosure of Murabaha and other deferred payment sales transactions."
            },
            {
                "id": "FAS7",
                "name": "Financial Accounting Standard 7",
                "title": "Salam and Parallel Salam",
                "issuer": "AAOIFI",
                "issue_date": "2010-01-01",
                "effective_date": "2011-01-01",
                "status": "active",
                "description": "This standard prescribes the accounting rules for Salam and Parallel Salam transactions, including recognition, measurement, presentation, and disclosure."
            },
            {
                "id": "FAS4",
                "name": "Financial Accounting Standard 4",
                "title": "Musharaka Financing",
                "issuer": "AAOIFI",
                "issue_date": "2008-01-01",
                "effective_date": "2009-01-01",
                "status": "active",
                "description": "This standard prescribes the accounting rules for Musharaka financing transactions."
            }
        ]
        
        with self.driver.session() as session:
            for standard in standards:
                try:
                    session.run("""
                    MERGE (s:Standard {id: $id})
                    SET s.name = $name,
                        s.title = $title,
                        s.issuer = $issuer,
                        s.issue_date = $issue_date,
                        s.effective_date = $effective_date,
                        s.status = $status,
                        s.description = $description
                    """, **standard)
                    logger.info(f"Created standard: {standard['id']}")
                except Exception as e:
                    logger.error(f"Error creating standard {standard['id']}: {e}")
    
    def create_relationships(self):
        """Create relationships between standards."""
        relationships = [
            ("FAS28", "RELATED_TO", "FAS7", {"type": "complementary", "description": "Both standards deal with deferred payment sales"}),
            ("FAS7", "RELATED_TO", "FAS4", {"type": "complementary", "description": "Both standards deal with financing methods"}),
            ("FAS28", "RELATED_TO", "FAS4", {"type": "complementary", "description": "Both standards deal with financing methods"})
        ]
        
        with self.driver.session() as session:
            for source, rel_type, target, properties in relationships:
                try:
                    session.run("""
                    MATCH (s1:Standard {id: $source})
                    MATCH (s2:Standard {id: $target})
                    MERGE (s1)-[r:RELATED_TO]->(s2)
                    SET r.type = $properties.type,
                        r.description = $properties.description
                    """, source=source, target=target, properties=properties)
                    logger.info(f"Created relationship: {source} -> {target}")
                except Exception as e:
                    logger.error(f"Error creating relationship {source} -> {target}: {e}")
    
    def create_enhancement_proposals(self):
        """Create sample enhancement proposals."""
        proposals = [
            {
                "id": "EP001",
                "title": "Clarification on Murabaha Profit Recognition",
                "description": "Proposal to clarify the timing of profit recognition in Murabaha transactions",
                "standard_id": "FAS28",
                "section_id": "4.2",
                "current_text": "Profits on Murabaha transactions should be recognized over the period of the contract.",
                "proposed_text": "Profits on Murabaha transactions should be recognized over the period of the contract using the effective profit rate method.",
                "rationale": "The current text does not specify the method of profit recognition, leading to inconsistent practices.",
                "status": "under_review",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "created_by": "enhancement_team_enhancement_agent_1",
                "team_id": "enhancement_team"
            },
            {
                "id": "EP002",
                "title": "Enhanced Disclosure Requirements for Salam",
                "description": "Proposal to enhance disclosure requirements for Salam transactions",
                "standard_id": "FAS7",
                "section_id": "5.3",
                "current_text": "Entities should disclose the amount of Salam financing at the end of the financial period.",
                "proposed_text": "Entities should disclose the amount of Salam financing at the end of the financial period, including a breakdown by commodity type, maturity profile, and any provisions for impairment.",
                "rationale": "The current disclosure requirements are insufficient for users to assess the risks associated with Salam financing.",
                "status": "draft",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "created_by": "enhancement_team_enhancement_agent_2",
                "team_id": "enhancement_team"
            }
        ]
        
        with self.driver.session() as session:
            for proposal in proposals:
                try:
                    session.run("""
                    MERGE (p:EnhancementProposal {id: $id})
                    SET p.title = $title,
                        p.description = $description,
                        p.standard_id = $standard_id,
                        p.section_id = $section_id,
                        p.current_text = $current_text,
                        p.proposed_text = $proposed_text,
                        p.rationale = $rationale,
                        p.status = $status,
                        p.created_at = $created_at,
                        p.updated_at = $updated_at,
                        p.created_by = $created_by,
                        p.team_id = $team_id
                    """, **proposal)
                    
                    # Create relationship to standard
                    session.run("""
                    MATCH (p:EnhancementProposal {id: $proposal_id})
                    MATCH (s:Standard {id: $standard_id})
                    MERGE (p)-[r:ENHANCES]->(s)
                    """, proposal_id=proposal["id"], standard_id=proposal["standard_id"])
                    
                    logger.info(f"Created enhancement proposal: {proposal['id']}")
                except Exception as e:
                    logger.error(f"Error creating enhancement proposal {proposal['id']}: {e}")
    
    def create_validation_results(self):
        """Create sample validation results."""
        validations = [
            {
                "id": "VR001",
                "proposal_id": "EP001",
                "validator_id": "validation_team_validation_agent_1",
                "team_id": "validation_team",
                "result": "approved",
                "confidence": 0.85,
                "comments": "The proposed clarification aligns with AAOIFI's principles and improves consistency.",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "VR002",
                "proposal_id": "EP001",
                "validator_id": "validation_team_validation_agent_2",
                "team_id": "validation_team",
                "result": "approved",
                "confidence": 0.78,
                "comments": "The effective profit rate method is widely accepted and provides more accurate profit recognition.",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "VR003",
                "proposal_id": "EP001",
                "validator_id": "validation_team_validation_agent_3",
                "team_id": "validation_team",
                "result": "needs_revision",
                "confidence": 0.65,
                "comments": "The proposal is generally sound but should include examples of how to apply the effective profit rate method.",
                "created_at": datetime.now().isoformat()
            }
        ]
        
        with self.driver.session() as session:
            for validation in validations:
                try:
                    session.run("""
                    MERGE (v:ValidationResult {id: $id})
                    SET v.proposal_id = $proposal_id,
                        v.validator_id = $validator_id,
                        v.team_id = $team_id,
                        v.result = $result,
                        v.confidence = $confidence,
                        v.comments = $comments,
                        v.created_at = $created_at
                    """, **validation)
                    
                    # Create relationship to proposal
                    session.run("""
                    MATCH (v:ValidationResult {id: $validation_id})
                    MATCH (p:EnhancementProposal {id: $proposal_id})
                    MERGE (v)-[r:VALIDATES]->(p)
                    """, validation_id=validation["id"], proposal_id=validation["proposal_id"])
                    
                    logger.info(f"Created validation result: {validation['id']}")
                except Exception as e:
                    logger.error(f"Error creating validation result {validation['id']}: {e}")
    
    def run(self):
        """Run the database initialization."""
        logger.info("Starting database initialization")
        
        if not self.connect():
            logger.error("Failed to connect to Neo4j database")
            return False
        
        try:
            self.create_constraints()
            self.create_standards()
            self.create_relationships()
            self.create_enhancement_proposals()
            self.create_validation_results()
            
            logger.info("Database initialization complete")
            return True
        except Exception as e:
            logger.error(f"Error during database initialization: {e}")
            return False
        finally:
            self.close()

def main():
    """Run the database initialization."""
    initializer = DatabaseInitializer()
    success = initializer.run()
    
    if success:
        logger.info("Database initialization completed successfully")
    else:
        logger.error("Database initialization failed")

if __name__ == "__main__":
    main()
