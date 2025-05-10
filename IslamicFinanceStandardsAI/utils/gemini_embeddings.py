"""
Gemini Embeddings for Islamic Finance Standards Enhancement System

This module provides a custom embeddings implementation using Google's Gemini API
as an alternative to OpenAI embeddings.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
import numpy as np
from langchain.embeddings.base import Embeddings

from .gemini_client import GeminiClient

logger = logging.getLogger(__name__)

class GeminiEmbeddings(Embeddings):
    """
    Custom embeddings implementation using Gemini API.
    Implements the LangChain Embeddings interface for compatibility with vector stores.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "models/embedding-001"):
        """
        Initialize the Gemini embeddings.
        
        Args:
            api_key: Gemini API key. If None, will try to get from environment.
            model: The embedding model to use (must start with 'models/')
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass api_key.")
        
        # Ensure model name starts with 'models/'
        if not model.startswith("models/"):
            self.model = f"models/{model}"
        else:
            self.model = model
            
        self.client = GeminiClient(api_key=self.api_key)
        logger.info(f"Initialized GeminiEmbeddings with model {self.model}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents.
        
        Args:
            texts: List of document texts to embed
            
        Returns:
            List of embeddings, one for each document
        """
        try:
            # Use the GeminiClient to get embeddings
            embeddings = self.client.get_embeddings(texts, model=self.model)
            return embeddings
        except Exception as e:
            logger.error(f"Error generating document embeddings with Gemini: {str(e)}")
            # Return zero embeddings as fallback
            return [[0.0] * 768 for _ in range(len(texts))]
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate an embedding for a query.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding for the query
        """
        try:
            # Use the GeminiClient to get a single embedding
            embeddings = self.client.get_embeddings([text], model=self.model)
            return embeddings[0]
        except Exception as e:
            logger.error(f"Error generating query embedding with Gemini: {str(e)}")
            # Return zero embedding as fallback
            return [0.0] * 768
