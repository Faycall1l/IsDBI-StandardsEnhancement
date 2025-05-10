"""
Mock Retrieval-Augmented Generation (RAG) Engine

This module provides a mock implementation of the RAG engine for testing purposes.
"""

import os
import logging
from typing import List, Dict, Any
import random

from langchain.docstore.document import Document

# Configure logging
logger = logging.getLogger(__name__)

class MockRAGEngine:
    """
    Mock implementation of the RAG engine for testing purposes.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MockRAGEngine, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the mock RAG engine"""
        logger.info("Initializing mock RAG engine")
        
        # Create a simple in-memory document store
        self.documents = [
            Document(
                page_content="Musharaka is a form of partnership where two or more persons combine either their capital or labour together, to share the profits, enjoying similar rights and liabilities.",
                metadata={"source": "mock", "standard": "FAS 4", "topic": "Musharaka"}
            ),
            Document(
                page_content="Mudaraba is a partnership in profit whereby one party provides capital (Rab al-Mal) and the other party provides labour (Mudarib).",
                metadata={"source": "mock", "standard": "FAS 3", "topic": "Mudaraba"}
            ),
            Document(
                page_content="Ijarah is a lease contract under which a bank or financier buys and leases out an asset or equipment required by its client for a rental fee.",
                metadata={"source": "mock", "standard": "FAS 8", "topic": "Ijarah"}
            ),
            Document(
                page_content="Sukuk are certificates of equal value representing undivided shares in the ownership of tangible assets, usufructs and services or (in the ownership of) the assets of particular projects or special investment activity.",
                metadata={"source": "mock", "standard": "FAS 17", "topic": "Sukuk"}
            ),
            Document(
                page_content="Takaful is a system of Islamic insurance based on the principle of mutual cooperation where participants contribute to a pool of funds to guarantee each other against loss or damage.",
                metadata={"source": "mock", "standard": "FAS 19", "topic": "Takaful"}
            ),
        ]
        
        logger.info(f"Mock RAG engine initialized with {len(self.documents)} documents")
    
    def add_document(self, file_path: str) -> int:
        """
        Mock implementation of adding a document to the vector store
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Number of chunks added to the vector store
        """
        logger.info(f"Mock: Adding document {file_path}")
        # Simulate adding 3-5 chunks
        num_chunks = random.randint(3, 5)
        
        for i in range(num_chunks):
            self.documents.append(
                Document(
                    page_content=f"Mock content for {os.path.basename(file_path)} - chunk {i+1}",
                    metadata={"source": file_path, "chunk": i+1}
                )
            )
        
        logger.info(f"Mock: Added {num_chunks} chunks from {file_path}")
        return num_chunks
    
    def add_text(self, text: str, metadata: Dict[str, Any]) -> int:
        """
        Mock implementation of adding text directly to the vector store
        
        Args:
            text: Text content to add
            metadata: Metadata for the text
            
        Returns:
            Number of chunks added to the vector store
        """
        logger.info("Mock: Adding text content")
        # Simulate adding 1-3 chunks
        num_chunks = random.randint(1, 3)
        
        for i in range(num_chunks):
            chunk_text = text[:min(100, len(text))] + "..." if len(text) > 100 else text
            self.documents.append(
                Document(
                    page_content=f"Mock chunk {i+1}: {chunk_text}",
                    metadata=metadata
                )
            )
        
        logger.info(f"Mock: Added {num_chunks} chunks from text")
        return num_chunks
    
    def retrieve(self, query: str, k: int = 5, use_compression: bool = True) -> List[Document]:
        """
        Mock implementation of retrieving relevant documents for a query
        
        Args:
            query: Query string
            k: Number of documents to retrieve
            use_compression: Whether to use contextual compression
            
        Returns:
            List of retrieved documents
        """
        logger.info(f"Mock: Retrieving documents for query: {query}")
        
        # Simulate relevance by simple keyword matching
        relevant_docs = []
        for doc in self.documents:
            # Simple relevance scoring based on word overlap
            query_words = set(query.lower().split())
            content_words = set(doc.page_content.lower().split())
            overlap = len(query_words.intersection(content_words))
            
            if overlap > 0:
                relevant_docs.append((doc, overlap))
        
        # Sort by relevance score and take top k
        relevant_docs.sort(key=lambda x: x[1], reverse=True)
        result = [doc for doc, _ in relevant_docs[:k]]
        
        # If we don't have enough relevant docs, add some random ones
        if len(result) < k:
            remaining = k - len(result)
            random_docs = random.sample([d for d in self.documents if d not in result], min(remaining, len(self.documents) - len(result)))
            result.extend(random_docs)
        
        logger.info(f"Mock: Retrieved {len(result)} documents")
        return result
    
    def get_retrieval_context(self, query: str, k: int = 5) -> str:
        """
        Mock implementation of getting formatted context string from retrieved documents
        
        Args:
            query: Query string
            k: Number of documents to retrieve
            
        Returns:
            Formatted context string
        """
        docs = self.retrieve(query, k)
        
        context = "RELEVANT CONTEXT:\n\n"
        for i, doc in enumerate(docs):
            context += f"Document {i+1}:\n"
            context += f"Source: {doc.metadata.get('source', 'Unknown')}\n"
            context += f"Content: {doc.page_content}\n\n"
        
        logger.info(f"Mock: Generated context with {len(docs)} documents")
        return context


