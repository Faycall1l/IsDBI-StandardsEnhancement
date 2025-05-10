"""
Production Configuration for Islamic Finance Standards Enhancement System

This module provides production-level configuration settings for the system,
including database connections, API keys, logging levels, and other parameters.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
NEO4J_CONFIG = {
    "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    "user": os.getenv("NEO4J_USER", "neo4j"),
    "password": os.getenv("NEO4J_PASSWORD", "password"),
    "max_connection_lifetime": 3600,
    "max_connection_pool_size": 50,
    "connection_timeout": 30,
    "connection_acquisition_timeout": 60,
    "retry_count": 3
}

# OpenAI API Configuration
OPENAI_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000,
    "timeout": 60,
    "retry_count": 3,
    "retry_delay": 5  # seconds
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_path": os.getenv("LOG_FILE_PATH", "logs/"),
    "rotate_logs": True,
    "max_log_size": 10 * 1024 * 1024,  # 10 MB
    "backup_count": 5
}

# Document Processing Configuration
DOCUMENT_PROCESSING_CONFIG = {
    "spacy_model": "en_core_web_lg",
    "max_document_size": 50 * 1024 * 1024,  # 50 MB
    "supported_formats": ["pdf", "docx", "txt"],
    "extraction_timeout": 300,  # seconds
    "parallel_processing": True,
    "max_workers": 4
}

# Enhancement Generation Configuration
ENHANCEMENT_CONFIG = {
    "max_proposals_per_standard": 10,
    "enhancement_types": [
        "DEFINITION",
        "ACCOUNTING_TREATMENT",
        "TRANSACTION_STRUCTURE",
        "AMBIGUITY_RESOLUTION",
        "NEW_GUIDANCE"
    ],
    "cot_reasoning": True,
    "max_context_length": 6000
}

# Validation Configuration
VALIDATION_CONFIG = {
    "criteria": {
        "SHARIAH_COMPLIANCE": {"weight": 0.35},
        "TECHNICAL_ACCURACY": {"weight": 0.25},
        "CLARITY_AND_PRECISION": {"weight": 0.20},
        "PRACTICAL_IMPLEMENTATION": {"weight": 0.15},
        "CONSISTENCY": {"weight": 0.05}
    },
    "approval_threshold": 0.8,
    "modification_threshold": 0.6
}

# Audit Logging Configuration
AUDIT_CONFIG = {
    "enabled": True,
    "storage_path": os.getenv("AUDIT_LOG_PATH", "audit_logs/"),
    "retention_period": 365,  # days
    "encryption_enabled": True,
    "encryption_key": os.getenv("AUDIT_ENCRYPTION_KEY")
}

# API Configuration
API_CONFIG = {
    "host": os.getenv("API_HOST", "0.0.0.0"),
    "port": int(os.getenv("API_PORT", "8000")),
    "workers": int(os.getenv("API_WORKERS", "4")),
    "timeout": 120,
    "cors_origins": os.getenv("CORS_ORIGINS", "*").split(","),
    "rate_limit": {
        "enabled": True,
        "requests_per_minute": 60
    },
    "auth": {
        "enabled": True,
        "jwt_secret": os.getenv("JWT_SECRET"),
        "token_expiry": 86400  # 24 hours
    }
}

# Performance Monitoring
MONITORING_CONFIG = {
    "enabled": True,
    "metrics": ["cpu", "memory", "response_time", "error_rate"],
    "alert_thresholds": {
        "cpu": 80,  # percent
        "memory": 80,  # percent
        "response_time": 5,  # seconds
        "error_rate": 5  # percent
    }
}

# RAG Configuration
RAG_CONFIG = {
    "vector_db_path": os.getenv("VECTOR_DB_PATH", "vector_db"),
    "embedding_model": os.getenv("EMBEDDING_MODEL", "openai"),
    "huggingface_embedding_model": os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2"),
    "chunk_size": int(os.getenv("CHUNK_SIZE", "1000")),
    "chunk_overlap": int(os.getenv("CHUNK_OVERLAP", "200")),
    "retrieval_k": int(os.getenv("RETRIEVAL_K", "5")),
    "use_contextual_compression": os.getenv("USE_CONTEXTUAL_COMPRESSION", "True").lower() == "true",
    "use_web_retrieval": os.getenv("USE_WEB_RETRIEVAL", "True").lower() == "true",
    "claim_verification": {
        "enabled": os.getenv("CLAIM_VERIFICATION_ENABLED", "True").lower() == "true",
        "confidence_threshold": float(os.getenv("CLAIM_CONFIDENCE_THRESHOLD", "0.7")),
        "max_claims_per_verification": int(os.getenv("MAX_CLAIMS_PER_VERIFICATION", "10"))
    }
}

# Feature Flags
FEATURE_FLAGS = {
    "use_mock_graph_on_failure": False,  # Changed to False to ensure Neo4j is required
    "use_mock_rag_on_failure": False,    # Disable mock RAG fallback
    "enable_advanced_validation": True,
    "enable_performance_monitoring": True,
    "enable_audit_logging": True,
    "enable_api_rate_limiting": True,
    "enable_rag": True,
    "enable_claim_verification": True
}
