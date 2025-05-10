#!/usr/bin/env python3
"""
Production-Ready API Server for Islamic Finance Standards Enhancement System

This module provides a RESTful API for the Islamic Finance Standards Enhancement system,
with authentication, rate limiting, and comprehensive error handling.
"""

import os
import sys
import json
import time
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from functools import wraps

# FastAPI imports
from fastapi import FastAPI, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
import uvicorn
import jwt
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import system components
from database.knowledge_graph import KnowledgeGraph
from database.mock_knowledge_graph import MockKnowledgeGraph
import neo4j
from agents.document_agent.document_agent import DocumentAgent
from agents.enhancement_agent.enhancement_agent import EnhancementAgent
from agents.validation_agent.validation_agent import ValidationAgent
from utils.enhanced_audit_logger import get_audit_logger
from utils.resilience import retry, CircuitBreaker, fallback, capture_exception
from utils.monitoring import metrics, performance_monitor, health_check, get_system_status
from extract_enhancements import extract_enhancements_from_logs, display_enhancements

# Import configuration
from config.production import (
    API_CONFIG,
    LOGGING_CONFIG,
    NEO4J_CONFIG,
    DOCUMENT_PROCESSING_CONFIG,
    ENHANCEMENT_CONFIG,
    VALIDATION_CONFIG
)

# Configure logging
log_dir = LOGGING_CONFIG.get("file_path", "logs/")
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, "api_server.log")
log_level = getattr(logging, LOGGING_CONFIG.get("level", "INFO"))

logger = logging.getLogger("api_server")
logger.setLevel(log_level)

# Add rotating file handler
import logging.handlers
file_handler = logging.handlers.RotatingFileHandler(
    log_file,
    maxBytes=LOGGING_CONFIG.get("max_log_size", 10 * 1024 * 1024),
    backupCount=LOGGING_CONFIG.get("backup_count", 5)
)
file_handler.setFormatter(logging.Formatter(LOGGING_CONFIG.get("format")))
logger.addHandler(file_handler)

# Add console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(LOGGING_CONFIG.get("format")))
logger.addHandler(console_handler)

# Initialize audit logger
audit_logger = get_audit_logger()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title="Islamic Finance Standards Enhancement API",
    description="API for enhancing Islamic finance standards with AI-driven proposals",
    version="1.0.0"
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=API_CONFIG.get("cors_origins", ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
JWT_SECRET = API_CONFIG.get("jwt_secret", "your-secret-key")  # Should be loaded from environment in production
JWT_ALGORITHM = API_CONFIG.get("jwt_algorithm", "HS256")
JWT_EXPIRATION = API_CONFIG.get("jwt_expiration_minutes", 30)

# Mock users database - in production, this would be a real database
USERS_DB = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        "disabled": False,
        "role": "admin"
    },
    "user": {
        "username": "user",
        "full_name": "Regular User",
        "email": "user@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        "disabled": False,
        "role": "user"
    }
}

# Knowledge graph connection with resilience
@fallback(lambda: MockKnowledgeGraph())
@CircuitBreaker(name="neo4j_connection", failure_threshold=3, recovery_timeout=60)
@retry(max_attempts=3, delay=2.0, backoff_factor=2.0, 
       exceptions=[neo4j.exceptions.ServiceUnavailable, ConnectionRefusedError])
def get_knowledge_graph():
    """
    Get a knowledge graph instance with robust error handling
    
    Returns:
        KnowledgeGraph instance or MockKnowledgeGraph if connection fails
    """
    try:
        logger.info("Attempting to connect to Neo4j knowledge graph")
        return KnowledgeGraph()
    except (neo4j.exceptions.ServiceUnavailable, ConnectionRefusedError) as e:
        logger.warning(f"Neo4j connection failed: {str(e)}")
        logger.info("Falling back to MockKnowledgeGraph")
        raise  # This will be caught by the retry decorator

# Initialize system components
knowledge_graph = get_knowledge_graph()
document_agent = DocumentAgent(knowledge_graph)
enhancement_agent = EnhancementAgent(knowledge_graph)
validation_agent = ValidationAgent(knowledge_graph)

# Pydantic models for request/response validation
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    role: str = "user"

class StandardDocument(BaseModel):
    title: str
    standard_type: str
    standard_number: str
    publication_date: str
    definitions: List[Dict[str, Any]]
    accounting_treatments: List[Dict[str, Any]]
    transaction_structures: List[Dict[str, Any]]
    ambiguities: List[str]

class EnhancementProposal(BaseModel):
    standard_id: str
    enhancement_type: str
    target_id: str
    original_content: str
    enhanced_content: str
    reasoning: str
    references: Optional[str] = None
    status: str = "PROPOSED"

class ValidationResult(BaseModel):
    proposal_id: str
    status: str
    overall_score: float
    shariah_compliance_score: float
    financial_best_practices_score: float
    clarity_improvement_score: float
    feedback: str

class HealthStatus(BaseModel):
    status: str
    components: Dict[str, Dict[str, Any]]
    timestamp: str

# Authentication functions
def verify_password(plain_password, hashed_password):
    # In production, use proper password hashing like bcrypt
    return plain_password == "password"  # Simplified for demo

