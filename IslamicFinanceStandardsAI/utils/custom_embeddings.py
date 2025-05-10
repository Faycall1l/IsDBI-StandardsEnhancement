"""
Custom embeddings implementation to work with OpenAI API v1.3.0
"""

import logging
import os
import numpy as np
from typing import List, Optional
import openai
from langchain.embeddings.base import Embeddings

# Configure logging
logger = logging.getLogger(__name__)

class CustomOpenAIEmbeddings(Embeddings):
    """
    Custom implementation of OpenAI embeddings to work with OpenAI API v1.3.0
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        model: str = "text-embedding-ada-002",
        chunk_size: int = 1000,
        max_retries: int = 3,
    ):
        """Initialize the embeddings class"""
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        self.model = model
        self.chunk_size = chunk_size
        self.max_retries = max_retries
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.openai_api_key)
        logger.info(f"Initialized CustomOpenAIEmbeddings with model {self.model}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents using the OpenAI API
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings, one for each text
        """
        if not texts:
            return []
        
        # Process in chunks to avoid API limits
        embeddings = []
        for i in range(0, len(texts), self.chunk_size):
            chunk = texts[i:i + self.chunk_size]
            chunk_embeddings = self._embed_chunk(chunk)
            embeddings.extend(chunk_embeddings)
        
        return embeddings
    
    def _embed_chunk(self, texts: List[str]) -> List[List[float]]:
        """Embed a chunk of texts"""
        for attempt in range(self.max_retries):
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=texts
                )
                return [item.embedding for item in response.data]
            except Exception as e:
                logger.warning(f"Error in embedding attempt {attempt+1}/{self.max_retries}: {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to embed texts after {self.max_retries} attempts")
                    raise
        
        # This should never be reached due to the raise in the loop
        return []
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query text using the OpenAI API
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding for the text
        """
        embeddings = self.embed_documents([text])
        return embeddings[0] if embeddings else []
