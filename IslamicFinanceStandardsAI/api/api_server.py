#!/usr/bin/env python3
"""
Islamic Finance Standards Enhancement API Server

This module provides a production-ready FastAPI server that exposes the functionality
of the Islamic Finance Standards Enhancement system through RESTful endpoints.
"""

import os
import sys
import json
import time
import logging
import uvicorn
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Request, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
import jwt
from jwt.exceptions import PyJWTError

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import system components
from database.knowledge_graph import KnowledgeGraph
from database.mock_knowledge_graph import MockKnowledgeGraph
from agents.document_agent.document_agent import DocumentAgent
from agents.enhancement_agent.enhancement_agent import EnhancementAgent
from agents.validation_agent.validation_agent import ValidationAgent
from utils.enhanced_audit_logger import get_audit_logger
from utils.resilience import retry, CircuitBreaker, fallback, capture_exception
from utils.monitoring import metrics, performance_monitor, monitor_endpoint, get_system_status
from config.production import (
    LOGGING_CONFIG, 
    NEO4J_CONFIG, 
    API_CONFIG,
    DOCUMENT_PROCESSING_CONFIG
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG.get("level", "INFO")),
    format=LOGGING_CONFIG.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
    handlers=[
        logging.FileHandler(os.path.join(LOGGING_CONFIG.get("file_path", "logs/"), "api_server.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize audit logger
audit_logger = get_audit_logger()

# Get knowledge graph instance
@fallback(lambda: MockKnowledgeGraph())
@CircuitBreaker(name="neo4j_connection", failure_threshold=3, recovery_timeout=60)
def get_knowledge_graph():
    """Get a knowledge graph instance with fallback to mock implementation"""
    try:
        return KnowledgeGraph()
    except Exception as e:
        logger.warning(f"Failed to connect to Neo4j: {str(e)}")
        logger.info("Falling back to MockKnowledgeGraph")
        raise

# Initialize knowledge graph
knowledge_graph = get_knowledge_graph()

# Initialize agents
document_agent = DocumentAgent(knowledge_graph)
enhancement_agent = EnhancementAgent(knowledge_graph)
validation_agent = ValidationAgent(knowledge_graph)

# Create FastAPI app
app = FastAPI(
    title="Islamic Finance Standards Enhancement API",
    description="API for enhancing Islamic finance standards through AI-driven analysis and proposals",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=API_CONFIG.get("cors_origins", ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
JWT_SECRET = API_CONFIG.get("auth", {}).get("jwt_secret", "islamic_finance_standards_secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = API_CONFIG.get("auth", {}).get("token_expiry", 86400)  # 24 hours

# Request rate limiting
if API_CONFIG.get("rate_limit", {}).get("enabled", False):
    import time
    from fastapi import Request
    from starlette.middleware.base import BaseHTTPMiddleware
    
    class RateLimitMiddleware(BaseHTTPMiddleware):
        def __init__(self, app, requests_per_minute=60):
            super().__init__(app)
            self.requests_per_minute = requests_per_minute
            self.request_timestamps = {}
        
        async def dispatch(self, request: Request, call_next):
            client_ip = request.client.host
            current_time = time.time()
            
            # Clean up old timestamps
            self.request_timestamps = {
                ip: timestamps for ip, timestamps in self.request_timestamps.items()
                if timestamps and timestamps[-1] > current_time - 60
            }
            
            # Get timestamps for this client
            if client_ip not in self.request_timestamps:
                self.request_timestamps[client_ip] = []
            
            timestamps = self.request_timestamps[client_ip]
            
            # Check if rate limit exceeded
            if len(timestamps) >= self.requests_per_minute:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded. Please try again later."}
                )
            
            # Add current timestamp
            timestamps.append(current_time)
            
            # Process the request
            return await call_next(request)
    
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=API_CONFIG.get("rate_limit", {}).get("requests_per_minute", 60)
    )

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Record API metrics
    endpoint = request.url.path
    metrics.record_api_metric(f"{endpoint}_response_time", process_time)
    
    return response

# Pydantic models for request/response validation
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class DocumentRequest(BaseModel):
    document_path: str = Field(..., description="Path to the document to process")

class EnhancementRequest(BaseModel):
    standard_id: str = Field(..., description="ID of the standard to enhance")

class ValidationRequest(BaseModel):
    proposal_id: str = Field(..., description="ID of the proposal to validate")

class SystemStatusResponse(BaseModel):
    status: str
    components: Dict[str, Any]
    metrics: Dict[str, Any]
    timestamp: str

# Mock user database for demonstration
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    }
}

# Authentication functions
def verify_password(plain_password, hashed_password):
    # In production, use proper password hashing
    return plain_password == "secret" and hashed_password == "fakehashedsecret"

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: int = JWT_EXPIRATION):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(seconds=expires_delta)
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
        token_data = TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Authentication endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    
    # Log authentication event
    audit_logger.log_event(
        event_type="USER_AUTHENTICATED",
        data={"username": user.username},
        actor=user.username
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# API endpoints
@app.get("/", tags=["General"])
async def root():
    """Root endpoint providing API information"""
    return {
        "name": "Islamic Finance Standards Enhancement API",
        "version": "1.0.0",
        "description": "API for enhancing Islamic finance standards through AI-driven analysis and proposals"
    }

@app.get("/health", tags=["Monitoring"], response_model=SystemStatusResponse)
@monitor_endpoint("health")
async def health_check():
    """Health check endpoint"""
    status = get_system_status()
    
    # Simplify for response
    response = {
        "status": status["health"]["overall_status"],
        "components": {
            name: check["status"] 
            for name, check in status["health"]["checks"].items()
        },
        "metrics": {
            "cpu": status["metrics"]["system"]["cpu"]["percent"],
            "memory": status["metrics"]["system"]["memory"]["percent_used"],
            "uptime": status["metrics"]["system"]["uptime_seconds"]
        },
        "timestamp": datetime.now().isoformat()
    }
    
    return response

@app.post("/documents/process", tags=["Document Processing"])
@monitor_endpoint("process_document")
async def process_document(
    request: DocumentRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """Process a document and extract structured information"""
    try:
        # Process document in background
        def process_document_task(document_path):
            try:
                result = document_agent.process_document(document_path)
                
                # Log success
                audit_logger.log_event(
                    event_type="DOCUMENT_PROCESSED",
                    data={
                        "document_path": document_path,
                        "result": {
                            "title": result.title,
                            "standard_type": result.standard_type,
                            "standard_number": result.standard_number
                        }
                    },
                    actor=current_user.username
                )
                
                return result
            except Exception as e:
                # Log failure
                audit_logger.log_event(
                    event_type="DOCUMENT_PROCESSING_FAILED",
                    data={
                        "document_path": document_path,
                        "error": str(e)
                    },
                    actor=current_user.username
                )
                logger.error(f"Error processing document: {str(e)}")
                raise
        
        # Add task to background
        background_tasks.add_task(process_document_task, request.document_path)
        
        return {
            "status": "processing",
            "message": "Document processing started in background",
            "document_path": request.document_path
        }
        
    except Exception as e:
        logger.error(f"Error initiating document processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/enhancements/generate", tags=["Enhancement Generation"])
@monitor_endpoint("generate_enhancements")
async def generate_enhancements(
    request: EnhancementRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """Generate enhancement proposals for a standard"""
    try:
        # Generate enhancements in background
        def generate_enhancements_task(standard_id):
            try:
                proposals = enhancement_agent.generate_enhancements(standard_id)
                
                # Log success
                audit_logger.log_event(
                    event_type="ENHANCEMENTS_GENERATED",
                    data={
                        "standard_id": standard_id,
                        "proposals_count": len(proposals)
                    },
                    actor=current_user.username
                )
                
                return proposals
            except Exception as e:
                # Log failure
                audit_logger.log_event(
                    event_type="ENHANCEMENT_GENERATION_FAILED",
                    data={
                        "standard_id": standard_id,
                        "error": str(e)
                    },
                    actor=current_user.username
                )
                logger.error(f"Error generating enhancements: {str(e)}")
                raise
        
        # Add task to background
        background_tasks.add_task(generate_enhancements_task, request.standard_id)
        
        return {
            "status": "processing",
            "message": "Enhancement generation started in background",
            "standard_id": request.standard_id
        }
        
    except Exception as e:
        logger.error(f"Error initiating enhancement generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/validations/validate", tags=["Validation"])
@monitor_endpoint("validate_proposal")
async def validate_proposal(
    request: ValidationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Validate an enhancement proposal"""
    try:
        # Validate proposal
        result = validation_agent.validate_proposal(request.proposal_id)
        
        # Log validation
        audit_logger.log_event(
            event_type="PROPOSAL_VALIDATED",
            data={
                "proposal_id": request.proposal_id,
                "validation_result": {
                    "status": result.status.value if hasattr(result, 'status') else result.get('status'),
                    "overall_score": result.overall_score if hasattr(result, 'overall_score') else result.get('overall_score')
                }
            },
            actor=current_user.username
        )
        
        return {
            "status": "success",
            "proposal_id": request.proposal_id,
            "validation_result": result
        }
        
    except Exception as e:
        logger.error(f"Error validating proposal: {str(e)}")
        
        # Log failure
        audit_logger.log_event(
            event_type="PROPOSAL_VALIDATION_FAILED",
            data={
                "proposal_id": request.proposal_id,
                "error": str(e)
            },
            actor=current_user.username
        )
        
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/standards", tags=["Standards"])
@monitor_endpoint("get_standards")
async def get_standards(current_user: User = Depends(get_current_active_user)):
    """Get all standards in the knowledge graph"""
    try:
        standards = knowledge_graph.get_standards()
        
        # Log access
        audit_logger.log_event(
            event_type="STANDARDS_ACCESSED",
            data={"count": len(standards)},
            actor=current_user.username
        )
        
        return {"standards": standards}
        
    except Exception as e:
        logger.error(f"Error retrieving standards: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/standards/{standard_id}/enhancements", tags=["Standards"])
@monitor_endpoint("get_enhancements_for_standard")
async def get_enhancements_for_standard(
    standard_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get all enhancement proposals for a standard"""
    try:
        enhancements = knowledge_graph.get_enhancements_for_standard(standard_id)
        
        # Log access
        audit_logger.log_event(
            event_type="ENHANCEMENTS_ACCESSED",
            data={
                "standard_id": standard_id,
                "count": len(enhancements)
            },
            actor=current_user.username
        )
        
        return {"enhancements": enhancements}
        
    except Exception as e:
        logger.error(f"Error retrieving enhancements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics", tags=["Monitoring"])
@monitor_endpoint("get_metrics")
async def get_metrics(current_user: User = Depends(get_current_active_user)):
    """Get system metrics"""
    try:
        return {"metrics": metrics.get_all_metrics()}
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audit-logs", tags=["Monitoring"])
@monitor_endpoint("get_audit_logs")
async def get_audit_logs(
    event_type: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    """Get audit logs with optional filtering"""
    try:
        events = audit_logger.get_events(event_type=event_type, limit=limit)
        
        # Log access
        audit_logger.log_event(
            event_type="AUDIT_LOGS_ACCESSED",
            data={
                "filter_event_type": event_type,
                "limit": limit,
                "count": len(events)
            },
            actor=current_user.username
        )
        
        return {"events": events}
        
    except Exception as e:
        logger.error(f"Error retrieving audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    
    # Log error
    audit_logger.log_event(
        event_type="API_ERROR",
        data={
            "path": request.url.path,
            "method": request.method,
            "error": str(exc)
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"}
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("Starting Islamic Finance Standards Enhancement API server")
    
    # Log startup
    audit_logger.log_event(
        event_type="API_SERVER_STARTED",
        data={"config": API_CONFIG}
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Shutting down Islamic Finance Standards Enhancement API server")
    
    # Close knowledge graph connection
    if hasattr(knowledge_graph, 'close'):
        knowledge_graph.close()
    
    # Flush audit logs
    audit_logger.flush()
    
    # Log shutdown
    audit_logger.log_event(
        event_type="API_SERVER_SHUTDOWN",
        data={}
    )

# Main function to run the server
def main():
    """Run the API server"""
    # Create logs directory if it doesn't exist
    os.makedirs(LOGGING_CONFIG.get("file_path", "logs/"), exist_ok=True)
    
    # Run server
    uvicorn.run(
        "api_server:app",
        host=API_CONFIG.get("host", "0.0.0.0"),
        port=API_CONFIG.get("port", 8000),
        reload=False,
        workers=API_CONFIG.get("workers", 4)
    )

if __name__ == "__main__":
    main()
