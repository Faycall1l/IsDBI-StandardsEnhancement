"""
Dual Storage Integration for Islamic Finance Standards Enhancement System

This module provides integration between:
1. FAISS for RAG (Retrieval-Augmented Generation)
2. Neo4j for knowledge graph storage and relationships

The system uses FAISS for efficient vector search during RAG operations
while storing enhancement proposals in both the mock knowledge graph and Neo4j.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

from database.knowledge_graph import KnowledgeGraph
from database.mock_knowledge_graph import MockKnowledgeGraph
from database.neo4j_vector_store import Neo4jVectorStore
from utils.gemini_embeddings import GeminiEmbeddings
from utils.rag_engine import RAGEngine, get_rag_engine
from models.enhancement_schema import EnhancementProposal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class DualStorageManager:
    """
    Manager for dual storage integration between FAISS and Neo4j
    """
    
    def __init__(self):
        """Initialize the dual storage manager"""
        self.logger = logging.getLogger(__name__)
        
        # Check if Neo4j is enabled
        self.use_neo4j = os.getenv("USE_NEO4J", "false").lower() == "true"
        
        # Initialize Neo4j vector store if enabled
        if self.use_neo4j:
            self._init_neo4j()
        else:
            self.logger.info("Neo4j integration is disabled")
            
        # Initialize RAG engine with FAISS
        self.rag_engine = get_rag_engine()
        self.logger.info("Initialized RAG engine with FAISS")
    
    def _init_neo4j(self):
        """Initialize Neo4j vector store"""
        try:
            # Get Neo4j connection details
            neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            neo4j_user = os.getenv("NEO4J_USER", "neo4j")
            neo4j_password = os.getenv("NEO4J_PASSWORD", "password123")
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            
            if not gemini_api_key:
                self.logger.error("GEMINI_API_KEY environment variable is not set")
                self.use_neo4j = False
                return
            
            # Initialize Gemini embeddings
            self.embeddings = GeminiEmbeddings(api_key=gemini_api_key)
            self.logger.info("Initialized Gemini embeddings for Neo4j integration")
            
            # Initialize Neo4j vector store
            self.neo4j_store = Neo4jVectorStore(
                embedding_function=self.embeddings,
                url=neo4j_uri,
                username=neo4j_user,
                password=neo4j_password,
                index_name="islamic_finance_vector",
                node_label="Document",
                text_node_property="content",
                embedding_node_property="embedding"
            )
            self.logger.info("Initialized Neo4j vector store")
            
            # Create vector index if it doesn't exist
            self.neo4j_store.create_vector_index()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Neo4j vector store: {str(e)}")
            self.use_neo4j = False
    
    def store_enhancement(self, proposal: EnhancementProposal, knowledge_graph: KnowledgeGraph) -> Dict[str, str]:
        """
        Store an enhancement proposal in both the knowledge graph and Neo4j
        
        Args:
            proposal: The enhancement proposal to store
            knowledge_graph: The knowledge graph instance
            
        Returns:
            Dictionary with IDs in both storage systems
        """
        result = {
            "kg_id": None,
            "neo4j_id": None
        }
        
        # Store in knowledge graph
        try:
            # Convert to dictionary for storage
            proposal_dict = proposal.dict()
            
            # Store the proposal node
            kg_id = knowledge_graph.create_node(
                label="EnhancementProposal",
                properties={
                    "standard_id": proposal.standard_id,
                    "enhancement_type": proposal.enhancement_type,
                    "target_id": proposal.target_id,
                    "original_content": proposal.original_content,
                    "enhanced_content": proposal.enhanced_content,
                    "reasoning": proposal.reasoning,
                    "references": proposal.references,
                    "status": proposal.status
                }
            )
            
            # Link proposal to standard
            knowledge_graph.create_relationship(
                start_node_id=proposal.standard_id,
                end_node_id=kg_id,
                relationship_type="HAS_ENHANCEMENT"
            )
            
            # Link proposal to target node
            knowledge_graph.create_relationship(
                start_node_id=kg_id,
                end_node_id=proposal.target_id,
                relationship_type="ENHANCES"
            )
            
            result["kg_id"] = kg_id
            self.logger.info(f"Stored enhancement proposal in knowledge graph with ID: {kg_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to store enhancement in knowledge graph: {str(e)}")
        
        # Store in Neo4j if enabled
        if self.use_neo4j:
            try:
                # Prepare the proposal text and metadata
                proposal_text = proposal.enhanced_content
                metadata = {
                    "standard_id": proposal.standard_id,
                    "enhancement_type": proposal.enhancement_type,
                    "target_id": proposal.target_id,
                    "original_content": proposal.original_content,
                    "reasoning": proposal.reasoning,
                    "references": proposal.references,
                    "status": proposal.status,
                    "type": "enhancement_proposal"
                }
                
                # Add the proposal to Neo4j
                proposal_ids = self.neo4j_store.add_texts([proposal_text], [metadata])
                neo4j_id = proposal_ids[0] if proposal_ids else None
                
                if neo4j_id:
                    result["neo4j_id"] = neo4j_id
                    self.logger.info(f"Stored enhancement proposal in Neo4j with ID: {neo4j_id}")
                    
                    # Link the proposal to the standard in Neo4j
                    try:
                        # First, find or create the standard node in Neo4j
                        with self.neo4j_store.driver.session() as session:
                            # Check if standard exists
                            query = """
                            MATCH (s:Standard)
                            WHERE s.id = $standard_id
                            RETURN id(s) AS standard_id
                            """
                            
                            result_set = session.run(
                                query,
                                standard_id=proposal.standard_id
                            )
                            
                            record = result_set.single()
                            if record:
                                neo4j_standard_id = str(record["standard_id"])
                            else:
                                # Standard doesn't exist, create it
                                create_query = """
                                CREATE (s:Standard {
                                    id: $standard_id,
                                    type: $standard_type,
                                    number: $standard_number
                                })
                                RETURN id(s) AS standard_id
                                """
                                
                                # Parse standard_id (e.g., "FAS-4" -> type="FAS", number="4")
                                parts = proposal.standard_id.split("-") if "-" in proposal.standard_id else [proposal.standard_id, "0"]
                                standard_type = parts[0] if len(parts) > 0 else "FAS"
                                standard_number = parts[1] if len(parts) > 1 else "0"
                                
                                result_set = session.run(
                                    create_query,
                                    standard_id=proposal.standard_id,
                                    standard_type=standard_type,
                                    standard_number=standard_number
                                )
                                
                                record = result_set.single()
                                neo4j_standard_id = str(record["standard_id"]) if record else None
                            
                            if neo4j_standard_id:
                                # Link the proposal to the standard
                                relationship_id = self.neo4j_store.link_document_to_node(
                                    document_id=neo4j_id,
                                    node_id=neo4j_standard_id,
                                    relationship_type="ENHANCES",
                                    properties={"type": proposal.enhancement_type}
                                )
                                
                                self.logger.info(f"Linked proposal {neo4j_id} to standard {neo4j_standard_id} with relationship ID: {relationship_id}")
                    
                    except Exception as e:
                        self.logger.error(f"Failed to link proposal to standard in Neo4j: {str(e)}")
                
            except Exception as e:
                self.logger.error(f"Failed to store enhancement proposal in Neo4j: {str(e)}")
        
        return result
    
    def retrieve_similar_enhancements(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve similar enhancement proposals using both FAISS and Neo4j
        
        Args:
            query: The query text
            top_k: Number of results to return
            
        Returns:
            List of similar enhancement proposals
        """
        results = []
        
        # Retrieve from FAISS
        try:
            faiss_results = self.rag_engine.retrieve(query, top_k=top_k)
            for doc in faiss_results:
                results.append({
                    "source": "FAISS",
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": doc.metadata.get("score", 0.0) if hasattr(doc, "metadata") else 0.0
                })
            
            self.logger.info(f"Retrieved {len(faiss_results)} similar documents from FAISS")
        except Exception as e:
            self.logger.error(f"Failed to retrieve from FAISS: {str(e)}")
        
        # Retrieve from Neo4j if enabled
        if self.use_neo4j:
            try:
                neo4j_results = self.neo4j_store.similarity_search_with_score(query, k=top_k)
                for doc, score in neo4j_results:
                    results.append({
                        "source": "Neo4j",
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "score": score
                    })
                
                self.logger.info(f"Retrieved {len(neo4j_results)} similar documents from Neo4j")
            except Exception as e:
                self.logger.error(f"Failed to retrieve from Neo4j: {str(e)}")
        
        # Sort by score (higher is better)
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Take top_k results
        return results[:top_k]
    
    def close(self):
        """Close connections"""
        if self.use_neo4j and hasattr(self, 'neo4j_store'):
            try:
                self.neo4j_store.close()
                self.logger.info("Closed Neo4j connection")
            except Exception as e:
                self.logger.error(f"Error closing Neo4j connection: {str(e)}")

# Singleton instance
_instance = None

def get_dual_storage_manager():
    """Get the singleton dual storage manager instance"""
    global _instance
    if _instance is None:
        _instance = DualStorageManager()
    return _instance
