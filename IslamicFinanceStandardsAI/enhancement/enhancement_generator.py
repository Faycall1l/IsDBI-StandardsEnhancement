"""
Enhancement Generator for Islamic Finance Standards
This module provides functionality to generate enhancement suggestions for AAOIFI standards
using a combination of RAG, web search, and knowledge graph integration.
"""

import re
import json
from typing import Dict, Any, List, Optional

class EnhancementGenerator:
    """
    A class for generating enhancement suggestions for Islamic finance standards.
    Uses a combination of RAG, web search, and knowledge graph integration.
    """
    
    def __init__(self, knowledge_graph=None, web_retriever=None, embeddings=None):
        """
        Initialize the EnhancementGenerator with necessary components.
        
        Args:
            knowledge_graph: The knowledge graph for storing and retrieving standards information
            web_retriever: Component for retrieving relevant information from the web
            embeddings: Component for generating and comparing embeddings
        """
        self.knowledge_graph = knowledge_graph
        self.web_retriever = web_retriever
        self.embeddings = embeddings
    
    def generate_enhancement(self, standard_id: str, standard_text: str, 
                            use_web_search: bool = True) -> Dict[str, Any]:
        """
        Generate an enhancement suggestion for a given standard text.
        
        Args:
            standard_id: The ID of the standard to enhance
            standard_text: The text of the standard to enhance
            use_web_search: Whether to use web search to find relevant information
            
        Returns:
            A dictionary containing the enhanced text, rationale, and other metadata
        """
        # Step 1: Extract key concepts from the standard text
        key_concepts = self._extract_key_concepts(standard_text)
        
        # Step 2: Retrieve relevant information from the knowledge graph
        kg_info = self._retrieve_from_knowledge_graph(standard_id, key_concepts)
        
        # Step 3: If enabled, search the web for additional information
        web_info = []
        if use_web_search and self.web_retriever:
            search_query = f"AAOIFI {standard_id} {' '.join(key_concepts[:3])} Islamic finance standards best practices"
            web_info = self._search_web(search_query)
        
        # Step 4: Generate the enhancement
        enhancement = self._generate_enhancement_text(standard_text, key_concepts, kg_info, web_info)
        
        # Step 5: Generate rationale for the enhancement
        rationale = self._generate_rationale(standard_text, enhancement, key_concepts, web_info)
        
        # Step 6: Return the result
        return {
            "standard_id": standard_id,
            "original_text": standard_text,
            "enhanced_text": enhancement,
            "rationale": rationale,
            "key_concepts": key_concepts,
            "web_sources": [source.get("title", "Unknown Source") for source in web_info]
        }
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from the standard text"""
        # Simple implementation - extract words that might be key concepts
        # In a real implementation, this would use NLP techniques
        words = re.findall(r'\b[A-Za-z]{4,}\b', text)
        # Filter common words and get unique concepts
        common_words = {'this', 'that', 'with', 'from', 'have', 'will', 'been', 'were', 'they', 'their', 'should'}
        concepts = [word.lower() for word in words if word.lower() not in common_words]
        # Return unique concepts
        return list(set(concepts))
    
    def _retrieve_from_knowledge_graph(self, standard_id: str, key_concepts: List[str]) -> List[Dict[str, Any]]:
        """Retrieve relevant information from the knowledge graph"""
        if not self.knowledge_graph:
            return []
        
        try:
            # Try to find the standard in the knowledge graph
            standard_node = self.knowledge_graph.find_nodes_by_properties(
                label="Standard",
                properties={"standard_id": standard_id}
            )
            
            # If standard exists, find related nodes
            if standard_node:
                related_nodes = self.knowledge_graph.get_related_nodes(standard_node[0]["id"])
                return related_nodes
            
            # If standard doesn't exist, search by key concepts
            results = []
            for concept in key_concepts[:5]:  # Limit to top 5 concepts
                concept_nodes = self.knowledge_graph.find_nodes_by_text_search(concept)
                results.extend(concept_nodes)
            
            return results
        except Exception as e:
            print(f"Error retrieving from knowledge graph: {e}")
            return []
    
    def _search_web(self, query: str) -> List[Dict[str, Any]]:
        """Search the web for relevant information"""
        if not self.web_retriever:
            return []
        
        try:
            search_results = self.web_retriever.search(query, max_results=5)
            return search_results
        except Exception as e:
            print(f"Error searching the web: {e}")
            return []
    
    def _generate_enhancement_text(self, original_text: str, key_concepts: List[str], 
                                 kg_info: List[Dict[str, Any]], web_info: List[Dict[str, Any]]) -> str:
        """Generate the enhanced text based on all available information"""
        # This is a simplified implementation
        # In a real system, this would use a more sophisticated approach
        
        # For demo purposes, we'll make some simple enhancements
        enhancements = []
        
        # Add clarity improvements
        if len(original_text.split()) > 20:  # If text is reasonably long
            enhancements.append("The standard should clearly define all key terms used.")
        
        # Add modern financial practices
        if "digital" not in original_text.lower() and "technology" not in original_text.lower():
            enhancements.append("The standard should address digital assets and technological innovations.")
        
        # Add risk management considerations
        if "risk" not in original_text.lower():
            enhancements.append("The standard should include comprehensive risk management guidelines.")
        
        # Add Shariah compliance emphasis
        if "shariah" not in original_text.lower() and "shari'ah" not in original_text.lower():
            enhancements.append("The standard should emphasize Shariah compliance verification procedures.")
        
        # Incorporate web information if available
        if web_info:
            web_concepts = set()
            for info in web_info:
                if "snippet" in info:
                    # Extract potentially useful phrases from web snippets
                    phrases = re.findall(r'([A-Z][^.!?]*?(compliance|standard|practice|principle|requirement)[^.!?]*[.!?])', 
                                        info.get("snippet", ""))
                    for phrase in phrases:
                        web_concepts.add(phrase[0])
            
            # Add insights from web search
            for concept in list(web_concepts)[:2]:  # Limit to 2 insights
                enhancements.append(concept)
        
        # Combine the original text with enhancements
        enhanced_text = original_text + "\n\nAdditional enhancements:\n"
        enhanced_text += "\n".join([f"- {enhancement}" for enhancement in enhancements])
        
        return enhanced_text
    
    def _generate_rationale(self, original_text: str, enhanced_text: str, 
                          key_concepts: List[str], web_info: List[Dict[str, Any]]) -> str:
        """Generate a rationale for the enhancement"""
        # Identify the main differences between original and enhanced
        enhancements = enhanced_text.replace(original_text, "").strip()
        
        # Generate rationale based on the enhancements
        rationale_parts = [
            "This enhancement addresses several key areas for improvement in the standard:",
        ]
        
        # Add rationale for clarity improvements
        if "define all key terms" in enhancements:
            rationale_parts.append("- Improved clarity through explicit definition of key terms, which reduces ambiguity in interpretation.")
        
        # Add rationale for digital/technology additions
        if "digital assets" in enhancements or "technological innovations" in enhancements:
            rationale_parts.append("- Incorporation of digital assets and technological innovations to ensure the standard remains relevant in the modern financial landscape.")
        
        # Add rationale for risk management
        if "risk management" in enhancements:
            rationale_parts.append("- Addition of risk management guidelines to help financial institutions implement the standard while maintaining appropriate risk controls.")
        
        # Add rationale for Shariah compliance
        if "Shariah compliance" in enhancements:
            rationale_parts.append("- Strengthened Shariah compliance verification procedures to ensure adherence to Islamic principles.")
        
        # Add rationale based on web sources
        if web_info:
            rationale_parts.append("- Integration of current best practices identified through analysis of recent publications and industry standards.")
        
        # Combine all rationale parts
        rationale = "\n".join(rationale_parts)
        
        return rationale
