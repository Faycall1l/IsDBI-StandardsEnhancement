"""
Mock Knowledge Graph for Testing

This module provides a mock implementation of the knowledge graph
that can be used for testing without requiring a Neo4j database.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional, Union

class MockKnowledgeGraph:
    """In-memory mock implementation of the knowledge graph for testing"""
    
    def __init__(self):
        """Initialize the mock knowledge graph"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing mock knowledge graph for testing")
        
        # In-memory storage
        self.nodes = {}
        self.relationships = {}
        
        # Node and relationship counters for generating IDs
        self.node_counter = 0
        self.relationship_counter = 0
    
    def close(self):
        """Close the mock knowledge graph connection"""
        self.logger.info("Closing mock knowledge graph connection")
        # No actual connection to close
    
    def create_node(self, label: str, properties: Dict[str, Any]) -> str:
        """Create a node in the knowledge graph"""
        node_id = str(self.node_counter)
        self.node_counter += 1
        
        self.nodes[node_id] = {
            "id": node_id,
            "label": label,
            "properties": properties
        }
        
        self.logger.info(f"Created {label} node with ID: {node_id}")
        return node_id
    
    def update_node(self, node_id: str, properties: Dict[str, Any]) -> bool:
        """Update a node in the knowledge graph"""
        if node_id not in self.nodes:
            self.logger.warning(f"Node with ID {node_id} not found")
            return False
        
        # Update properties
        self.nodes[node_id]["properties"].update(properties)
        self.logger.info(f"Updated node with ID: {node_id}")
        return True
    
    def delete_node(self, node_id: str) -> bool:
        """Delete a node from the knowledge graph"""
        if node_id not in self.nodes:
            self.logger.warning(f"Node with ID {node_id} not found")
            return False
        
        # Delete the node
        del self.nodes[node_id]
        
        # Delete relationships involving this node
        relationships_to_delete = []
        for rel_id, rel in self.relationships.items():
            if rel["start_node_id"] == node_id or rel["end_node_id"] == node_id:
                relationships_to_delete.append(rel_id)
        
        for rel_id in relationships_to_delete:
            del self.relationships[rel_id]
        
        self.logger.info(f"Deleted node with ID: {node_id} and {len(relationships_to_delete)} relationships")
        return True
    
    def get_node_by_id(self, node_id: str) -> Optional[Dict]:
        """Get a node by its ID"""
        if node_id not in self.nodes:
            self.logger.warning(f"Node with ID {node_id} not found")
            return None
        
        return self.nodes[node_id]
    
    def search_nodes(self, label: str, properties: Dict[str, Any]) -> List[Dict]:
        """Search for nodes by label and properties"""
        results = []
        
        for node_id, node in self.nodes.items():
            if node["label"] != label:
                continue
            
            # Check if all specified properties match
            match = True
            for key, value in properties.items():
                if key not in node["properties"] or node["properties"][key] != value:
                    match = False
                    break
            
            if match:
                results.append(node)
        
        self.logger.info(f"Found {len(results)} nodes matching search criteria")
        return results
    
    def create_relationship(self, start_node_id: str, end_node_id: str, relationship_type: str, properties: Dict[str, Any] = None) -> str:
        """Create a relationship between two nodes"""
        if start_node_id not in self.nodes:
            self.logger.warning(f"Start node with ID {start_node_id} not found")
            return None
        
        if end_node_id not in self.nodes:
            self.logger.warning(f"End node with ID {end_node_id} not found")
            return None
        
        if properties is None:
            properties = {}
        
        relationship_id = str(self.relationship_counter)
        self.relationship_counter += 1
        
        self.relationships[relationship_id] = {
            "id": relationship_id,
            "start_node_id": start_node_id,
            "end_node_id": end_node_id,
            "type": relationship_type,
            "properties": properties
        }
        
        self.logger.info(f"Created {relationship_type} relationship with ID: {relationship_id}")
        return relationship_id
    
    def get_related_nodes(self, node_id: str, relationship_type: str = None) -> List[Dict]:
        """Get nodes related to a given node"""
        if node_id not in self.nodes:
            self.logger.warning(f"Node with ID {node_id} not found")
            return []
        
        related_nodes = []
        
        # Find relationships where this node is the start or end
        for rel_id, rel in self.relationships.items():
            # Filter by relationship type if specified
            if relationship_type and rel["type"] != relationship_type:
                continue
            
            related_node_id = None
            
            if rel["start_node_id"] == node_id:
                related_node_id = rel["end_node_id"]
            elif rel["end_node_id"] == node_id:
                related_node_id = rel["start_node_id"]
            
            if related_node_id and related_node_id in self.nodes:
                related_node = self.nodes[related_node_id].copy()
                related_node["relationship"] = {
                    "id": rel_id,
                    "type": rel["type"],
                    "properties": rel["properties"]
                }
                related_nodes.append(related_node)
        
        self.logger.info(f"Found {len(related_nodes)} nodes related to node {node_id}")
        return related_nodes
    
    # Specialized methods for Islamic finance standards
    
    def create_standard(self, title: str, standard_type: str, standard_number: str, publication_date: str, description: str = "") -> str:
        """Create a standard node"""
        return self.create_node(
            label="Standard",
            properties={
                "title": title,
                "standard_type": standard_type,
                "standard_number": standard_number,
                "publication_date": publication_date,
                "description": description
            }
        )
    
    def create_concept(self, name: str, description: str) -> str:
        """Create a concept node"""
        return self.create_node(
            label="Concept",
            properties={
                "name": name,
                "description": description
            }
        )
    
    def create_principle(self, name: str, description: str) -> str:
        """Create a Shariah principle node"""
        return self.create_node(
            label="Principle",
            properties={
                "name": name,
                "description": description
            }
        )
    
    def create_transaction_type(self, name: str, description: str) -> str:
        """Create a transaction type node"""
        return self.create_node(
            label="TransactionType",
            properties={
                "name": name,
                "description": description
            }
        )
    
    def create_validation_rule(self, name: str, description: str, rule_type: str) -> str:
        """Create a validation rule node"""
        return self.create_node(
            label="ValidationRule",
            properties={
                "name": name,
                "description": description,
                "rule_type": rule_type
            }
        )
    
    def create_amendment(self, standard_id: str, amendment_type: str, description: str, content: str, effective_date: str) -> str:
        """Create an amendment node"""
        amendment_id = self.create_node(
            label="Amendment",
            properties={
                "amendment_type": amendment_type,
                "description": description,
                "content": content,
                "effective_date": effective_date
            }
        )
        
        # Link the amendment to the standard
        self.create_relationship(
            start_node_id=amendment_id,
            end_node_id=standard_id,
            relationship_type="AMENDS"
        )
        
        return amendment_id
    
    # Relationship methods
    
    def link_standard_to_concept(self, standard_id: str, concept_id: str, properties: Dict[str, Any] = None) -> str:
        """Link a standard to a concept"""
        return self.create_relationship(
            start_node_id=standard_id,
            end_node_id=concept_id,
            relationship_type="COVERS",
            properties=properties
        )
    
    def link_concept_to_principle(self, concept_id: str, principle_id: str, properties: Dict[str, Any] = None) -> str:
        """Link a concept to a Shariah principle"""
        return self.create_relationship(
            start_node_id=concept_id,
            end_node_id=principle_id,
            relationship_type="HAS_PRINCIPLE",
            properties=properties
        )
    
    def link_standard_to_standard(self, source_id: str, target_id: str, properties: Dict[str, Any] = None) -> str:
        """Link a standard to another standard"""
        return self.create_relationship(
            start_node_id=source_id,
            end_node_id=target_id,
            relationship_type="REFERENCES",
            properties=properties
        )
    
    # Query methods
    
    def get_standards(self) -> List[Dict]:
        """Get all standards"""
        return [node for node_id, node in self.nodes.items() if node["label"] == "Standard"]
    
    def get_concepts(self) -> List[Dict]:
        """Get all concepts"""
        return [node for node_id, node in self.nodes.items() if node["label"] == "Concept"]
    
    def get_principles(self) -> List[Dict]:
        """Get all principles"""
        return [node for node_id, node in self.nodes.items() if node["label"] == "Principle"]
    
    def get_concepts_for_standard(self, standard_id: str) -> List[Dict]:
        """Get concepts covered by a standard"""
        concepts = []
        
        for rel_id, rel in self.relationships.items():
            if rel["start_node_id"] == standard_id and rel["type"] == "COVERS":
                concept_id = rel["end_node_id"]
                if concept_id in self.nodes and self.nodes[concept_id]["label"] == "Concept":
                    concepts.append(self.nodes[concept_id])
        
        return concepts
    
    def get_principles_for_concept(self, concept_id: str) -> List[Dict]:
        """Get principles for a concept"""
        principles = []
        
        for rel_id, rel in self.relationships.items():
            if rel["start_node_id"] == concept_id and rel["type"] == "HAS_PRINCIPLE":
                principle_id = rel["end_node_id"]
                if principle_id in self.nodes and self.nodes[principle_id]["label"] == "Principle":
                    principles.append(self.nodes[principle_id])
        
        return principles
    
    def get_amendments_for_standard(self, standard_id: str) -> List[Dict]:
        """Get amendments for a standard"""
        amendments = []
        
        for rel_id, rel in self.relationships.items():
            if rel["end_node_id"] == standard_id and rel["type"] == "AMENDS":
                amendment_id = rel["start_node_id"]
                if amendment_id in self.nodes and self.nodes[amendment_id]["label"] == "Amendment":
                    amendments.append(self.nodes[amendment_id])
        
        return amendments
    
    def get_enhancements_for_standard(self, standard_id: str) -> List[Dict]:
        """Get enhancement proposals for a standard"""
        enhancements = []
        
        for node_id, node in self.nodes.items():
            if node["label"] == "EnhancementProposal" and node["properties"].get("standard_id") == standard_id:
                enhancements.append(node)
        
        return enhancements
    
    def get_principle_by_name(self, name: str) -> Optional[Dict]:
        """Get a principle by name"""
        for node_id, node in self.nodes.items():
            if node["label"] == "Principle" and node["properties"].get("name") == name:
                return node
        
        return None
    
    def get_definitions_for_standard(self, standard_id: str) -> List[Dict]:
        """Get definitions for a standard"""
        definitions = []
        
        for rel_id, rel in self.relationships.items():
            if rel["start_node_id"] == standard_id and rel["type"] == "HAS_DEFINITION":
                definition_id = rel["end_node_id"]
                if definition_id in self.nodes and self.nodes[definition_id]["label"] == "Definition":
                    definitions.append(self.nodes[definition_id])
        
        return definitions
    
    def get_accounting_treatments_for_standard(self, standard_id: str) -> List[Dict]:
        """Get accounting treatments for a standard"""
        treatments = []
        
        for rel_id, rel in self.relationships.items():
            if rel["start_node_id"] == standard_id and rel["type"] == "HAS_ACCOUNTING_TREATMENT":
                treatment_id = rel["end_node_id"]
                if treatment_id in self.nodes and self.nodes[treatment_id]["label"] == "AccountingTreatment":
                    treatments.append(self.nodes[treatment_id])
        
        return treatments
    
    def get_transaction_structures_for_standard(self, standard_id: str) -> List[Dict]:
        """Get transaction structures for a standard"""
        structures = []
        
        for rel_id, rel in self.relationships.items():
            if rel["start_node_id"] == standard_id and rel["type"] == "HAS_TRANSACTION_STRUCTURE":
                structure_id = rel["end_node_id"]
                if structure_id in self.nodes and self.nodes[structure_id]["label"] == "TransactionStructure":
                    structures.append(self.nodes[structure_id])
        
        return structures
    
    def get_ambiguities_for_standard(self, standard_id: str) -> List[Dict]:
        """Get ambiguities for a standard"""
        ambiguities = []
        
        for rel_id, rel in self.relationships.items():
            if rel["start_node_id"] == standard_id and rel["type"] == "HAS_AMBIGUITY":
                ambiguity_id = rel["end_node_id"]
                if ambiguity_id in self.nodes and self.nodes[ambiguity_id]["label"] == "Ambiguity":
                    ambiguities.append(self.nodes[ambiguity_id])
        
        return ambiguities
    
    def find_path_between_standards(self, source_id: str, target_id: str) -> List[List[Dict]]:
        """Find paths between two standards"""
        # Simple implementation that just checks for direct connections
        paths = []
        
        for rel_id, rel in self.relationships.items():
            if rel["start_node_id"] == source_id and rel["end_node_id"] == target_id:
                paths.append([
                    self.nodes[source_id],
                    self.nodes[target_id]
                ])
        
        return paths
