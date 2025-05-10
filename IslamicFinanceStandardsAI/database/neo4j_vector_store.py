"""
Neo4j Vector Store for Islamic Finance Standards

This module provides a Neo4j-based vector store implementation that combines
the graph database capabilities of Neo4j with vector embeddings for semantic search.
It integrates with the Gemini embeddings to provide a comprehensive knowledge graph
that supports both structured queries and semantic similarity search.
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime

import numpy as np
from neo4j import GraphDatabase, basic_auth
from langchain.vectorstores.base import VectorStore
from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings

# Import our custom embeddings
from utils.gemini_embeddings import GeminiEmbeddings

logger = logging.getLogger(__name__)

class Neo4jVectorStore(VectorStore):
    """
    Neo4j-based vector store for Islamic finance standards that combines
    graph database capabilities with vector embeddings for semantic search.
    """
    
    def __init__(
        self,
        embedding_function: Embeddings,
        url: str = None,
        username: str = None,
        password: str = None,
        database: str = "neo4j",
        index_name: str = "vector",
        node_label: str = "Document",
        text_node_property: str = "text",
        embedding_node_property: str = "embedding",
        embedding_dimension: int = 768
    ):
        """
        Initialize the Neo4j vector store.
        
        Args:
            embedding_function: Function to generate embeddings
            url: Neo4j URL (defaults to environment variable NEO4J_URI)
            username: Neo4j username (defaults to environment variable NEO4J_USER)
            password: Neo4j password (defaults to environment variable NEO4J_PASSWORD)
            database: Neo4j database name
            index_name: Name of the vector index in Neo4j
            node_label: Label for document nodes
            text_node_property: Property name for document text
            embedding_node_property: Property name for embedding vectors
            embedding_dimension: Dimension of embedding vectors
        """
        self.embedding_function = embedding_function
        self.url = url or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.username = username or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        self.database = database
        self.index_name = index_name
        self.node_label = node_label
        self.text_node_property = text_node_property
        self.embedding_node_property = embedding_node_property
        self.embedding_dimension = embedding_dimension
        
        # Initialize Neo4j driver
        try:
            self.driver = GraphDatabase.driver(
                self.url,
                auth=basic_auth(self.username, self.password)
            )
            logger.info(f"Successfully connected to Neo4j at {self.url}")
            
            # Ensure vector index exists
            self._create_vector_index()
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise
    
    def _create_vector_index(self):
        """Create the vector index in Neo4j if it doesn't exist"""
        # Check if index exists
        check_query = """
        SHOW INDEXES
        YIELD name, type
        WHERE name = $index_name AND type = 'VECTOR'
        RETURN count(*) > 0 AS exists
        """
        
        # Create index if it doesn't exist
        create_query = f"""
        CREATE VECTOR INDEX {self.index_name} IF NOT EXISTS
        FOR (d:{self.node_label})
        ON (d.{self.embedding_node_property})
        OPTIONS {{indexConfig: {{
            `vector.dimensions`: {self.embedding_dimension},
            `vector.similarity_function`: 'cosine'
        }}}}
        """
        
        with self.driver.session(database=self.database) as session:
            # Check if index exists
            result = session.run(check_query, index_name=self.index_name)
            index_exists = result.single()["exists"]
            
            if not index_exists:
                # Create index
                session.run(create_query)
                logger.info(f"Created vector index '{self.index_name}' in Neo4j")
            else:
                logger.info(f"Vector index '{self.index_name}' already exists in Neo4j")
    
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[str]:
        """
        Add texts to the vector store.
        
        Args:
            texts: List of text strings to add
            metadatas: Optional list of metadata dicts, one for each text
            ids: Optional list of IDs, one for each text
            
        Returns:
            List of IDs of the added texts
        """
        # Generate embeddings for texts
        embeddings = self.embedding_function.embed_documents(texts)
        
        # Prepare for batch insert
        if not metadatas:
            metadatas = [{} for _ in texts]
        
        if not ids:
            ids = [str(i) for i in range(len(texts))]
        
        # Create Cypher query for batch insert
        query = f"""
        UNWIND $data AS item
        CREATE (d:{self.node_label} {{
            id: item.id,
            {self.text_node_property}: item.text,
            {self.embedding_node_property}: item.embedding
        }})
        SET d += item.metadata
        RETURN d.id AS id
        """
        
        # Prepare data for batch insert
        data = [
            {
                "id": id_,
                "text": text,
                "embedding": embedding,
                "metadata": metadata
            }
            for id_, text, embedding, metadata in zip(ids, texts, embeddings, metadatas)
        ]
        
        # Execute batch insert
        with self.driver.session(database=self.database) as session:
            result = session.run(query, data=data)
            inserted_ids = [record["id"] for record in result]
            
        logger.info(f"Added {len(inserted_ids)} texts to Neo4j vector store")
        return inserted_ids
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        **kwargs: Any,
    ) -> List[Tuple[Document, float]]:
        """
        Search for documents similar to the query text.
        
        Args:
            query: Query text
            k: Number of documents to return
            
        Returns:
            List of tuples of (document, score)
        """
        # Generate embedding for query
        embedding = self.embedding_function.embed_query(query)
        
        # Create Cypher query for vector search
        search_query = f"""
        CALL db.index.vector.queryNodes(
            '{self.index_name}',
            $k,
            $embedding
        )
        YIELD node, score
        RETURN node.id AS id,
               node.{self.text_node_property} AS text,
               score,
               node {{.*}} AS metadata
        """
        
        # Execute search
        with self.driver.session(database=self.database) as session:
            result = session.run(search_query, k=k, embedding=embedding)
            
            docs_and_scores = []
            for record in result:
                # Extract metadata (excluding text and embedding)
                metadata = record["metadata"]
                if self.text_node_property in metadata:
                    del metadata[self.text_node_property]
                if self.embedding_node_property in metadata:
                    del metadata[self.embedding_node_property]
                if "id" in metadata:
                    del metadata["id"]
                
                # Create document
                doc = Document(
                    page_content=record["text"],
                    metadata=metadata
                )
                
                # Add to results
                docs_and_scores.append((doc, record["score"]))
        
        return docs_and_scores
    
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        **kwargs: Any,
    ) -> List[Document]:
        """
        Search for documents similar to the query text.
        
        Args:
            query: Query text
            k: Number of documents to return
            
        Returns:
            List of documents
        """
        docs_and_scores = self.similarity_search_with_score(query, k, **kwargs)
        return [doc for doc, _ in docs_and_scores]
    
    def add_documents(self, documents: List[Document], **kwargs: Any) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of documents to add
            
        Returns:
            List of IDs of the added documents
        """
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        return self.add_texts(texts, metadatas, **kwargs)
    
    def delete(self, ids: Optional[List[str]] = None, **kwargs: Any) -> None:
        """
        Delete documents from the vector store.
        
        Args:
            ids: List of IDs to delete
        """
        if not ids:
            # Delete all documents
            query = f"""
            MATCH (d:{self.node_label})
            DELETE d
            """
            
            with self.driver.session(database=self.database) as session:
                session.run(query)
                
            logger.info(f"Deleted all documents from Neo4j vector store")
        else:
            # Delete specific documents
            query = f"""
            UNWIND $ids AS id
            MATCH (d:{self.node_label} {{id: id}})
            DELETE d
            """
            
            with self.driver.session(database=self.database) as session:
                session.run(query, ids=ids)
                
            logger.info(f"Deleted {len(ids)} documents from Neo4j vector store")
    
    def close(self) -> None:
        """Close the Neo4j connection"""
        if hasattr(self, 'driver'):
            self.driver.close()
            logger.info("Closed Neo4j connection")
    
    @classmethod
    def from_texts(
        cls,
        texts: List[str],
        embedding: Embeddings,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> "Neo4jVectorStore":
        """
        Create a Neo4jVectorStore from a list of texts.
        
        Args:
            texts: List of texts
            embedding: Embedding function
            metadatas: Optional list of metadatas
            
        Returns:
            Neo4jVectorStore
        """
        store = cls(embedding_function=embedding, **kwargs)
        store.add_texts(texts, metadatas)
        return store
    
    def link_document_to_node(self, document_id: str, node_id: str, relationship_type: str, properties: Dict[str, Any] = None) -> str:
        """
        Create a relationship between a document and another node in the graph.
        
        Args:
            document_id: ID of the document
            node_id: ID of the node to link to
            relationship_type: Type of relationship
            properties: Optional properties for the relationship
            
        Returns:
            ID of the created relationship
        """
        # In Neo4j, relationship types cannot be parameterized directly
        # We need to use different queries for different relationship types
        if relationship_type == "DESCRIBES":
            query = """
            MATCH (d:Document {id: $document_id})
            MATCH (n) WHERE id(n) = $node_id
            CREATE (d)-[r:DESCRIBES]->(n)
            SET r = $properties
            RETURN id(r) AS relationship_id
            """
        elif relationship_type == "RELATES_TO":
            query = """
            MATCH (d:Document {id: $document_id})
            MATCH (n) WHERE id(n) = $node_id
            CREATE (d)-[r:RELATES_TO]->(n)
            SET r = $properties
            RETURN id(r) AS relationship_id
            """
        else:
            # Default to a generic relationship type
            query = """
            MATCH (d:Document {id: $document_id})
            MATCH (n) WHERE id(n) = $node_id
            CREATE (d)-[r:LINKED_TO]->(n)
            SET r = $properties
            RETURN id(r) AS relationship_id
            """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(
                query,
                document_id=document_id,
                node_id=int(node_id),
                properties=properties or {}
            )
            record = result.single()
            if record:
                return str(record["relationship_id"])
            return None
    
    def get_documents_for_node(self, node_id: str, relationship_type: str = None) -> List[Document]:
        """
        Get documents related to a node.
        
        Args:
            node_id: ID of the node
            relationship_type: Optional type of relationship
            
        Returns:
            List of documents
        """
        if relationship_type:
            query = f"""
            MATCH (d:{self.node_label})-[r:{relationship_type}]->(n)
            WHERE id(n) = $node_id
            RETURN d.id AS id, d.{self.text_node_property} AS text, d {{.*}} AS metadata
            """
        else:
            query = f"""
            MATCH (d:{self.node_label})-[r]->(n)
            WHERE id(n) = $node_id
            RETURN d.id AS id, d.{self.text_node_property} AS text, d {{.*}} AS metadata
            """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, node_id=int(node_id))
            
            documents = []
            for record in result:
                # Extract metadata (excluding text and embedding)
                metadata = record["metadata"]
                if self.text_node_property in metadata:
                    del metadata[self.text_node_property]
                if self.embedding_node_property in metadata:
                    del metadata[self.embedding_node_property]
                
                # Create document
                doc = Document(
                    page_content=record["text"],
                    metadata=metadata
                )
                
                documents.append(doc)
        
        return documents
