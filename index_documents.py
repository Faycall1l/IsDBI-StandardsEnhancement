#!/usr/bin/env python
"""
Document Indexing Script for Islamic Finance Standards Enhancement System

This script indexes all documents in the data folder into the RAG vector store
to enable accurate information retrieval for the multi-agent system.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import RAG engine
from IslamicFinanceStandardsAI.utils.rag_engine import get_rag_engine
from IslamicFinanceStandardsAI.config.production import RAG_CONFIG, FEATURE_FLAGS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def index_documents(data_dir, extensions=None):
    """
    Index all documents in the specified directory into the RAG vector store.
    
    Args:
        data_dir: Directory containing documents to index
        extensions: List of file extensions to include (default: txt, pdf, docx)
    """
    if extensions is None:
        extensions = ["txt", "pdf", "docx"]
    
    # Get RAG engine
    rag_engine = get_rag_engine()
    if rag_engine is None:
        logger.error("Failed to initialize RAG engine. Exiting.")
        return False
    
    # Find all documents with specified extensions
    indexed_count = 0
    failed_count = 0
    
    for ext in extensions:
        files = list(Path(data_dir).glob(f"**/*.{ext}"))
        logger.info(f"Found {len(files)} .{ext} files in {data_dir}")
        
        for file_path in files:
            try:
                logger.info(f"Indexing {file_path}")
                chunks_added = rag_engine.add_document(str(file_path))
                logger.info(f"Successfully indexed {file_path} ({chunks_added} chunks added)")
                indexed_count += 1
            except Exception as e:
                logger.error(f"Failed to index {file_path}: {str(e)}")
                failed_count += 1
    
    logger.info(f"Indexing complete. {indexed_count} documents indexed, {failed_count} failed.")
    return indexed_count > 0

def main():
    parser = argparse.ArgumentParser(description="Index documents for RAG system")
    parser.add_argument("--data-dir", default="data", help="Directory containing documents to index")
    parser.add_argument("--extensions", default="txt,pdf,docx", help="Comma-separated list of file extensions to index")
    args = parser.parse_args()
    
    # Check if data directory exists
    if not os.path.isdir(args.data_dir):
        logger.error(f"Data directory {args.data_dir} does not exist")
        return 1
    
    # Parse extensions
    extensions = [ext.strip() for ext in args.extensions.split(",")]
    
    # Index documents
    success = index_documents(args.data_dir, extensions)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