class MockClaimVerifier:
    """
    Mock implementation of the claim verification system for testing purposes.
    """
    
    def __init__(self):
        """Initialize the mock claim verifier"""
        self.rag_engine = MockRAGEngine()
        logger.info("Mock claim verifier initialized")
    
    def extract_claims(self, text: str) -> List[str]:
        """
        Mock implementation of extracting individual claims from text
        
        Args:
            text: Text to extract claims from
            
        Returns:
            List of individual claims
        """
        # Simple claim extraction by splitting on periods
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        # Only treat sentences with more than 5 words as claims
        claims = [s for s in sentences if len(s.split()) > 5]
        
        logger.info(f"Mock: Extracted {len(claims)} claims from text")
        return claims
    
    def verify_claim(self, claim: str) -> Dict[str, Any]:
        """
        Mock implementation of verifying a single claim against the knowledge base
        
        Args:
            claim: Claim to verify
            
        Returns:
            Verification result with confidence score and evidence
        """
        # Get relevant documents
        docs = self.rag_engine.retrieve(claim, k=3)
        sources = [doc.metadata.get('source', 'Unknown') for doc in docs]
        
        # Simple verification logic based on word overlap
        claim_words = set(claim.lower().split())
        
        # Calculate overlap with each document
        max_overlap = 0
        best_doc = None
        
        for doc in docs:
            content_words = set(doc.page_content.lower().split())
            overlap = len(claim_words.intersection(content_words)) / max(len(claim_words), 1)
            
            if overlap > max_overlap:
                max_overlap = overlap
                best_doc = doc
        
        # Determine verification result based on overlap
        if max_overlap > 0.5:
            verified = True
            confidence = min(0.5 + max_overlap, 0.95)  # Cap at 0.95
            evidence = best_doc.page_content if best_doc else "No specific evidence found"
        elif max_overlap > 0.3:
            verified = True
            confidence = 0.3 + max_overlap
            evidence = "Partial evidence found: " + (best_doc.page_content if best_doc else "No specific evidence")
        else:
            verified = False
            confidence = max(0.1, max_overlap)
            evidence = "Insufficient evidence to verify this claim"
        
        result = {
            "claim": claim,
            "verified": verified,
            "confidence": confidence,
            "evidence": evidence,
            "sources": sources
        }
        
        logger.info(f"Mock: Verified claim with confidence {confidence:.2f}")
        return result
    
    def verify_text(self, text: str) -> Dict[str, Any]:
        """
        Mock implementation of verifying all claims in a text
        
        Args:
            text: Text containing claims to verify
            
        Returns:
            Verification results for all claims
        """
        claims = self.extract_claims(text)
        
        verification_results = []
        unverified_claims = []
        
        for claim in claims:
            result = self.verify_claim(claim)
            verification_results.append(result)
            
            if not result["verified"] or result["confidence"] < 0.7:
                unverified_claims.append(claim)
        
        overall_verification = {
            "text": text,
            "claims_total": len(claims),
            "claims_verified": len(claims) - len(unverified_claims),
            "verification_rate": (len(claims) - len(unverified_claims)) / max(len(claims), 1),
            "unverified_claims": unverified_claims,
            "claim_results": verification_results
        }
        
        logger.info(f"Mock: Verified text with {len(claims)} claims, {len(unverified_claims)} unverified")
        return overall_verification
    
    def improve_response(self, original_text: str, verification_results: Dict[str, Any]) -> str:
        """
        Mock implementation of improving a response by correcting unverified claims
        
        Args:
            original_text: Original response text
            verification_results: Results from verify_text
            
        Returns:
            Improved response with corrected claims
        """
        if verification_results["verification_rate"] > 0.9:
            # Response is already good
            return original_text
        
        # Simple improvement by adding qualifiers to unverified claims
        improved_text = original_text
        for claim in verification_results["unverified_claims"]:
            if claim in improved_text:
                improved_text = improved_text.replace(
                    claim, 
                    f"{claim} (this statement may require further verification)"
                )
        
        logger.info("Mock: Generated improved response with corrected claims")
        return improved_text


# Create singleton instances
mock_rag_engine = MockRAGEngine()
mock_claim_verifier = MockClaimVerifier()

def get_mock_rag_engine() -> MockRAGEngine:
    """Get the singleton mock RAG engine instance"""
    return mock_rag_engine

def get_mock_claim_verifier() -> MockClaimVerifier:
    """Get the singleton mock claim verifier instance"""
    return mock_claim_verifier