def get_user(username: str):
    if username in USERS_DB:
        user_dict = USERS_DB[username]
        return User(**user_dict)
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, USERS_DB[username]["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Middleware for performance monitoring
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    
    # Track request metrics
    metrics.increment("api_requests_total")
    
    try:
        response = await call_next(request)
        
        # Track response time
        process_time = time.time() - start_time
        metrics.observe("api_request_duration_seconds", process_time)
        
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        # Track errors
        metrics.increment("api_errors_total")
        logger.error(f"Request error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# Routes
@app.post("/token", response_model=Token)
@limiter.limit("10/minute")
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=JWT_EXPIRATION)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Log successful login
    audit_logger.log_event(
        event_type="USER_LOGIN",
        data={"username": user.username}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/health")
async def health_check_endpoint():
    """Check the health of the API and its components"""
    health_status = get_system_status()
    return HealthStatus(
        status="healthy" if health_status["overall_status"] == "healthy" else "unhealthy",
        components=health_status["components"],
        timestamp=datetime.now().isoformat()
    )

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@app.post("/documents/process")
@limiter.limit("5/minute")
async def process_document(
    request: Request,
    background_tasks: BackgroundTasks,
    file_path: str,
    current_user: User = Depends(get_current_active_user)
):
    """Process a document and extract structured information"""
    try:
        # Log the request
        logger.info(f"Processing document request: {file_path} by user {current_user.username}")
        
        # Process the document
        with performance_monitor.measure("document_processing"):
            document = document_agent.process_document(file_path)
        
        # Log the successful processing
        audit_logger.log_event(
            event_type="DOCUMENT_PROCESSED",
            data={
                "file_path": file_path,
                "user": current_user.username,
                "document_title": document.title
            }
        )
        
        return jsonable_encoder(document)
    except Exception as e:
        # Log the error
        logger.error(f"Document processing error: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Track the error
        metrics.increment("document_processing_errors")
        
        # Log the error event
        audit_logger.log_event(
            event_type="DOCUMENT_PROCESSING_ERROR",
            data={
                "file_path": file_path,
                "user": current_user.username,
                "error": str(e)
            }
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing error: {str(e)}"
        )

@app.post("/enhancements/generate")
@limiter.limit("10/minute")
async def generate_enhancements(
    request: Request,
    standard_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Generate enhancement proposals for a standard"""
    try:
        # Log the request
        logger.info(f"Generating enhancements for standard {standard_id} by user {current_user.username}")
        
        # Generate enhancements
        with performance_monitor.measure("enhancement_generation"):
            proposals = enhancement_agent.generate_enhancements(standard_id)
        
        # Log the successful generation
        audit_logger.log_event(
            event_type="ENHANCEMENTS_GENERATED",
            data={
                "standard_id": standard_id,
                "user": current_user.username,
                "proposal_count": len(proposals)
            }
        )
        
        return jsonable_encoder(proposals)
    except Exception as e:
        # Log the error
        logger.error(f"Enhancement generation error: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Track the error
        metrics.increment("enhancement_generation_errors")
        
        # Log the error event
        audit_logger.log_event(
            event_type="ENHANCEMENT_GENERATION_ERROR",
            data={
                "standard_id": standard_id,
                "user": current_user.username,
                "error": str(e)
            }
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enhancement generation error: {str(e)}"
        )

@app.post("/validation/validate")
@limiter.limit("15/minute")
async def validate_proposal(
    request: Request,
    proposal_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Validate an enhancement proposal"""
    try:
        # Log the request
        logger.info(f"Validating proposal {proposal_id} by user {current_user.username}")
        
        # Validate the proposal
        with performance_monitor.measure("proposal_validation"):
            validation_result = validation_agent.validate_proposal(proposal_id)
        
        # Log the successful validation
        audit_logger.log_event(
            event_type="PROPOSAL_VALIDATED",
            data={
                "proposal_id": proposal_id,
                "user": current_user.username,
                "validation_status": validation_result.status
            }
        )
        
        return jsonable_encoder(validation_result)
    except Exception as e:
        # Log the error
        logger.error(f"Proposal validation error: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Track the error
        metrics.increment("proposal_validation_errors")
        
        # Log the error event
        audit_logger.log_event(
            event_type="PROPOSAL_VALIDATION_ERROR",
            data={
                "proposal_id": proposal_id,
                "user": current_user.username,
                "error": str(e)
            }
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Proposal validation error: {str(e)}"
        )

@app.get("/enhancements/extract")
@limiter.limit("5/minute")
async def extract_enhancements_endpoint(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Extract enhancement proposals from event logs"""
    try:
        # Log the request
        logger.info(f"Extracting enhancements from logs by user {current_user.username}")
        
        # Extract enhancements
        with performance_monitor.measure("enhancement_extraction"):
            proposals = extract_enhancements_from_logs()
        
        # Log the successful extraction
        audit_logger.log_event(
            event_type="ENHANCEMENTS_EXTRACTED",
            data={
                "user": current_user.username,
                "proposal_count": len(proposals)
            }
        )
        
        return jsonable_encoder(proposals)
    except Exception as e:
        # Log the error
        logger.error(f"Enhancement extraction error: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Track the error
        metrics.increment("enhancement_extraction_errors")
        
        # Log the error event
        audit_logger.log_event(
            event_type="ENHANCEMENT_EXTRACTION_ERROR",
            data={
                "user": current_user.username,
                "error": str(e)
            }
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enhancement extraction error: {str(e)}"
        )

@app.get("/metrics")
async def get_metrics(current_user: User = Depends(get_current_active_user)):
    """Get system metrics (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access metrics"
        )
    
    return metrics.get_all_metrics()

# Main function to run the API server
def main():
    """Run the API server"""
    host = API_CONFIG.get("host", "0.0.0.0")
    port = API_CONFIG.get("port", 8000)
    
    logger.info(f"Starting API server on {host}:{port}")
    
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=API_CONFIG.get("reload", False),
        workers=API_CONFIG.get("workers", 1)
    )

if __name__ == "__main__":
    main()
