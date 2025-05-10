"""
Validation Schema Models

This module defines the data models for validation results and related components.
"""

from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field


class ValidationStatus(str, Enum):
    """Status of a validation result"""
    APPROVED = "APPROVED"
    APPROVED_WITH_MODIFICATIONS = "APPROVED_WITH_MODIFICATIONS"
    REJECTED = "REJECTED"
    NEEDS_REVISION = "NEEDS_REVISION"


class ValidationCriteria(str, Enum):
    """Criteria used for validation"""
    SHARIAH_COMPLIANCE = "SHARIAH_COMPLIANCE"
    TECHNICAL_ACCURACY = "TECHNICAL_ACCURACY"
    CLARITY_AND_PRECISION = "CLARITY_AND_PRECISION"
    PRACTICAL_IMPLEMENTATION = "PRACTICAL_IMPLEMENTATION"
    CONSISTENCY = "CONSISTENCY"


class ValidationResult(BaseModel):
    """Model for a validation result"""
    proposal_id: str
    validation_date: str
    validation_scores: Dict[str, float]
    overall_score: float
    status: ValidationStatus
    feedback: str
    modified_content: Optional[str] = None
