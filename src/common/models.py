from pydantic import BaseModel, Field
from typing import List, Optional
import uuid

class StandardDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    source_standard: str  # e.g., "FAS 4", "FAS 10", "FAS 32"
    content: str
    identified_ambiguities: List[str] = Field(default_factory=list)
    # Potentially add other structured data extracted by Document Processing Agent

class EnhancementProposal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_standard_id: str
    original_standard_title: str
    proposed_enhancement_text: str
    chain_of_thought_reasoning: str
    status: str = "generated" # e.g., generated, validated, rejected
    # Potentially add sections like 'affected_clauses', 'impact_assessment'
