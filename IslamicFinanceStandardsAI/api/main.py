"""
Main API Module

This module provides the FastAPI application and endpoints for the Islamic Finance Standards AI system.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database.knowledge_graph import KnowledgeGraph
from agents.document_agent.document_agent import DocumentAgent
from agents.enhancement_agent.enhancement_agent import EnhancementAgent
from agents.validation_agent.validation_agent import ValidationAgent
from models.document_schema import StandardDocument
from models.enhancement_schema import EnhancementProposal
from models.validation_schema import ValidationResult

# Initialize FastAPI app
app = FastAPI(
    title="Islamic Finance Standards AI",
    description="API for the multi-agent system enhancing AAOIFI standards",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize knowledge graph
knowledge_graph = KnowledgeGraph()

# Initialize agents
document_agent = DocumentAgent(knowledge_graph)
enhancement_agent = EnhancementAgent(knowledge_graph)
validation_agent = ValidationAgent(knowledge_graph)

# Define request/response models
class DocumentProcessRequest(BaseModel):
    file_path: str

class EnhancementRequest(BaseModel):
    standard_id: str

class ValidationRequest(BaseModel):
    proposal_id: str

class StandardResponse(BaseModel):
    id: str
    title: str
    standard_type: str
    standard_number: str
    publication_date: str

class EnhancementResponse(BaseModel):
    id: str
    standard_id: str
    enhancement_type: str
    target_id: str
    status: str

class ValidationResponse(BaseModel):
    id: str
    proposal_id: str
    status: str
    overall_score: float

# API endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to the Islamic Finance Standards AI API"}

# Document Agent endpoints
@app.post("/documents/process", response_model=StandardResponse)
async def process_document(request: DocumentProcessRequest, background_tasks: BackgroundTasks):
    """Process a document and extract structured information"""
    try:
        # Check if file exists
        if not os.path.exists(request.file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
        
        # Process document
        document = document_agent.process_document(request.file_path)
        
        # Get the ID from the knowledge graph
        standards = knowledge_graph.search_nodes(
            label="Standard",
            properties={
                "title": document.title,
                "standard_type": document.standard_type,
                "standard_number": document.standard_number
            }
        )
        
        if not standards:
            raise HTTPException(status_code=500, detail="Failed to store document in knowledge graph")
        
        standard_id = standards[0]["id"]
        
        return {
            "id": standard_id,
            "title": document.title,
            "standard_type": document.standard_type,
            "standard_number": document.standard_number,
            "publication_date": document.publication_date
        }
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents", response_model=List[StandardResponse])
async def get_standards():
    """Get all standards in the knowledge graph"""
    try:
        standards = knowledge_graph.get_standards()
        
        return [
            {
                "id": standard["id"],
                "title": standard["properties"]["title"],
                "standard_type": standard["properties"]["standard_type"],
                "standard_number": standard["properties"]["standard_number"],
                "publication_date": standard["properties"]["publication_date"]
            }
            for standard in standards
        ]
        
    except Exception as e:
        logger.error(f"Error getting standards: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{standard_id}", response_model=Dict[str, Any])
async def get_standard_details(standard_id: str = Path(..., description="ID of the standard")):
    """Get detailed information about a standard"""
    try:
        # Get standard information
        standard = knowledge_graph.get_node_by_id(standard_id)
        if not standard:
            raise HTTPException(status_code=404, detail=f"Standard with ID {standard_id} not found")
        
        # Get related information
        definitions = knowledge_graph.get_definitions_for_standard(standard_id)
        accounting_treatments = knowledge_graph.get_accounting_treatments_for_standard(standard_id)
        transaction_structures = knowledge_graph.get_transaction_structures_for_standard(standard_id)
        ambiguities = knowledge_graph.get_ambiguities_for_standard(standard_id)
        
        return {
            "id": standard["id"],
            "title": standard["properties"]["title"],
            "standard_type": standard["properties"]["standard_type"],
            "standard_number": standard["properties"]["standard_number"],
            "publication_date": standard["properties"]["publication_date"],
            "definitions": [node["properties"] for node in definitions],
            "accounting_treatments": [node["properties"] for node in accounting_treatments],
            "transaction_structures": [node["properties"] for node in transaction_structures],
            "ambiguities": [node["properties"] for node in ambiguities]
        }
        
    except Exception as e:
        logger.error(f"Error getting standard details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhancement Agent endpoints
@app.post("/enhancements/generate", response_model=List[EnhancementResponse])
async def generate_enhancements(request: EnhancementRequest, background_tasks: BackgroundTasks):
    """Generate enhancement proposals for a standard"""
    try:
        # Check if standard exists
        standard = knowledge_graph.get_node_by_id(request.standard_id)
        if not standard:
            raise HTTPException(status_code=404, detail=f"Standard with ID {request.standard_id} not found")
        
        # Generate enhancements in the background
        background_tasks.add_task(
            enhancement_agent.generate_enhancements,
            request.standard_id
        )
        
        return {"message": "Enhancement generation started in the background"}
        
    except Exception as e:
        logger.error(f"Error generating enhancements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/enhancements", response_model=List[EnhancementResponse])
async def get_enhancements(
    standard_id: Optional[str] = Query(None, description="Filter by standard ID"),
    enhancement_type: Optional[str] = Query(None, description="Filter by enhancement type"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """Get enhancement proposals with optional filters"""
    try:
        # Build query parameters
        query_params = {}
        if standard_id:
            query_params["standard_id"] = standard_id
        if enhancement_type:
            query_params["enhancement_type"] = enhancement_type
        if status:
            query_params["status"] = status
        
        # Search for enhancements
        enhancements = knowledge_graph.search_nodes(label="EnhancementProposal", properties=query_params)
        
        return [
            {
                "id": enhancement["id"],
                "standard_id": enhancement["properties"]["standard_id"],
                "enhancement_type": enhancement["properties"]["enhancement_type"],
                "target_id": enhancement["properties"]["target_id"],
                "status": enhancement["properties"]["status"]
            }
            for enhancement in enhancements
        ]
        
    except Exception as e:
        logger.error(f"Error getting enhancements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/enhancements/{proposal_id}", response_model=Dict[str, Any])
async def get_enhancement_details(proposal_id: str = Path(..., description="ID of the enhancement proposal")):
    """Get detailed information about an enhancement proposal"""
    try:
        # Get proposal information
        proposal = knowledge_graph.get_node_by_id(proposal_id)
        if not proposal:
            raise HTTPException(status_code=404, detail=f"Proposal with ID {proposal_id} not found")
        
        # Get validation results
        validation_nodes = knowledge_graph.get_related_nodes(
            proposal_id,
            relationship_type="HAS_VALIDATION",
            direction="INCOMING"
        )
        
        validations = []
        for validation in validation_nodes:
            # Get validation scores
            score_nodes = knowledge_graph.get_related_nodes(
                validation["id"],
                relationship_type="HAS_SCORE"
            )
            
            scores = {
                node["properties"]["criterion"]: node["properties"]["score"]
                for node in score_nodes
            }
            
            validations.append({
                "id": validation["id"],
                "validation_date": validation["properties"]["validation_date"],
                "overall_score": validation["properties"]["overall_score"],
                "status": validation["properties"]["status"],
                "feedback": validation["properties"]["feedback"],
                "modified_content": validation["properties"]["modified_content"],
                "scores": scores
            })
        
        return {
            "id": proposal["id"],
            "standard_id": proposal["properties"]["standard_id"],
            "enhancement_type": proposal["properties"]["enhancement_type"],
            "target_id": proposal["properties"]["target_id"],
            "original_content": proposal["properties"]["original_content"],
            "enhanced_content": proposal["properties"]["enhanced_content"],
            "reasoning": proposal["properties"]["reasoning"],
            "references": proposal["properties"]["references"],
            "status": proposal["properties"]["status"],
            "validations": validations
        }
        
    except Exception as e:
        logger.error(f"Error getting enhancement details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Validation Agent endpoints
@app.post("/validations/validate", response_model=ValidationResponse)
async def validate_proposal(request: ValidationRequest, background_tasks: BackgroundTasks):
    """Validate an enhancement proposal"""
    try:
        # Check if proposal exists
        proposal = knowledge_graph.get_node_by_id(request.proposal_id)
        if not proposal:
            raise HTTPException(status_code=404, detail=f"Proposal with ID {request.proposal_id} not found")
        
        # Validate proposal
        validation_result = validation_agent.validate_proposal(request.proposal_id)
        
        # Get the ID from the knowledge graph
        validation_nodes = knowledge_graph.get_related_nodes(
            request.proposal_id,
            relationship_type="HAS_VALIDATION",
            direction="INCOMING"
        )
        
        if not validation_nodes:
            raise HTTPException(status_code=500, detail="Failed to store validation result in knowledge graph")
        
        validation_id = validation_nodes[0]["id"]
        
        # Update proposal status
        knowledge_graph.update_node(
            request.proposal_id,
            {"status": validation_result.status.value}
        )
        
        return {
            "id": validation_id,
            "proposal_id": request.proposal_id,
            "status": validation_result.status.value,
            "overall_score": validation_result.overall_score
        }
        
    except Exception as e:
        logger.error(f"Error validating proposal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/validations", response_model=List[ValidationResponse])
async def get_validations(
    proposal_id: Optional[str] = Query(None, description="Filter by proposal ID"),
    status: Optional[str] = Query(None, description="Filter by validation status")
):
    """Get validation results with optional filters"""
    try:
        # Build query parameters
        query_params = {}
        if status:
            query_params["status"] = status
        
        # Search for validations
        validations = knowledge_graph.search_nodes(label="ValidationResult", properties=query_params)
        
        # Filter by proposal ID if specified
        if proposal_id:
            validations = [v for v in validations if v["properties"]["proposal_id"] == proposal_id]
        
        return [
            {
                "id": validation["id"],
                "proposal_id": validation["properties"]["proposal_id"],
                "status": validation["properties"]["status"],
                "overall_score": validation["properties"]["overall_score"]
            }
            for validation in validations
        ]
        
    except Exception as e:
        logger.error(f"Error getting validations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/validations/{validation_id}", response_model=Dict[str, Any])
async def get_validation_details(validation_id: str = Path(..., description="ID of the validation result")):
    """Get detailed information about a validation result"""
    try:
        # Get validation information
        validation = knowledge_graph.get_node_by_id(validation_id)
        if not validation:
            raise HTTPException(status_code=404, detail=f"Validation with ID {validation_id} not found")
        
        # Get validation scores
        score_nodes = knowledge_graph.get_related_nodes(
            validation_id,
            relationship_type="HAS_SCORE"
        )
        
        scores = {
            node["properties"]["criterion"]: node["properties"]["score"]
            for node in score_nodes
        }
        
        return {
            "id": validation["id"],
            "proposal_id": validation["properties"]["proposal_id"],
            "validation_date": validation["properties"]["validation_date"],
            "overall_score": validation["properties"]["overall_score"],
            "status": validation["properties"]["status"],
            "feedback": validation["properties"]["feedback"],
            "modified_content": validation["properties"]["modified_content"],
            "scores": scores
        }
        
    except Exception as e:
        logger.error(f"Error getting validation details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
