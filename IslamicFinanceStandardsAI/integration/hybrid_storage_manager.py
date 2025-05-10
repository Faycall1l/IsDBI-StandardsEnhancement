"""
Hybrid Storage Manager for Islamic Finance Standards Enhancement System

This module provides a hybrid storage solution that:
1. Uses FAISS for primary RAG operations (for efficiency)
2. Stores enhancement proposals in both the mock knowledge graph and Neo4j
3. Enables semantic search across both storage systems
4. Integrates with the event-driven architecture

It serves as a bridge between the existing multi-agent system and the Neo4j knowledge graph.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

# Import database components
from database.knowledge_graph import KnowledgeGraph
from database.mock_knowledge_graph import MockKnowledgeGraph
from database.neo4j_vector_store import Neo4jVectorStore

# Import utility components
from utils.gemini_embeddings import GeminiEmbeddings
from utils.gemini_client import GeminiClient
from utils.rag_engine import get_rag_engine
from utils.event_bus import EventBus, EventType

# Import configuration
from config.production import FEATURE_FLAGS

# Import model schemas
from models.enhancement_schema import EnhancementProposal, EnhancementStatus
from models.validation_schema import ValidationResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class HybridStorageManager:
    """
    Hybrid storage manager that integrates FAISS and Neo4j
    for the Islamic Finance Standards Enhancement system.
    """
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """
        Initialize the hybrid storage manager
        
        Args:
            event_bus: Optional event bus for publishing events
        """
        self.logger = logging.getLogger(__name__)
        self.event_bus = event_bus
        
        # Check if Neo4j is enabled
        self.use_neo4j = os.getenv("USE_NEO4J", "false").lower() == "true"
        
        # Initialize Neo4j integration if enabled
        if self.use_neo4j:
            self._init_neo4j()
        else:
            self.logger.info("Neo4j integration is disabled")
        
        # Initialize RAG engine with FAISS
        try:
            self.rag_engine = get_rag_engine()
            self.logger.info("Initialized RAG engine with FAISS")
        except Exception as e:
            self.logger.error(f"Failed to initialize RAG engine: {str(e)}")
            # Create a simplified RAG engine for storage only
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            from langchain.vectorstores import FAISS
            from langchain.docstore.document import Document
            
            self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            self.vector_store = FAISS.from_documents(
                [Document(page_content="Islamic Finance Standards", metadata={"source": "initialization"})],
                self.embeddings
            )
            self.logger.info("Created simplified RAG engine for storage")
        
        # Initialize Gemini client if needed
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            self.gemini_client = GeminiClient(api_key=gemini_api_key)
            self.logger.info("Initialized Gemini client")
        else:
            self.gemini_client = None
            self.logger.warning("Gemini client not initialized (API key not provided)")
    
    def _init_neo4j(self):
        """Initialize Neo4j vector store"""
        try:
            # Get Neo4j connection details
            neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            neo4j_user = os.getenv("NEO4J_USER", "neo4j")
            neo4j_password = os.getenv("NEO4J_PASSWORD", "password123")
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            
            if not gemini_api_key:
                self.logger.warning("Gemini API key not provided, using placeholder")
                gemini_api_key = "PLACEHOLDER_API_KEY"
            
            # Initialize embeddings
            self.embeddings = GeminiEmbeddings(api_key=gemini_api_key)
            
            # Initialize Neo4j vector store
            self.neo4j_store = Neo4jVectorStore(
                url=neo4j_uri,
                username=neo4j_user,
                password=neo4j_password,
                embedding=self.embeddings,
                index_name="islamic_finance_standards",
                node_label="Standard",
                text_node_property="content",
                embedding_node_property="embedding"
            )
            
            self.logger.info("Initialized Neo4j vector store")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Neo4j: {str(e)}")
            self.use_neo4j = False
    
    def store_enhancement(self, proposal: EnhancementProposal, knowledge_graph: KnowledgeGraph) -> Dict[str, Any]:
        """
        Store an enhancement proposal in both the knowledge graph and Neo4j
        
        Args:
            proposal: The enhancement proposal to store
            knowledge_graph: The knowledge graph instance
            
        Returns:
            Dictionary with IDs in both storage systems
        """
        try:
            # Store in knowledge graph
            proposal_id = knowledge_graph.store_enhancement_proposal(proposal)
            self.logger.info(f"Stored enhancement proposal in knowledge graph with ID: {proposal_id}")
            
            # Prepare result
            result = {
                "knowledge_graph_id": proposal_id,
                "neo4j_id": None
            }
            
            # Store in Neo4j if enabled
            if self.use_neo4j and hasattr(self, 'neo4j_store'):
                try:
                    # Prepare document for Neo4j
                    doc_content = f"""
                    Enhancement Proposal: {proposal.title}
                    
                    Standard: {proposal.standard_id}
                    Section: {proposal.section}
                    
                    Current Text:
                    {proposal.current_text}
                    
                    Proposed Enhancement:
                    {proposal.proposed_text}
                    
                    Rationale:
                    {proposal.rationale}
                    
                    Impact Analysis:
                    {proposal.impact_analysis}
                    """
                    
                    # Add to Neo4j vector store
                    metadata = {
                        "type": "enhancement_proposal",
                        "proposal_id": proposal_id,
                        "standard_id": proposal.standard_id,
                        "section": proposal.section,
                        "title": proposal.title,
                        "status": proposal.status.value,
                        "timestamp": proposal.timestamp.isoformat(),
                        "source": "enhancement_agent"
                    }
                    
                    # Split into chunks if needed
                    from langchain.docstore.document import Document
                    docs = [Document(page_content=doc_content, metadata=metadata)]
                    
                    if hasattr(self, 'text_splitter'):
                        docs = self.text_splitter.split_documents(docs)
                    
                    # Add to Neo4j
                    ids = self.neo4j_store.add_documents(docs)
                    result["neo4j_id"] = ids[0] if ids else None
                    
                    self.logger.info(f"Stored enhancement proposal in Neo4j with ID: {result['neo4j_id']}")
                    
                    # Publish event if event bus is available
                    if self.event_bus:
                        event_data = {
                            "proposal_id": proposal_id,
                            "neo4j_id": result["neo4j_id"],
                            "timestamp": datetime.now().isoformat()
                        }
                        self.event_bus.publish(EventType.ENHANCEMENT_STORED, event_data)
                        self.logger.info("Published ENHANCEMENT_STORED event")
                    
                except Exception as e:
                    self.logger.error(f"Failed to store in Neo4j: {str(e)}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to store enhancement proposal: {str(e)}")
            return {"knowledge_graph_id": None, "neo4j_id": None}
    
    def store_validation_result(self, validation_result: ValidationResult, knowledge_graph: KnowledgeGraph) -> str:
        """
        Store a validation result in both the knowledge graph and Neo4j
        
        Args:
            validation_result: The validation result to store
            knowledge_graph: The knowledge graph instance
            
        Returns:
            ID of the stored validation result in the knowledge graph
        """
        try:
            # Store in knowledge graph
            result_id = knowledge_graph.store_validation_result(validation_result)
            self.logger.info(f"Stored validation result in knowledge graph with ID: {result_id}")
            
            # Store in Neo4j if enabled
            if self.use_neo4j and hasattr(self, 'neo4j_store'):
                try:
                    # Prepare document for Neo4j
                    doc_content = f"""
                    Validation Result for Proposal: {validation_result.proposal_id}
                    
                    Shariah Compliance: {'Compliant' if validation_result.is_shariah_compliant else 'Non-Compliant'}
                    
                    Feedback:
                    {validation_result.feedback}
                    
                    Improvement Suggestions:
                    {validation_result.improvement_suggestions}
                    
                    References:
                    {', '.join(validation_result.references)}
                    """
                    
                    # Add to Neo4j vector store
                    metadata = {
                        "type": "validation_result",
                        "result_id": result_id,
                        "proposal_id": validation_result.proposal_id,
                        "is_shariah_compliant": validation_result.is_shariah_compliant,
                        "timestamp": validation_result.timestamp.isoformat(),
                        "source": "validation_agent"
                    }
                    
                    # Split into chunks if needed
                    from langchain.docstore.document import Document
                    docs = [Document(page_content=doc_content, metadata=metadata)]
                    
                    if hasattr(self, 'text_splitter'):
                        docs = self.text_splitter.split_documents(docs)
                    
                    # Add to Neo4j
                    ids = self.neo4j_store.add_documents(docs)
                    neo4j_id = ids[0] if ids else None
                    
                    self.logger.info(f"Stored validation result in Neo4j with ID: {neo4j_id}")
                    
                    # Publish event if event bus is available
                    if self.event_bus:
                        event_data = {
                            "result_id": result_id,
                            "neo4j_id": neo4j_id,
                            "proposal_id": validation_result.proposal_id,
                            "timestamp": datetime.now().isoformat()
                        }
                        self.event_bus.publish(EventType.VALIDATION_STORED, event_data)
                        self.logger.info("Published VALIDATION_STORED event")
                    
                except Exception as e:
                    self.logger.error(f"Failed to update Neo4j with validation result: {str(e)}")
            
            return result_id
            
        except Exception as e:
            self.logger.error(f"Failed to store validation result: {str(e)}")
            return None
    
    def get_similar_documents(self, query: str, top_k: int = 5, use_web: bool = False) -> List[Dict[str, Any]]:
        """
        Retrieve similar documents using FAISS, Neo4j, and optionally web search
        
        Args:
            query: The query text
            top_k: Number of results to return
            use_web: Whether to use web search to enhance results
            
        Returns:
            List of similar documents
        """
        results = []
        
        # Retrieve from FAISS
        try:
            if hasattr(self, 'rag_engine') and self.rag_engine:
                # Use the RAG engine to retrieve documents
                docs = self.rag_engine.retrieve(query, k=top_k, use_web=use_web)
                for i, doc in enumerate(docs):
                    results.append({
                        "source": doc.metadata.get("source", "FAISS"),
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "score": 1.0 - (i * 0.1)  # Approximate score based on position
                    })
                
                self.logger.info(f"Retrieved {len(docs)} similar documents from RAG engine")
            elif hasattr(self, 'vector_store'):
                # Use the simplified vector store directly
                faiss_results = self.vector_store.similarity_search_with_score(query, k=top_k)
                for doc, score in faiss_results:
                    results.append({
                        "source": "FAISS",
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "score": score
                    })
                
                self.logger.info(f"Retrieved {len(faiss_results)} similar documents from simplified FAISS")
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
        
        # If web search is enabled, retrieve from web
        if use_web:
            try:
                web_results = self.web_search(query, k=top_k)
                for i, result in enumerate(web_results):
                    results.append({
                        "source": "Web",
                        "content": result["content"],
                        "metadata": result["metadata"],
                        "score": 1.0 - (i * 0.1)  # Approximate score based on position
                    })
                
                self.logger.info(f"Retrieved {len(web_results)} similar documents from web search")
            except Exception as e:
                self.logger.error(f"Failed to retrieve from web search: {str(e)}")
        
        # Sort by score (higher is better)
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Take top_k results
        return results[:top_k]
    
    def web_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Perform a web search for Islamic finance standards related to the query
        
        Args:
            query: The search query
            k: Maximum number of results to return
            
        Returns:
            List of search results with content and metadata
        """
        try:
            # Import web retriever
            from utils.web_retriever import get_web_retriever
            web_retriever = get_web_retriever()
            
            if not web_retriever:
                self.logger.error("Web retriever not available")
                return []
            
            # Search for standards
            standards = web_retriever.search_standards(query, max_results=k)
            results = []
            
            for standard in standards:
                # Try to retrieve content if URL is available
                content = ""
                if "url" in standard and standard["url"]:
                    try:
                        content = web_retriever.retrieve_standard_content(standard["url"])
                    except Exception as e:
                        self.logger.error(f"Error retrieving content from {standard['url']}: {str(e)}")
                        content = standard.get("snippet", "")
                else:
                    content = standard.get("snippet", "")
                
                # Create result
                results.append({
                    "content": content,
                    "metadata": {
                        "source": standard.get("source", "web"),
                        "title": standard.get("title", "Unknown Standard"),
                        "url": standard.get("url", ""),
                        "retrieved_from_web": True
                    }
                })
            
            self.logger.info(f"Retrieved {len(results)} standards from web search")
            return results
            
        except Exception as e:
            self.logger.error(f"Error performing web search: {str(e)}")
            return []
    
    def retrieve_similar_enhancements(self, query: str, top_k: int = 5, use_web: bool = False) -> List[Dict[str, Any]]:
        """
        Retrieve similar enhancement proposals using both FAISS and Neo4j
        
        Args:
            query: The query text
            top_k: Number of results to return
            use_web: Whether to use web search to enhance results
            
        Returns:
            List of similar enhancement proposals
        """
        # This is now a wrapper around get_similar_documents for backward compatibility
        return self.get_similar_documents(query, top_k, use_web)
    
    def generate_response(self, query: str, context: Optional[str] = None, use_web: bool = False) -> str:
        """
        Generate a response using Gemini based on a query and optional context
        
        Args:
            query: The user query
            context: Optional context information
            use_web: Whether to use web search to enhance results
            
        Returns:
            Generated response
        """
        if not self.gemini_client:
            self.logger.error("Gemini client not initialized")
            return "Unable to generate response (Gemini client not initialized)"
        
        try:
            # Retrieve relevant documents if no context is provided
            if not context:
                results = self.get_similar_documents(query, top_k=3, use_web=use_web)
                context = "\n\n".join([result["content"] for result in results])
                
                # Add a note if web search was used
                if use_web:
                    web_sources = [result["metadata"].get("url", "") for result in results 
                                 if result["metadata"].get("retrieved_from_web", False) and result["metadata"].get("url")]
                    if web_sources:
                        context += "\n\nWeb sources consulted:\n" + "\n".join(web_sources)
            
            # Generate response
            prompt = f"""
            Context information:
            {context}
            
            User query: {query}
            
            Please provide a detailed and accurate response based on the context information.
            Focus on Islamic finance principles and standards.
            """
            
            response = self.gemini_client.generate_text(
                prompt=prompt,
                temperature=0.7,
                max_tokens=1000,
                system_prompt="You are an expert in Islamic finance, Shariah compliance, and accounting standards."
            )
            
            self.logger.info("Generated response with Gemini")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to generate response: {str(e)}")
            return f"Error generating response: {str(e)}"
    
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

def get_hybrid_storage_manager(event_bus: Optional[EventBus] = None):
    """Get the singleton hybrid storage manager instance"""
    global _instance
    if _instance is None:
        _instance = HybridStorageManager(event_bus=event_bus)
    return _instance
