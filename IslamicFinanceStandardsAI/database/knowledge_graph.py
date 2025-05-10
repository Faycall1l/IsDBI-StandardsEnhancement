"""
Knowledge Graph Database

This module provides a Neo4j-based knowledge graph implementation for storing
and retrieving information about AAOIFI standards and enhancements.

The knowledge graph serves as the central "brain" of the multi-agent system,
storing and organizing all critical information from AAOIFI FAS (Financial
Accounting Standards) and SS (Shariah Standards) documents. It enables
context-aware decisions by the agents through a rich network of interconnected
nodes and relationships.

Key components include:
- Standards nodes (FAS and SS)
- Financial concepts and entities
- Shariah principles
- Transaction types
- Relationships between standards, concepts, and principles
- Amendment history and validation rules
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dotenv import load_dotenv
from neo4j import GraphDatabase, basic_auth

# Load environment variables
load_dotenv()

class KnowledgeGraph:
    """Neo4j-based knowledge graph for Islamic finance standards"""
    
    def __init__(self):
        """Initialize the knowledge graph connection"""
        self.logger = logging.getLogger(__name__)
        
        # Get Neo4j connection details from environment variables
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        
        # Initialize connection
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=basic_auth(self.user, self.password)
            )
            self.logger.info("Successfully connected to Neo4j knowledge graph")
        except Exception as e:
            self.logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise
    
    def close(self):
        """Close the knowledge graph connection"""
        if hasattr(self, 'driver'):
            self.driver.close()
    
    def create_node(self, label: str, properties: Dict[str, Any]) -> str:
        """
        Create a node in the knowledge graph
        
        Args:
            label: Node label (e.g., 'Standard', 'Definition')
            properties: Dictionary of node properties
            
        Returns:
            ID of the created node
        """
        query = f"""
        CREATE (n:{label} $properties)
        RETURN id(n) AS node_id
        """
        
        with self.driver.session() as session:
            result = session.run(query, properties=properties)
            record = result.single()
            if record:
                return str(record["node_id"])
            return None
    
    def get_node_by_id(self, node_id: str) -> Optional[Dict]:
        """
        Get a node by its ID
        
        Args:
            node_id: ID of the node to retrieve
            
        Returns:
            Dictionary with node information, or None if not found
        """
        query = """
        MATCH (n)
        WHERE id(n) = $node_id
        RETURN id(n) AS id, labels(n) AS labels, properties(n) AS properties
        """
        
        with self.driver.session() as session:
            result = session.run(query, node_id=int(node_id))
            record = result.single()
            
            if record:
                # Get the first label (assuming there's at least one)
                label = record["labels"][0] if record["labels"] else "Unknown"
                
                return {
                    "id": str(record["id"]),
                    "label": label,
                    "properties": record["properties"]
                }
            
            return None
    
    def update_node(self, node_id: str, properties: Dict[str, Any]) -> bool:
        """
        Update a node's properties
        
        Args:
            node_id: ID of the node to update
            properties: Dictionary of properties to update
            
        Returns:
            True if successful, False otherwise
        """
        query = """
        MATCH (n)
        WHERE id(n) = $node_id
        SET n += $properties
        RETURN n
        """
        
        with self.driver.session() as session:
            result = session.run(query, node_id=int(node_id), properties=properties)
            return result.single() is not None
    
    def delete_node(self, node_id: str) -> bool:
        """
        Delete a node
        
        Args:
            node_id: ID of the node to delete
            
        Returns:
            True if successful, False otherwise
        """
        query = """
        MATCH (n)
        WHERE id(n) = $node_id
        DETACH DELETE n
        """
        
        with self.driver.session() as session:
            result = session.run(query, node_id=int(node_id))
            return result.consume().counters.nodes_deleted > 0
    
    def create_relationship(self, start_node_id: str, end_node_id: str, relationship_type: str, properties: Dict[str, Any] = None) -> str:
        """
        Create a relationship between two nodes
        
        Args:
            start_node_id: ID of the start node
            end_node_id: ID of the end node
            relationship_type: Type of relationship
            properties: Optional dictionary of relationship properties
            
        Returns:
            ID of the created relationship
        """
        if properties is None:
            properties = {}
        
        query = """
        MATCH (a), (b)
        WHERE id(a) = $start_node_id AND id(b) = $end_node_id
        CREATE (a)-[r:`{relationship_type}` $properties]->(b)
        RETURN id(r) AS rel_id
        """.format(relationship_type=relationship_type)
        
        with self.driver.session() as session:
            result = session.run(
                query,
                start_node_id=int(start_node_id),
                end_node_id=int(end_node_id),
                properties=properties
            )
            record = result.single()
            if record:
                return str(record["rel_id"])
            return None
    
    def get_related_nodes(self, node_id: str, relationship_type: str = None, direction: str = "OUTGOING") -> List[Dict]:
        """
        Get nodes related to a given node
        
        Args:
            node_id: ID of the node
            relationship_type: Optional type of relationship to filter by
            direction: Direction of relationship ('OUTGOING', 'INCOMING', or 'BOTH')
            
        Returns:
            List of related node dictionaries
        """
        if direction == "OUTGOING":
            match_clause = "MATCH (n)-[r]->(m)"
        elif direction == "INCOMING":
            match_clause = "MATCH (n)<-[r]-(m)"
        else:  # BOTH
            match_clause = "MATCH (n)-[r]-(m)"
        
        if relationship_type:
            match_clause = match_clause.replace("[r]", f"[r:`{relationship_type}`]")
        
        query = f"""
        {match_clause}
        WHERE id(n) = $node_id
        RETURN id(m) AS id, labels(m) AS labels, properties(m) AS properties
        """
        
        with self.driver.session() as session:
            result = session.run(query, node_id=int(node_id))
            nodes = []
            
            for record in result:
                # Get the first label (assuming there's at least one)
                label = record["labels"][0] if record["labels"] else "Unknown"
                
                nodes.append({
                    "id": str(record["id"]),
                    "label": label,
                    "properties": record["properties"]
                })
            
            return nodes
    
    def search_nodes(self, label: str = None, properties: Dict[str, Any] = None) -> List[Dict]:
        """
        Search for nodes matching criteria
        
        Args:
            label: Optional node label to filter by
            properties: Optional dictionary of properties to match
            
        Returns:
            List of matching node dictionaries
        """
        if properties is None:
            properties = {}
        
        # Build the query
        if label:
            match_clause = f"MATCH (n:{label})"
        else:
            match_clause = "MATCH (n)"
        
        where_clauses = []
        for key, value in properties.items():
            where_clauses.append(f"n.{key} = ${key}")
        
        if where_clauses:
            where_clause = "WHERE " + " AND ".join(where_clauses)
        else:
            where_clause = ""
        
        query = f"""
        {match_clause}
        {where_clause}
        RETURN id(n) AS id, labels(n) AS labels, properties(n) AS properties
        """
        
        with self.driver.session() as session:
            result = session.run(query, **properties)
            nodes = []
            
            for record in result:
                # Get the first label (assuming there's at least one)
                label = record["labels"][0] if record["labels"] else "Unknown"
                
                nodes.append({
                    "id": str(record["id"]),
                    "label": label,
                    "properties": record["properties"]
                })
            
            return nodes
    
    def run_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict]:
        """
        Run a custom Cypher query
        
        Args:
            query: Cypher query string
            parameters: Optional dictionary of query parameters
            
        Returns:
            List of result records as dictionaries
        """
        if parameters is None:
            parameters = {}
        
        with self.driver.session() as session:
            result = session.run(query, **parameters)
            return [record.data() for record in result]
    
    def get_standards(self) -> List[Dict]:
        """
        Get all standards in the knowledge graph
        
        Returns:
            List of standard node dictionaries
        """
        return self.search_nodes(label="Standard")
    
    def get_standard_by_number(self, standard_type: str, standard_number: str) -> Optional[Dict]:
        """
        Get a standard by its type and number
        
        Args:
            standard_type: Type of standard (e.g., 'FAS', 'SS')
            standard_number: Standard number
            
        Returns:
            Standard node dictionary, or None if not found
        """
        properties = {
            "standard_type": standard_type,
            "standard_number": standard_number
        }
        
        results = self.search_nodes(label="Standard", properties=properties)
        return results[0] if results else None
    
    def get_definitions_for_standard(self, standard_id: str) -> List[Dict]:
        """
        Get all definitions for a standard
        
        Args:
            standard_id: ID of the standard
            
        Returns:
            List of definition node dictionaries
        """
        return self.get_related_nodes(standard_id, relationship_type="HAS_DEFINITION")
    
    def get_accounting_treatments_for_standard(self, standard_id: str) -> List[Dict]:
        """
        Get all accounting treatments for a standard
        
        Args:
            standard_id: ID of the standard
            
        Returns:
            List of accounting treatment node dictionaries
        """
        return self.get_related_nodes(standard_id, relationship_type="HAS_ACCOUNTING_TREATMENT")
    
    def get_transaction_structures_for_standard(self, standard_id: str) -> List[Dict]:
        """
        Get all transaction structures for a standard
        
        Args:
            standard_id: ID of the standard
            
        Returns:
            List of transaction structure node dictionaries
        """
        return self.get_related_nodes(standard_id, relationship_type="HAS_TRANSACTION_STRUCTURE")
    
    def get_ambiguities_for_standard(self, standard_id: str) -> List[Dict]:
        """
        Get all ambiguities for a standard
        
        Args:
            standard_id: ID of the standard
            
        Returns:
            List of ambiguity node dictionaries
        """
        return self.get_related_nodes(standard_id, relationship_type="HAS_AMBIGUITY")
    
    def get_enhancements_for_standard(self, standard_id: str) -> List[Dict]:
        """
        Get all enhancement proposals for a standard
        
        Args:
            standard_id: ID of the standard
            
        Returns:
            List of enhancement proposal node dictionaries
        """
        query = """
        MATCH (s)-[*1..2]->(e:EnhancementProposal)
        WHERE id(s) = $standard_id
        RETURN id(e) AS id, labels(e) AS labels, properties(e) AS properties
        """
        
        with self.driver.session() as session:
            result = session.run(query, standard_id=int(standard_id))
            nodes = []
            
            for record in result:
                # Get the first label (assuming there's at least one)
                label = record["labels"][0] if record["labels"] else "Unknown"
                
                nodes.append({
                    "id": str(record["id"]),
                    "label": label,
                    "properties": record["properties"]
                })
            
            return nodes
            
    # Islamic Finance Knowledge Graph Specific Methods
    
    def create_concept(self, name: str, description: str, properties: Dict[str, Any] = None) -> str:
        """
        Create a financial concept node in the knowledge graph
        
        Args:
            name: Name of the concept (e.g., 'Musharaka', 'Ijarah')
            description: Description of the concept
            properties: Additional properties for the concept
            
        Returns:
            ID of the created concept node
        """
        if properties is None:
            properties = {}
            
        properties.update({
            "name": name,
            "description": description
        })
        
        return self.create_node(label="Concept", properties=properties)
    
    def create_principle(self, name: str, description: str, properties: Dict[str, Any] = None) -> str:
        """
        Create a Shariah principle node in the knowledge graph
        
        Args:
            name: Name of the principle (e.g., 'Profit Sharing', 'Risk Allocation')
            description: Description of the principle
            properties: Additional properties for the principle
            
        Returns:
            ID of the created principle node
        """
        if properties is None:
            properties = {}
            
        properties.update({
            "name": name,
            "description": description
        })
        
        return self.create_node(label="Principle", properties=properties)
    
    def create_transaction_type(self, name: str, description: str, properties: Dict[str, Any] = None) -> str:
        """
        Create a transaction type node in the knowledge graph
        
        Args:
            name: Name of the transaction type (e.g., 'Lease Payment', 'Profit Distribution')
            description: Description of the transaction type
            properties: Additional properties for the transaction type
            
        Returns:
            ID of the created transaction type node
        """
        if properties is None:
            properties = {}
            
        properties.update({
            "name": name,
            "description": description
        })
        
        return self.create_node(label="TransactionType", properties=properties)
    
    def create_validation_rule(self, name: str, description: str, rule_type: str, properties: Dict[str, Any] = None) -> str:
        """
        Create a validation rule node in the knowledge graph
        
        Args:
            name: Name of the validation rule
            description: Description of the validation rule
            rule_type: Type of rule (e.g., 'Shariah Check', 'Technical Validation')
            properties: Additional properties for the validation rule
            
        Returns:
            ID of the created validation rule node
        """
        if properties is None:
            properties = {}
            
        properties.update({
            "name": name,
            "description": description,
            "rule_type": rule_type
        })
        
        return self.create_node(label="ValidationRule", properties=properties)
    
    def create_amendment(self, name: str, description: str, status: str, properties: Dict[str, Any] = None) -> str:
        """
        Create an amendment node in the knowledge graph
        
        Args:
            name: Name of the amendment
            description: Description of the amendment
            status: Status of the amendment (e.g., 'Pending', 'Approved', 'Rejected')
            properties: Additional properties for the amendment
            
        Returns:
            ID of the created amendment node
        """
        if properties is None:
            properties = {}
            
        properties.update({
            "name": name,
            "description": description,
            "status": status,
            "created_at": properties.get("created_at", datetime.now().isoformat())
        })
        
        return self.create_node(label="Amendment", properties=properties)
    
    # Relationship methods for Islamic Finance Knowledge Graph
    
    def link_standard_to_concept(self, standard_id: str, concept_id: str, properties: Dict[str, Any] = None) -> str:
        """
        Create a COVERS relationship from a standard to a concept
        
        Args:
            standard_id: ID of the standard node
            concept_id: ID of the concept node
            properties: Optional properties for the relationship
            
        Returns:
            ID of the created relationship
        """
        return self.create_relationship(
            start_node_id=standard_id,
            end_node_id=concept_id,
            relationship_type="COVERS",
            properties=properties
        )
    
    def link_concept_to_principle(self, concept_id: str, principle_id: str, properties: Dict[str, Any] = None) -> str:
        """
        Create a HAS_PRINCIPLE relationship from a concept to a principle
        
        Args:
            concept_id: ID of the concept node
            principle_id: ID of the principle node
            properties: Optional properties for the relationship
            
        Returns:
            ID of the created relationship
        """
        return self.create_relationship(
            start_node_id=concept_id,
            end_node_id=principle_id,
            relationship_type="HAS_PRINCIPLE",
            properties=properties
        )
    
    def link_standard_to_standard(self, source_id: str, target_id: str, properties: Dict[str, Any] = None) -> str:
        """
        Create a REFERENCES relationship between standards
        
        Args:
            source_id: ID of the source standard node
            target_id: ID of the target standard node
            properties: Optional properties for the relationship
            
        Returns:
            ID of the created relationship
        """
        return self.create_relationship(
            start_node_id=source_id,
            end_node_id=target_id,
            relationship_type="REFERENCES",
            properties=properties
        )
    
    def link_amendment_to_standard(self, amendment_id: str, standard_id: str, properties: Dict[str, Any] = None) -> str:
        """
        Create a VALIDATES relationship from an amendment to a standard
        
        Args:
            amendment_id: ID of the amendment node
            standard_id: ID of the standard node
            properties: Optional properties for the relationship
            
        Returns:
            ID of the created relationship
        """
        return self.create_relationship(
            start_node_id=amendment_id,
            end_node_id=standard_id,
            relationship_type="VALIDATES",
            properties=properties
        )
    
    def link_transaction_to_concept(self, transaction_id: str, concept_id: str, properties: Dict[str, Any] = None) -> str:
        """
        Create a USES relationship from a transaction to a concept
        
        Args:
            transaction_id: ID of the transaction node
            concept_id: ID of the concept node
            properties: Optional properties for the relationship
            
        Returns:
            ID of the created relationship
        """
        return self.create_relationship(
            start_node_id=transaction_id,
            end_node_id=concept_id,
            relationship_type="USES",
            properties=properties
        )
    
    def link_validation_to_amendment(self, validation_id: str, amendment_id: str, is_approved: bool, properties: Dict[str, Any] = None) -> str:
        """
        Create an APPROVED_BY or REJECTED_BY relationship from an amendment to a validation rule
        
        Args:
            validation_id: ID of the validation rule node
            amendment_id: ID of the amendment node
            is_approved: Whether the amendment was approved by the validation rule
            properties: Optional properties for the relationship
            
        Returns:
            ID of the created relationship
        """
        relationship_type = "APPROVED_BY" if is_approved else "REJECTED_BY"
        
        return self.create_relationship(
            start_node_id=amendment_id,
            end_node_id=validation_id,
            relationship_type=relationship_type,
            properties=properties
        )
    
    # Query methods for the Islamic Finance Knowledge Graph
    
    def get_concepts(self) -> List[Dict]:
        """
        Get all financial concepts in the knowledge graph
        
        Returns:
            List of concept node dictionaries
        """
        return self.search_nodes(label="Concept")
    
    def get_principles(self) -> List[Dict]:
        """
        Get all Shariah principles in the knowledge graph
        
        Returns:
            List of principle node dictionaries
        """
        return self.search_nodes(label="Principle")
    
    def get_transaction_types(self) -> List[Dict]:
        """
        Get all transaction types in the knowledge graph
        
        Returns:
            List of transaction type node dictionaries
        """
        return self.search_nodes(label="TransactionType")
    
    def get_validation_rules(self) -> List[Dict]:
        """
        Get all validation rules in the knowledge graph
        
        Returns:
            List of validation rule node dictionaries
        """
        return self.search_nodes(label="ValidationRule")
    
    def get_amendments(self, status: str = None) -> List[Dict]:
        """
        Get all amendments in the knowledge graph, optionally filtered by status
        
        Args:
            status: Optional status to filter by (e.g., 'Pending', 'Approved', 'Rejected')
            
        Returns:
            List of amendment node dictionaries
        """
        if status:
            return self.search_nodes(label="Amendment", properties={"status": status})
        return self.search_nodes(label="Amendment")
    
    def get_concepts_for_standard(self, standard_id: str) -> List[Dict]:
        """
        Get all concepts covered by a standard
        
        Args:
            standard_id: ID of the standard
            
        Returns:
            List of concept node dictionaries
        """
        return self.get_related_nodes(standard_id, relationship_type="COVERS")
    
    def get_principles_for_concept(self, concept_id: str) -> List[Dict]:
        """
        Get all principles associated with a concept
        
        Args:
            concept_id: ID of the concept
            
        Returns:
            List of principle node dictionaries
        """
        return self.get_related_nodes(concept_id, relationship_type="HAS_PRINCIPLE")
    
    def get_related_standards(self, standard_id: str) -> List[Dict]:
        """
        Get all standards referenced by a standard
        
        Args:
            standard_id: ID of the standard
            
        Returns:
            List of standard node dictionaries
        """
        return self.get_related_nodes(standard_id, relationship_type="REFERENCES")
    
    def get_amendments_for_standard(self, standard_id: str) -> List[Dict]:
        """
        Get all amendments validating a standard
        
        Args:
            standard_id: ID of the standard
            
        Returns:
            List of amendment node dictionaries
        """
        return self.get_related_nodes(standard_id, relationship_type="VALIDATES", direction="INCOMING")
    
    def get_concept_by_name(self, name: str) -> Optional[Dict]:
        """
        Get a concept by its name
        
        Args:
            name: Name of the concept
            
        Returns:
            Concept node dictionary, or None if not found
        """
        results = self.search_nodes(label="Concept", properties={"name": name})
        return results[0] if results else None
    
    def get_principle_by_name(self, name: str) -> Optional[Dict]:
        """
        Get a principle by its name
        
        Args:
            name: Name of the principle
            
        Returns:
            Principle node dictionary, or None if not found
        """
        results = self.search_nodes(label="Principle", properties={"name": name})
        return results[0] if results else None
    
    def find_path_between_standards(self, source_id: str, target_id: str) -> List[Dict]:
        """
        Find the shortest path between two standards
        
        Args:
            source_id: ID of the source standard
            target_id: ID of the target standard
            
        Returns:
            List of nodes and relationships in the path
        """
        query = """
        MATCH path = shortestPath((source:Standard)-[*]-(target:Standard))
        WHERE id(source) = $source_id AND id(target) = $target_id
        RETURN path
        """
        
        with self.driver.session() as session:
            result = session.run(query, source_id=int(source_id), target_id=int(target_id))
            paths = []
            
            for record in result:
                path = record["path"]
                path_data = {
                    "nodes": [],
                    "relationships": []
                }
                
                for node in path.nodes:
                    path_data["nodes"].append({
                        "id": str(node.id),
                        "labels": list(node.labels),
                        "properties": dict(node)
                    })
                
                for rel in path.relationships:
                    path_data["relationships"].append({
                        "id": str(rel.id),
                        "type": rel.type,
                        "start_node": str(rel.start_node.id),
                        "end_node": str(rel.end_node.id),
                        "properties": dict(rel)
                    })
                
                paths.append(path_data)
            
            return paths
