"""
Improved API Endpoints

This module provides enhanced API endpoints for the Islamic Finance Standards AI system,
optimized for handling large documents and managing API request volume.
"""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Path, Body, File, UploadFile, Form, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from database.knowledge_graph import KnowledgeGraph
from agents.document_agent.document_agent import DocumentAgent
from agents.enhancement_agent.enhancement_agent import EnhancementAgent
from agents.validation_agent.validation_agent import ValidationAgent

# Initialize router
router = APIRouter(prefix="/v2", tags=["improved-api"])

# Initialize logger
logger = logging.getLogger(__name__)

# Define request/response models
class DocumentSectionRequest(BaseModel):
    """Request model for processing specific sections of a document"""
    file_path: str
    sections: List[str] = Field(default_factory=list, description="Specific sections to extract (empty for all)")
    max_pages: Optional[int] = Field(None, description="Maximum number of pages to process")

class BatchProcessRequest(BaseModel):
    """Request model for batch processing multiple documents"""
    file_paths: List[str]
    batch_size: int = Field(2, description="Number of documents to process in each batch")
    delay_seconds: int = Field(5, description="Delay between batches in seconds")

class EnhancementLimitedRequest(BaseModel):
    """Request model for generating a limited number of enhancements"""
    standard_id: str
    max_count: int = Field(3, description="Maximum number of enhancements to generate")
    types: List[str] = Field(default_factory=list, description="Types of enhancements to prioritize")

class ProcessingStatus(BaseModel):
    """Response model for task processing status"""
    task_id: str
    status: str
    progress: float = Field(0.0, description="Progress percentage (0-100)")
    message: str = Field("", description="Status message")
    result_id: Optional[str] = None

# Task storage
background_tasks = {}

# Knowledge graph dependency
def get_knowledge_graph():
    """Get or create a knowledge graph instance"""
    kg = KnowledgeGraph()
    try:
        yield kg
    finally:
        kg.close()

# Agent dependencies
def get_document_agent(kg: KnowledgeGraph = Depends(get_knowledge_graph)):
    """Get a document agent instance"""
    return DocumentAgent(kg)

def get_enhancement_agent(kg: KnowledgeGraph = Depends(get_knowledge_graph)):
    """Get an enhancement agent instance"""
    return EnhancementAgent(kg)

def get_validation_agent(kg: KnowledgeGraph = Depends(get_knowledge_graph)):
    """Get a validation agent instance"""
    return ValidationAgent(kg)

