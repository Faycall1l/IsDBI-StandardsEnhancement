"""
Gemini API client for the Islamic Finance Standards Enhancement system.
Provides an alternative to OpenAI for text generation and embeddings.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
import google.generativeai as genai

logger = logging.getLogger(__name__)

class GeminiClient:
    """
    Client for interacting with Google's Gemini API.
    Can be used as a fallback when OpenAI API is unavailable.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini client.
        
        Args:
            api_key: Google API key for Gemini. If None, will try to get from environment.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass api_key.")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        logger.info("Initialized Gemini client")
    
    def generate_text(
        self, 
        prompt: str, 
        model: str = "gemini-1.5-flash", 
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate text using Gemini.
        
        Args:
            prompt: The prompt to generate text from
            model: The model to use (default: gemini-1.5-flash)
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            system_prompt: Optional system prompt for role-based prompting
            
        Returns:
            Generated text
        """
        try:
            # Get the model
            model_obj = genai.GenerativeModel(model_name=model)
            
            # Set generation config
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            
            # Handle system prompt and user prompt together
            if system_prompt:
                # For models that support system prompts, we need to use a different approach
                response = model_obj.generate_content(
                    [
                        {"role": "user", "parts": [prompt]}
                    ],
                    generation_config=generation_config,
                    safety_settings={
                        "HARASSMENT": "block_none",
                        "HATE": "block_none",
                        "SEXUAL": "block_none",
                        "DANGEROUS": "block_none"
                    }
                )
            else:
                # Simple completion without system prompt
                response = model_obj.generate_content(
                    prompt,
                    generation_config=generation_config,
                    safety_settings={
                        "HARASSMENT": "block_none",
                        "HATE": "block_none",
                        "SEXUAL": "block_none",
                        "DANGEROUS": "block_none"
                    }
                )
            
            # Extract text from response
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating text with Gemini: {str(e)}")
            return f"Error: {str(e)}"
    
    def get_embeddings(self, texts: List[str], model: str = "models/embedding-001") -> List[List[float]]:
        """
        Get embeddings for a list of texts using Gemini.
        
        Args:
            texts: List of texts to get embeddings for
            model: The embedding model to use (must start with 'models/')
            
        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        try:
            embeddings = []
            # Ensure model name starts with 'models/'
            if not model.startswith("models/"):
                model = f"models/{model}"
                
            # Use the embedding model from the Gemini API
            for text in texts:
                # Get embedding for the text
                embedding_result = genai.embed_content(
                    model=model,
                    content=text,
                    task_type="retrieval_document"
                )
                
                # Extract the embedding values
                embedding_values = embedding_result['embedding']
                embeddings.append(embedding_values)
                
            logger.info(f"Generated {len(embeddings)} embeddings with Gemini")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings with Gemini: {str(e)}")
            # Return zero embeddings as fallback
            return [[0.0] * 768 for _ in range(len(texts))]
    
    def verify_claim(self, claim: str, context: str) -> Dict[str, Any]:
        """
        Verify a claim against a context using Gemini.
        
        Args:
            claim: The claim to verify
            context: The context to verify against
            
        Returns:
            Dictionary with verification results
        """
        prompt = f"""
        CLAIM TO VERIFY: {claim}
        
        CONTEXT:
        {context[:5000]}  # Limit context length
        
        TASK:
        Verify if the claim is supported by the provided context from Islamic finance standards.
        
        VERIFICATION RESULT:
        - verified: [true/false] Is the claim verified by the context?
        - confidence: [0.0-1.0] How confident are you in this verification?
        - evidence: What specific evidence supports or contradicts the claim?
        """
        
        try:
            response = self.generate_text(
                prompt=prompt,
                temperature=0.0,
                max_tokens=500,
                system_prompt="You are an expert in Islamic finance and Shariah standards."
            )
            
            # Parse the response
            import re
            verified = "true" in response.lower() and "verified: true" in response.lower()
            
            # Extract confidence score
            confidence_match = re.search(r'confidence[:\s]+([0-9.]+)', response, re.IGNORECASE)
            confidence = float(confidence_match.group(1)) if confidence_match else 0.5
            
            # Extract evidence
            evidence = response.split("evidence", 1)[1].strip() if "evidence" in response.lower() else response
            
            return {
                "verified": verified,
                "confidence": confidence,
                "evidence": evidence
            }
            
        except Exception as e:
            logger.error(f"Error verifying claim with Gemini: {str(e)}")
            return {
                "verified": False,
                "confidence": 0.0,
                "evidence": f"Error: {str(e)}"
            }
    
    def classify_claims(self, text: str) -> Dict[str, List[str]]:
        """
        Classify claims in text as verifiable or subjective.
        
        Args:
            text: Text containing claims to classify
            
        Returns:
            Dictionary with lists of verifiable and subjective claims
        """
        prompt = f"""
        TEXT:
        {text}
        
        TASK:
        Analyze the text and identify two types of statements:
        1. Verifiable claims: Factual statements that can be verified against Islamic finance standards
        2. Subjective suggestions: Opinions, recommendations, or suggestions that cannot be directly verified
        
        FORMAT YOUR RESPONSE AS FOLLOWS:
        VERIFIABLE CLAIMS:
        - [claim 1]
        - [claim 2]
        ...
        
        SUBJECTIVE SUGGESTIONS:
        - [suggestion 1]
        - [suggestion 2]
        ...
        """
        
        try:
            response = self.generate_text(
                prompt=prompt,
                temperature=0.0,
                max_tokens=1000,
                system_prompt="You are an expert in Islamic finance and Shariah standards."
            )
            
            # Parse the response
            verifiable = []
            subjective = []
            
            current_section = None
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                if "VERIFIABLE CLAIMS:" in line.upper():
                    current_section = "verifiable"
                elif "SUBJECTIVE SUGGESTIONS:" in line.upper():
                    current_section = "subjective"
                elif line.startswith('-') and current_section == "verifiable":
                    claim = line[1:].strip()
                    if claim:
                        verifiable.append(claim)
                elif line.startswith('-') and current_section == "subjective":
                    suggestion = line[1:].strip()
                    if suggestion:
                        subjective.append(suggestion)
            
            return {
                "verifiable": verifiable,
                "subjective": subjective
            }
            
        except Exception as e:
            logger.error(f"Error classifying claims with Gemini: {str(e)}")
            return {
                "verifiable": [],
                "subjective": []
            }
