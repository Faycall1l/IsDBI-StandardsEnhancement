"""
Enhancement Proposal Model for Islamic Finance Standards Enhancement System

This module defines the data model for representing enhancement proposals.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class EnhancementProposal:
    """Enhancement proposal for an Islamic finance standard"""
    id: str
    standard_id: str
    title: str
    description: str
    status: str  # DRAFT, SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED
    created_by: str
    created_at: str
    updated_at: Optional[str] = None
    approved_at: Optional[str] = None
    approved_by: Optional[str] = None
    validation_score: Optional[float] = None
    validation_feedback: Optional[str] = None
    claims: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the enhancement proposal to a dictionary"""
        return {
            "id": self.id,
            "standard_id": self.standard_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "approved_at": self.approved_at,
            "approved_by": self.approved_by,
            "validation_score": self.validation_score,
            "validation_feedback": self.validation_feedback,
            "claims": self.claims,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnhancementProposal':
        """Create an enhancement proposal from a dictionary"""
        return cls(
            id=data.get("id"),
            standard_id=data.get("standard_id"),
            title=data.get("title"),
            description=data.get("description"),
            status=data.get("status"),
            created_by=data.get("created_by"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            approved_at=data.get("approved_at"),
            approved_by=data.get("approved_by"),
            validation_score=data.get("validation_score"),
            validation_feedback=data.get("validation_feedback"),
            claims=data.get("claims", []),
            metadata=data.get("metadata", {})
        )