# Document processing endpoints
@router.post("/documents/process-sections", response_model=ProcessingStatus)
async def process_document_sections(
    request: DocumentSectionRequest, 
    background_tasks: BackgroundTasks,
    document_agent: DocumentAgent = Depends(get_document_agent)
):
    """Process specific sections of a document"""
    try:
        # Check if file exists
        if not os.path.exists(request.file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
        
        # Generate task ID
        task_id = f"doc_section_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.path.basename(request.file_path)}"
        
        # Initialize task status
        background_tasks[task_id] = {
            "status": "queued",
            "progress": 0.0,
            "message": "Document processing queued",
            "result_id": None
        }
        
        # Define the background task
        def process_document_background(task_id, file_path, sections, max_pages):
            try:
                # Update status
                background_tasks[task_id]["status"] = "processing"
                background_tasks[task_id]["progress"] = 10.0
                background_tasks[task_id]["message"] = "Extracting text from document"
                
                # Process document with section filtering
                document = document_agent.process_document(
                    file_path, 
                    max_pages=max_pages,
                    sections_to_extract=sections if sections else None
                )
                
                # Update progress
                background_tasks[task_id]["progress"] = 60.0
                background_tasks[task_id]["message"] = "Storing in knowledge graph"
                
                # Get the ID from the knowledge graph
                standards = document_agent.knowledge_graph.search_nodes(
                    label="Standard",
                    properties={
                        "title": document.title
                    }
                )
                
                if not standards:
                    background_tasks[task_id]["status"] = "failed"
                    background_tasks[task_id]["message"] = "Failed to store document in knowledge graph"
                    return
                
                standard_id = standards[0]["id"]
                
                # Update task status
                background_tasks[task_id]["status"] = "completed"
                background_tasks[task_id]["progress"] = 100.0
                background_tasks[task_id]["message"] = "Document processing completed"
                background_tasks[task_id]["result_id"] = standard_id
                
            except Exception as e:
                logger.error(f"Error in background task {task_id}: {str(e)}")
                background_tasks[task_id]["status"] = "failed"
                background_tasks[task_id]["message"] = f"Error: {str(e)}"
        
        # Add the task to background_tasks
        background_tasks.add_task(
            process_document_background, 
            task_id, 
            request.file_path, 
            request.sections,
            request.max_pages
        )
        
        return {
            "task_id": task_id,
            "status": "queued",
            "progress": 0.0,
            "message": "Document processing queued"
        }
        
    except Exception as e:
        logger.error(f"Error processing document sections: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/batch-process", response_model=List[ProcessingStatus])
async def batch_process_documents(
    request: BatchProcessRequest, 
    background_tasks: BackgroundTasks,
    document_agent: DocumentAgent = Depends(get_document_agent)
):
    """Process multiple documents in batches"""
    try:
        task_ids = []
        
        # Check if files exist
        for file_path in request.file_paths:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        # Define the background task
        def process_batch_background(file_paths, batch_size, delay_seconds):
            for i in range(0, len(file_paths), batch_size):
                batch = file_paths[i:i+batch_size]
                
                # Process each file in the batch
                for file_path in batch:
                    task_id = f"batch_doc_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.path.basename(file_path)}"
                    task_ids.append(task_id)
                    
                    # Initialize task status
                    background_tasks[task_id] = {
                        "status": "queued",
                        "progress": 0.0,
                        "message": "Document processing queued",
                        "result_id": None
                    }
                    
                    try:
                        # Update status
                        background_tasks[task_id]["status"] = "processing"
                        background_tasks[task_id]["progress"] = 10.0
                        
                        # Process document
                        document = document_agent.process_document(file_path)
                        
                        # Get the ID from the knowledge graph
                        standards = document_agent.knowledge_graph.search_nodes(
                            label="Standard",
                            properties={
                                "title": document.title
                            }
                        )
                        
                        if not standards:
                            background_tasks[task_id]["status"] = "failed"
                            background_tasks[task_id]["message"] = "Failed to store document in knowledge graph"
                            continue
                        
                        standard_id = standards[0]["id"]
                        
                        # Update task status
                        background_tasks[task_id]["status"] = "completed"
                        background_tasks[task_id]["progress"] = 100.0
                        background_tasks[task_id]["message"] = "Document processing completed"
                        background_tasks[task_id]["result_id"] = standard_id
                        
                    except Exception as e:
                        logger.error(f"Error in batch task {task_id}: {str(e)}")
                        background_tasks[task_id]["status"] = "failed"
                        background_tasks[task_id]["message"] = f"Error: {str(e)}"
                
                # Delay between batches
                if i + batch_size < len(file_paths):
                    time.sleep(delay_seconds)
        
        # Add the batch processing task to background_tasks
        background_tasks.add_task(
            process_batch_background, 
            request.file_paths, 
            request.batch_size,
            request.delay_seconds
        )
        
        # Return initial task statuses
        return [
            {
                "task_id": f"batch_doc_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.path.basename(file_path)}",
                "status": "queued",
                "progress": 0.0,
                "message": f"Document {i+1}/{len(request.file_paths)} queued for batch processing"
            }
            for i, file_path in enumerate(request.file_paths)
        ]
        
    except Exception as e:
        logger.error(f"Error batch processing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}", response_model=ProcessingStatus)
async def get_task_status(task_id: str):
    """Get the status of a background task"""
    if task_id not in background_tasks:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
    
    task_info = background_tasks[task_id]
    return {
        "task_id": task_id,
        **task_info
    }

# Enhanced enhancement endpoints
@router.post("/enhancements/limited", response_model=ProcessingStatus)
async def generate_limited_enhancements(
    request: EnhancementLimitedRequest, 
    background_tasks: BackgroundTasks,
    enhancement_agent: EnhancementAgent = Depends(get_enhancement_agent)
):
    """Generate a limited number of high-priority enhancements"""
    try:
        # Check if standard exists
        standard = enhancement_agent.knowledge_graph.get_node_by_id(request.standard_id)
        if not standard:
            raise HTTPException(status_code=404, detail=f"Standard with ID {request.standard_id} not found")
        
        # Generate task ID
        task_id = f"enh_limited_{datetime.now().strftime('%Y%m%d%H%M%S')}_{request.standard_id}"
        
        # Initialize task status
        background_tasks[task_id] = {
            "status": "queued",
            "progress": 0.0,
            "message": "Enhancement generation queued",
            "result_ids": []
        }
        
        # Define the background task
        def generate_enhancements_background(task_id, standard_id, max_count, types):
            try:
                # Update status
                background_tasks[task_id]["status"] = "processing"
                background_tasks[task_id]["progress"] = 10.0
                background_tasks[task_id]["message"] = "Retrieving context from knowledge graph"
                
                # Get enhanced context for better quality
                related_nodes = enhancement_agent.knowledge_graph.get_related_nodes(standard_id)
                standard_info = enhancement_agent.knowledge_graph.get_node_by_id(standard_id)
                
                # Update progress
                background_tasks[task_id]["progress"] = 30.0
                background_tasks[task_id]["message"] = "Generating enhancements"
                
                # Process enhancements with prioritization by type
                all_proposals = enhancement_agent.generate_enhancements(standard_id)
                
                # Filter and limit enhancements based on types and max_count
                if types:
                    # Prioritize requested types
                    prioritized_proposals = [p for p in all_proposals if p.enhancement_type in types]
                    other_proposals = [p for p in all_proposals if p.enhancement_type not in types]
                    limited_proposals = prioritized_proposals[:max_count]
                    
                    # Fill remaining slots if needed
                    if len(limited_proposals) < max_count:
                        remaining_slots = max_count - len(limited_proposals)
                        limited_proposals.extend(other_proposals[:remaining_slots])
                else:
                    # Just take the first max_count proposals
                    limited_proposals = all_proposals[:max_count]
                
                # Get proposal IDs from the knowledge graph
                proposal_ids = []
                for proposal in limited_proposals:
                    # Search for the proposal
                    proposals = enhancement_agent.knowledge_graph.search_nodes(
                        label="EnhancementProposal",
                        properties={
                            "standard_id": standard_id,
                            "enhancement_type": proposal.enhancement_type
                        }
                    )
                    
                    if proposals:
                        proposal_ids.append(proposals[0]["id"])
                
                # Update task status
                background_tasks[task_id]["status"] = "completed"
                background_tasks[task_id]["progress"] = 100.0
                background_tasks[task_id]["message"] = f"Generated {len(proposal_ids)} enhancements"
                background_tasks[task_id]["result_ids"] = proposal_ids
                
            except Exception as e:
                logger.error(f"Error in background task {task_id}: {str(e)}")
                background_tasks[task_id]["status"] = "failed"
                background_tasks[task_id]["message"] = f"Error: {str(e)}"
        
        # Add the task to background_tasks
        background_tasks.add_task(
            generate_enhancements_background, 
            task_id, 
            request.standard_id, 
            request.max_count,
            request.types
        )
        
        return {
            "task_id": task_id,
            "status": "queued",
            "progress": 0.0,
            "message": "Enhancement generation queued"
        }
        
    except Exception as e:
        logger.error(f"Error generating limited enhancements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Smart validation endpoints
@router.post("/validations/batch", response_model=ProcessingStatus)
async def batch_validate_proposals(
    proposal_ids: List[str] = Body(..., description="List of proposal IDs to validate"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    validation_agent: ValidationAgent = Depends(get_validation_agent)
):
    """Validate multiple enhancement proposals in a batch"""
    try:
        # Check if proposals exist
        for proposal_id in proposal_ids:
            proposal = validation_agent.knowledge_graph.get_node_by_id(proposal_id)
            if not proposal:
                raise HTTPException(status_code=404, detail=f"Proposal with ID {proposal_id} not found")
        
        # Generate task ID
        task_id = f"val_batch_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Initialize task status
        background_tasks[task_id] = {
            "status": "queued",
            "progress": 0.0,
            "message": "Batch validation queued",
            "result_ids": []
        }
        
        # Define the background task
        def validate_batch_background(task_id, proposal_ids):
            try:
                # Update status
                background_tasks[task_id]["status"] = "processing"
                background_tasks[task_id]["progress"] = 5.0
                
                validation_ids = []
                total_proposals = len(proposal_ids)
                
                for i, proposal_id in enumerate(proposal_ids):
                    try:
                        # Update progress
                        progress = 5.0 + (90.0 * (i / total_proposals))
                        background_tasks[task_id]["progress"] = progress
                        background_tasks[task_id]["message"] = f"Validating proposal {i+1}/{total_proposals}"
                        
                        # Validate proposal
                        validation_result = validation_agent.validate_proposal(proposal_id)
                        
                        # Get the ID from the knowledge graph
                        validation_nodes = validation_agent.knowledge_graph.get_related_nodes(
                            proposal_id,
                            relationship_type="HAS_VALIDATION",
                            direction="INCOMING"
                        )
                        
                        if validation_nodes:
                            validation_ids.append(validation_nodes[0]["id"])
                            
                            # Update proposal status
                            validation_agent.knowledge_graph.update_node(
                                proposal_id,
                                {"status": validation_result.status.value}
                            )
                    
                    except Exception as e:
                        logger.error(f"Error validating proposal {proposal_id}: {str(e)}")
                        # Continue with other proposals
                
                # Update task status
                background_tasks[task_id]["status"] = "completed"
                background_tasks[task_id]["progress"] = 100.0
                background_tasks[task_id]["message"] = f"Validated {len(validation_ids)}/{total_proposals} proposals"
                background_tasks[task_id]["result_ids"] = validation_ids
                
            except Exception as e:
                logger.error(f"Error in background task {task_id}: {str(e)}")
                background_tasks[task_id]["status"] = "failed"
                background_tasks[task_id]["message"] = f"Error: {str(e)}"
        
        # Add the task to background_tasks
        background_tasks.add_task(
            validate_batch_background, 
            task_id, 
            proposal_ids
        )
        
        return {
            "task_id": task_id,
            "status": "queued",
            "progress": 0.0,
            "message": "Batch validation queued"
        }
        
    except Exception as e:
        logger.error(f"Error batch validating proposals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Multi-agent orchestration endpoint
@router.post("/orchestration/full-pipeline", response_model=ProcessingStatus)
async def run_full_pipeline(
    file_path: str = Body(..., description="Path to the document to process"),
    enhancement_limit: int = Body(3, description="Maximum number of enhancements to generate"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    document_agent: DocumentAgent = Depends(get_document_agent),
    enhancement_agent: EnhancementAgent = Depends(get_enhancement_agent),
    validation_agent: ValidationAgent = Depends(get_validation_agent)
):
    """Run the full multi-agent pipeline on a document"""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        
        # Generate task ID
        task_id = f"pipeline_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.path.basename(file_path)}"
        
        # Initialize task status
        background_tasks[task_id] = {
            "status": "queued",
            "progress": 0.0,
            "message": "Pipeline processing queued",
            "result": {
                "standard_id": None,
                "enhancement_ids": [],
                "validation_ids": []
            }
        }
        
        # Define the background task
        def run_pipeline_background(task_id, file_path, enhancement_limit):
            try:
                # Step 1: Document processing
                background_tasks[task_id]["status"] = "processing"
                background_tasks[task_id]["progress"] = 5.0
                background_tasks[task_id]["message"] = "Processing document"
                
                document = document_agent.process_document(file_path)
                
                # Get the standard ID
                standards = document_agent.knowledge_graph.search_nodes(
                    label="Standard",
                    properties={
                        "title": document.title
                    }
                )
                
                if not standards:
                    background_tasks[task_id]["status"] = "failed"
                    background_tasks[task_id]["message"] = "Failed to store document in knowledge graph"
                    return
                
                standard_id = standards[0]["id"]
                background_tasks[task_id]["result"]["standard_id"] = standard_id
                
                # Step 2: Generate enhancements
                background_tasks[task_id]["progress"] = 30.0
                background_tasks[task_id]["message"] = "Generating enhancements"
                
                all_proposals = enhancement_agent.generate_enhancements(standard_id)
                limited_proposals = all_proposals[:enhancement_limit]
                
                # Get proposal IDs
                proposal_ids = []
                for proposal in limited_proposals:
                    # Search for the proposal
                    proposals = enhancement_agent.knowledge_graph.search_nodes(
                        label="EnhancementProposal",
                        properties={
                            "standard_id": standard_id,
                            "enhancement_type": proposal.enhancement_type
                        }
                    )
                    
                    if proposals:
                        proposal_ids.append(proposals[0]["id"])
                
                background_tasks[task_id]["result"]["enhancement_ids"] = proposal_ids
                
                # Step 3: Validate enhancements
                background_tasks[task_id]["progress"] = 60.0
                background_tasks[task_id]["message"] = "Validating enhancements"
                
                validation_ids = []
                for proposal_id in proposal_ids:
                    # Validate proposal
                    validation_result = validation_agent.validate_proposal(proposal_id)
                    
                    # Get validation ID
                    validation_nodes = validation_agent.knowledge_graph.get_related_nodes(
                        proposal_id,
                        relationship_type="HAS_VALIDATION",
                        direction="INCOMING"
                    )
                    
                    if validation_nodes:
                        validation_ids.append(validation_nodes[0]["id"])
                        
                        # Update proposal status
                        validation_agent.knowledge_graph.update_node(
                            proposal_id,
                            {"status": validation_result.status.value}
                        )
                
                background_tasks[task_id]["result"]["validation_ids"] = validation_ids
                
                # Pipeline completed
                background_tasks[task_id]["status"] = "completed"
                background_tasks[task_id]["progress"] = 100.0
                background_tasks[task_id]["message"] = "Pipeline processing completed"
                
            except Exception as e:
                logger.error(f"Error in pipeline task {task_id}: {str(e)}")
                background_tasks[task_id]["status"] = "failed"
                background_tasks[task_id]["message"] = f"Error: {str(e)}"
        
        # Add the task to background_tasks
        background_tasks.add_task(
            run_pipeline_background, 
            task_id, 
            file_path,
            enhancement_limit
        )
        
        return {
            "task_id": task_id,
            "status": "queued",
            "progress": 0.0,
            "message": "Pipeline processing queued"
        }
        
    except Exception as e:
        logger.error(f"Error running pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# File upload endpoint for document processing
@router.post("/upload-and-process", response_model=ProcessingStatus)
async def upload_and_process(
    file: UploadFile = File(...),
    sections: str = Form(""),
    max_pages: Optional[int] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    document_agent: DocumentAgent = Depends(get_document_agent)
):
    """Upload a document file and process it"""
    try:
        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, f"{timestamp}_{file.filename}")
        
        # Save the uploaded file
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        # Parse sections if provided
        section_list = []
        if sections:
            section_list = [s.strip() for s in sections.split(",")]
        
        # Generate task ID
        task_id = f"upload_{timestamp}_{file.filename}"
        
        # Initialize task status
        background_tasks[task_id] = {
            "status": "queued",
            "progress": 0.0,
            "message": "Document upload and processing queued",
            "result_id": None,
            "file_path": file_path
        }
        
        # Define the background task
        def process_uploaded_document(task_id, file_path, sections, max_pages):
            try:
                # Update status
                background_tasks[task_id]["status"] = "processing"
                background_tasks[task_id]["progress"] = 10.0
                background_tasks[task_id]["message"] = "Extracting text from document"
                
                # Process document with section filtering
                document = document_agent.process_document(
                    file_path, 
                    max_pages=max_pages,
                    sections_to_extract=sections if sections else None
                )
                
                # Update progress
                background_tasks[task_id]["progress"] = 60.0
                background_tasks[task_id]["message"] = "Storing in knowledge graph"
                
                # Get the ID from the knowledge graph
                standards = document_agent.knowledge_graph.search_nodes(
                    label="Standard",
                    properties={
                        "title": document.title
                    }
                )
                
                if not standards:
                    background_tasks[task_id]["status"] = "failed"
                    background_tasks[task_id]["message"] = "Failed to store document in knowledge graph"
                    return
                
                standard_id = standards[0]["id"]
                
                # Update task status
                background_tasks[task_id]["status"] = "completed"
                background_tasks[task_id]["progress"] = 100.0
                background_tasks[task_id]["message"] = "Document processing completed"
                background_tasks[task_id]["result_id"] = standard_id
                
            except Exception as e:
                logger.error(f"Error in background task {task_id}: {str(e)}")
                background_tasks[task_id]["status"] = "failed"
                background_tasks[task_id]["message"] = f"Error: {str(e)}"
        
        # Add the task to background_tasks
        background_tasks.add_task(
            process_uploaded_document, 
            task_id, 
            file_path, 
            section_list,
            max_pages
        )
        
        return {
            "task_id": task_id,
            "status": "queued",
            "progress": 0.0,
            "message": f"Document uploaded and queued for processing: {file.filename}"
        }
        
    except Exception as e:
        logger.error(f"Error uploading and processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
