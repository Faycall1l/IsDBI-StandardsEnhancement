"""
Document Schema Models

This module defines the data models for AAOIFI standard documents and their components.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class Definition(BaseModel):
    """Model for a term definition in a standard"""
    term: str
    definition: str
    source_text: Optional[str] = None


class AccountingTreatment(BaseModel):
    """Model for an accounting treatment in a standard"""
    title: str
    description: str
    source_text: Optional[str] = None


class TransactionStructure(BaseModel):
    """Model for a transaction structure in a standard"""
    title: str
    steps: List[str] = Field(default_factory=list)
    description: str
    source_text: Optional[str] = None


class StandardDocument(BaseModel):
    """Model for a complete standard document"""
    title: str
    standard_type: str  # FAS or SS
    standard_number: str
    publication_date: str
    definitions: List[Definition] = Field(default_factory=list)
    accounting_treatments: List[AccountingTreatment] = Field(default_factory=list)
    transaction_structures: List[TransactionStructure] = Field(default_factory=list)
    ambiguities: List[Dict[str, str]] = Field(default_factory=list)
    raw_text: Optional[str] = None
