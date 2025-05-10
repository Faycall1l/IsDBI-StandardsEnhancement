#!/usr/bin/env python3
"""
API Server Runner

This script runs the Islamic Finance Standards AI API server with
both original and improved endpoints.
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("api_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import API modules
from improved_endpoints import router as improved_router

# Initialize FastAPI app
app = FastAPI(
    title="Islamic Finance Standards AI",
    description="API for the multi-agent system enhancing AAOIFI standards",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(improved_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to the Islamic Finance Standards AI API",
        "documentation": "/docs",
        "api_version": "2.0.0"
    }

# System status endpoint
@app.get("/system/status")
async def system_status():
    """Get system status"""
    return {
        "status": "operational",
        "api_version": "2.0.0",
        "openai_api": "configured" if os.getenv("OPENAI_API_KEY") else "not configured",
        "neo4j_connection": "configured"
    }

# Run the application
if __name__ == "__main__":
    import uvicorn
    
    # Get host and port from environment variables or use defaults
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    logger.info(f"Starting API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
