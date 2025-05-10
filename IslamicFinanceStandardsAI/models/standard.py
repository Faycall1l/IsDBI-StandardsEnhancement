"""
Standard Model for Islamic Finance Standards Enhancement System

This module defines the data models for representing Islamic finance standards.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class StandardSection:
    """Section of an Islamic finance standard"""
    id: str
    title: str
    content: str
    subsections: List['StandardSection'] = field(default_factory=list)
    
    def to_text(self) -> str:
        """Convert the section to text format"""
        text = f"{self.title}:\n{self.content}\n"
        
        for subsection in self.subsections:
            text += f"\n{subsection.to_text()}"
            
        return text

@dataclass
class Standard:
    """Islamic finance standard"""
    id: str
    name: str
    description: str
    version: str
    publication_date: str
    sections: List[StandardSection] = field(default_factory=list)
    ambiguities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_text(self) -> str:
        """Convert the standard to text format"""
        text = f"{self.name} ({self.id})\n"
        text += f"Version: {self.version}\n"
        text += f"Publication Date: {self.publication_date}\n"
        text += f"Description: {self.description}\n\n"
        
        for section in self.sections:
            text += f"{section.to_text()}\n"
            
        return text
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the standard to a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "publication_date": self.publication_date,
            "sections": [self._section_to_dict(section) for section in self.sections],
            "ambiguities": self.ambiguities,
            "metadata": self.metadata
        }
    
    def _section_to_dict(self, section: StandardSection) -> Dict[str, Any]:
        """Convert a section to a dictionary"""
        return {
            "id": section.id,
            "title": section.title,
            "content": section.content,
            "subsections": [self._section_to_dict(subsection) for subsection in section.subsections]
        }
