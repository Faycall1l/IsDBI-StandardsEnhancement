"""
Enhancement Schema Models

This module defines the data models for enhancement proposals and related components.
"""

from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field


class EnhancementType(str, Enum):
    """Types of enhancements that can be proposed"""
    DEFINITION = "DEFINITION"
    ACCOUNTING_TREATMENT = "ACCOUNTING_TREATMENT"
    TRANSACTION_STRUCTURE = "TRANSACTION_STRUCTURE"
    AMBIGUITY_RESOLUTION = "AMBIGUITY_RESOLUTION"
    NEW_GUIDANCE = "NEW_GUIDANCE"


class EnhancementStatus(str, Enum):
    """Status of an enhancement proposal"""
    PROPOSED = "PROPOSED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    APPROVED_WITH_MODIFICATIONS = "APPROVED_WITH_MODIFICATIONS"
    REJECTED = "REJECTED"


class Enhancement(BaseModel):
    """Base model for an enhancement"""
    content: str
    reasoning: str
    references: str


class EnhancementProposal(BaseModel):
    """Model for a complete enhancement proposal"""
    standard_id: str
    enhancement_type: str
    target_id: str  # ID of the target node (definition, accounting treatment, etc.)
    original_content: str
    enhanced_content: str
    reasoning: str
    references: str
    status: str = EnhancementStatus.PROPOSED
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
