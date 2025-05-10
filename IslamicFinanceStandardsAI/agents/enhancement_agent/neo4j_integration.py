"""
Neo4j Integration for Enhancement Agent

This module provides integration between the Enhancement Agent and the Neo4j knowledge graph,
allowing enhancement proposals to be stored in both the mock knowledge graph and Neo4j.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from database.neo4j_vector_store import Neo4jVectorStore
from utils.gemini_embeddings import GeminiEmbeddings
from models.enhancement_schema import EnhancementProposal

logger = logging.getLogger(__name__)

class Neo4jEnhancementStore:
    """
    Neo4j integration for storing enhancement proposals
    """
    
    def __init__(self):
        """Initialize the Neo4j enhancement store"""
        self.logger = logging.getLogger(__name__)
        
        # Check if Neo4j is enabled
        self.enabled = os.getenv("USE_NEO4J", "false").lower() == "true"
        
        if not self.enabled:
            self.logger.info("Neo4j integration is disabled")
            return
        
        # Check if Gemini API key is set
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            self.logger.warning("GEMINI_API_KEY environment variable is not set, Neo4j integration will be disabled")
            self.enabled = False
            return
        
        # Check if Neo4j connection details are set
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "password123")
        
        # Initialize Gemini embeddings
        try:
            self.embeddings = GeminiEmbeddings(api_key=self.gemini_api_key)
            self.logger.info("Initialized Gemini embeddings for Neo4j integration")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini embeddings: {str(e)}")
            self.enabled = False
            return
        
        # Initialize Neo4j vector store
        try:
            self.vector_store = Neo4jVectorStore(
                embedding_function=self.embeddings,
                url=self.neo4j_uri,
                username=self.neo4j_user,
                password=self.neo4j_password,
                index_name="islamic_finance_vector",
                node_label="EnhancementProposal",
                text_node_property="content",
                embedding_node_property="embedding"
            )
            self.logger.info("Initialized Neo4j vector store for enhancement proposals")
        except Exception as e:
            self.logger.error(f"Failed to initialize Neo4j vector store: {str(e)}")
            self.enabled = False
            return
    
    def store_enhancement_proposal(self, proposal: EnhancementProposal, standard_id: str) -> Optional[str]:
        """
        Store an enhancement proposal in Neo4j
        
        Args:
            proposal: Enhancement proposal to store
            standard_id: ID of the standard the proposal is for
            
        Returns:
            ID of the stored proposal in Neo4j, or None if Neo4j integration is disabled
        """
        if not self.enabled:
            self.logger.info("Neo4j integration is disabled, skipping proposal storage")
            return None
        
        try:
            # Prepare the proposal text and metadata
            proposal_text = proposal.content
            metadata = {
                "title": proposal.title,
                "standard_id": standard_id,
                "proposal_id": proposal.proposal_id,
                "timestamp": datetime.now().isoformat(),
                "type": "enhancement_proposal"
            }
            
            # Add the proposal to Neo4j
            proposal_ids = self.vector_store.add_texts([proposal_text], [metadata])
            proposal_id = proposal_ids[0] if proposal_ids else None
            
            if proposal_id:
                self.logger.info(f"Stored enhancement proposal in Neo4j with ID: {proposal_id}")
                
                # Link the proposal to the standard in Neo4j
                try:
                    # First, find the standard node in Neo4j
                    with self.vector_store.driver.session() as session:
                        # Check if standard exists
                        query = """
                        MATCH (s:Standard)
                        WHERE s.standard_number = $standard_number
                        RETURN id(s) AS standard_id
                        """
                        
                        result = session.run(
                            query,
                            standard_number=standard_id.split("-")[1] if "-" in standard_id else standard_id
                        )
                        
                        record = result.single()
                        if record:
                            neo4j_standard_id = str(record["standard_id"])
                            
                            # Link the proposal to the standard
                            relationship_id = self.vector_store.link_document_to_node(
                                document_id=proposal_id,
                                node_id=neo4j_standard_id,
                                relationship_type="ENHANCES",
                                properties={"created_at": datetime.now().isoformat()}
                            )
                            
                            self.logger.info(f"Linked proposal {proposal_id} to standard {neo4j_standard_id} with relationship ID: {relationship_id}")
                        else:
                            # Standard doesn't exist, create it
                            create_query = """
                            CREATE (s:Standard {
                                title: $title,
                                standard_type: $standard_type,
                                standard_number: $standard_number,
                                publication_date: $publication_date
                            })
                            RETURN id(s) AS standard_id
                            """
                            
                            # Parse standard_id (e.g., "FAS-4-001" -> type="FAS", number="4")
                            parts = standard_id.split("-")
                            standard_type = parts[0] if len(parts) > 0 else "FAS"
                            standard_number = parts[1] if len(parts) > 1 else "0"
                            
                            result = session.run(
                                create_query,
                                title=f"{standard_type} {standard_number}",
                                standard_type=standard_type,
                                standard_number=standard_number,
                                publication_date=datetime.now().isoformat()
                            )
                            
                            record = result.single()
                            if record:
                                neo4j_standard_id = str(record["standard_id"])
                                
                                # Link the proposal to the standard
                                relationship_id = self.vector_store.link_document_to_node(
                                    document_id=proposal_id,
                                    node_id=neo4j_standard_id,
                                    relationship_type="ENHANCES",
                                    properties={"created_at": datetime.now().isoformat()}
                                )
                                
                                self.logger.info(f"Created standard {neo4j_standard_id} and linked proposal {proposal_id} with relationship ID: {relationship_id}")
                
                except Exception as e:
                    self.logger.error(f"Failed to link proposal to standard in Neo4j: {str(e)}")
            
            return proposal_id
            
        except Exception as e:
            self.logger.error(f"Failed to store enhancement proposal in Neo4j: {str(e)}")
            return None
    
    def close(self):
        """Close the Neo4j connection"""
        if self.enabled and hasattr(self, 'vector_store'):
            try:
                self.vector_store.close()
                self.logger.info("Closed Neo4j connection")
            except Exception as e:
                self.logger.error(f"Error closing Neo4j connection: {str(e)}")

# Singleton instance
_instance = None

def get_neo4j_enhancement_store():
    """Get the singleton Neo4j enhancement store instance"""
    global _instance
    if _instance is None:
        _instance = Neo4jEnhancementStore()
    return _instance
