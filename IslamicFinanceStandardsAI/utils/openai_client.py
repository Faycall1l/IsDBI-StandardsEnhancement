"""
OpenAI Client

This module provides a wrapper for the OpenAI API to generate text and embeddings.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI

class OpenAIClient:
    """Client for interacting with OpenAI API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI client
        
        Args:
            api_key: OpenAI API key (optional, will use environment variable if not provided)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided and OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialized OpenAI client")
    
    def generate_text(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000, 
                     system_prompt: str = "You are a helpful assistant.") -> str:
        """
        Generate text using OpenAI's GPT model
        
        Args:
            prompt: The user prompt
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            system_prompt: System prompt to set the assistant's behavior
            
        Returns:
            Generated text
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",  # Using GPT-4 for high-quality responses
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract the generated text from the response
            generated_text = response.choices[0].message.content
            return generated_text
            
        except Exception as e:
            self.logger.error(f"Error generating text with OpenAI: {str(e)}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to generate embeddings for
            
        Returns:
            List of embedding vectors
        """
        try:
            # Use the text-embedding-ada-002 model for embeddings
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=texts
            )
            
            # Extract embeddings from the response
            embeddings = [item.embedding for item in response.data]
            return embeddings
            
        except Exception as e:
            self.logger.error(f"Error generating embeddings with OpenAI: {str(e)}")
            raise
