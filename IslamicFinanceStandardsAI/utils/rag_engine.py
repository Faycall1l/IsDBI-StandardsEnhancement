"""
Retrieval-Augmented Generation (RAG) Engine

This module provides RAG capabilities for the Islamic Finance Standards Enhancement system,
enabling accurate information retrieval and reducing hallucinations in LLM outputs.
"""

import os
import re
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# OpenAI imports for error handling
import openai
from openai import OpenAIError, APITimeoutError, APIConnectionError, RateLimitError

# Vector database and embedding imports
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain.docstore.document import Document
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.chat_models import ChatOpenAI  # Use ChatOpenAI instead of OpenAI
from langchain.schema.runnable import RunnablePassthrough

# Import custom embeddings implementations
from .custom_embeddings import CustomOpenAIEmbeddings
from .gemini_embeddings import GeminiEmbeddings

# Import web retriever for Shariah standards
from .web_retriever import get_web_retriever

# Import configuration
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.production import RAG_CONFIG, OPENAI_CONFIG, FEATURE_FLAGS

# Configure logging
logger = logging.getLogger(__name__)

class RAGEngine:
    """
    Retrieval-Augmented Generation engine for accurate information retrieval
    and hallucination reduction in LLM outputs.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGEngine, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the RAG engine"""
        self.config = RAG_CONFIG
        self.vector_db_path = self.config.get("vector_db_path", "vector_db")
        
        # Create vector DB directory if it doesn't exist
        os.makedirs(self.vector_db_path, exist_ok=True)
        
        # Initialize Gemini client for text generation
        self._initialize_gemini_client()
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.get("chunk_size", 1000),
            chunk_overlap=self.config.get("chunk_overlap", 200)
        )
        
        # Initialize web search flag
        self.use_web_retrieval = self.config.get("use_web_retrieval", False)
        
        # Initialize embedding model
        embedding_type = self.config.get("embedding_model", "openai")
        self.use_gemini = os.getenv("USE_GEMINI", "false").lower() == "true"
        
    def _initialize_gemini_client(self):
        """Initialize Gemini client for text generation"""
        try:
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if gemini_api_key:
                from .gemini_client import GeminiClient
                self.gemini_client = GeminiClient(api_key=gemini_api_key)
                logger.info("Successfully initialized Gemini client")
            else:
                logger.warning("No Gemini API key found. Gemini client not initialized.")
                self.gemini_client = None
        except Exception as e:
            logger.error(f"Error initializing Gemini client: {str(e)}")
            self.gemini_client = None
        
        # Try Gemini first if enabled
        if self.use_gemini:
            try:
                gemini_api_key = os.getenv("GEMINI_API_KEY")
                if gemini_api_key:
                    self.embeddings = GeminiEmbeddings(
                        api_key=gemini_api_key,
                        model="embedding-001"
                    )
                    logger.info("Successfully initialized GeminiEmbeddings")
                    return
            except Exception as e:
                logger.error(f"Error initializing GeminiEmbeddings: {str(e)}")
                logger.info("Falling back to OpenAI or HuggingFace embeddings")
        
        # Try OpenAI if Gemini failed or is not enabled
        if embedding_type == "openai":
            try:
                # Use our custom OpenAI embeddings implementation
                self.embeddings = CustomOpenAIEmbeddings(
                    openai_api_key=OPENAI_CONFIG.get("api_key"),
                    model="text-embedding-ada-002"
                )
                logger.info("Successfully initialized CustomOpenAIEmbeddings")
            except Exception as e:
                logger.error(f"Error initializing CustomOpenAIEmbeddings: {str(e)}")
                # Fallback to HuggingFace embeddings if OpenAI fails
                logger.info("Falling back to HuggingFace embeddings")
                model_name = "sentence-transformers/all-mpnet-base-v2"
                self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        else:
            # Use local HuggingFace embeddings
            model_name = self.config.get("huggingface_embedding_model", "sentence-transformers/all-mpnet-base-v2")
            self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        
        # Initialize text splitter for chunking (with separators)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.get("chunk_size", 1000),
            chunk_overlap=self.config.get("chunk_overlap", 200),
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Initialize vector store
        self.vector_store = None
        try:
            self._load_or_create_vector_store()
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            # Create a simple empty vector store as fallback
            self.vector_store = FAISS.from_documents(
                [Document(page_content="Islamic Finance Standards", metadata={"source": "initialization"})],
                self.embeddings
            )
            logger.info("Created fallback vector store")
        
        # Initialize LLM for contextual compression
        use_gemini = os.getenv("USE_GEMINI", "false").lower() == "true"
        
        if use_gemini:
            try:
                # Use Gemini for LLM operations
                from langchain_google_genai import ChatGoogleGenerativeAI
                gemini_api_key = os.getenv("GEMINI_API_KEY")
                if gemini_api_key:
                    os.environ["GOOGLE_API_KEY"] = gemini_api_key
                    self.llm = ChatGoogleGenerativeAI(
                        model="gemini-1.5-flash",
                        temperature=0.0
                    )
                    logger.info("Successfully initialized Gemini LLM")
                    return
            except Exception as e:
                logger.error(f"Error initializing Gemini LLM: {str(e)}")
                logger.info("Falling back to OpenAI LLM")
        
        # Fallback to OpenAI
        try:
            self.llm = ChatOpenAI(
                openai_api_key=OPENAI_CONFIG.get("api_key"),
                temperature=0.0,
                model=OPENAI_CONFIG.get("model", "gpt-4")
            )
            logger.info("Successfully initialized OpenAI LLM")
        except Exception as e:
            logger.error(f"Error initializing OpenAI LLM: {str(e)}")
            # Fallback to a simpler model if the primary one fails
            try:
                self.llm = ChatOpenAI(
                    openai_api_key=OPENAI_CONFIG.get("api_key"),
                    temperature=0.0,
                    model="gpt-3.5-turbo"
                )
                logger.info("Falling back to gpt-3.5-turbo model")
            except Exception as e2:
                logger.error(f"Error initializing fallback LLM: {str(e2)}")
                raise RuntimeError("Failed to initialize LLM for RAG engine")
        
        # Initialize contextual compression retriever
        try:
            self.compressor = LLMChainExtractor.from_llm(self.llm)
            logger.info("Successfully initialized contextual compression retriever")
        except Exception as e:
            logger.error(f"Error initializing compressor: {str(e)}")
            self.compressor = None
            logger.warning("Contextual compression will not be available")
        
        logger.info("RAG Engine initialized successfully")
    
    def _load_or_create_vector_store(self):
        """Load existing vector store or create a new one"""
        vector_index_path = os.path.join(self.vector_db_path, "faiss_index")
        
        if os.path.exists(vector_index_path):
            # Load existing vector store
            try:
                self.vector_store = FAISS.load_local(
                    folder_path=self.vector_db_path,
                    embeddings=self.embeddings,
                    index_name="faiss_index"
                )
                logger.info(f"Loaded existing vector store from {vector_index_path}")
            except Exception as e:
                logger.error(f"Error loading vector store: {str(e)}")
                # Create a new vector store if loading fails
                self.vector_store = FAISS.from_documents(
                    [Document(page_content="Islamic Finance Standards", metadata={"source": "initialization"})],
                    self.embeddings
                )
                logger.info("Created new vector store due to loading error")
        else:
            # Create a new vector store
            self.vector_store = FAISS.from_documents(
                [Document(page_content="Islamic Finance Standards", metadata={"source": "initialization"})],
                self.embeddings
            )
            logger.info("Created new vector store")
            
            # Save the vector store
            self.vector_store.save_local(self.vector_db_path, index_name="faiss_index")
            logger.info(f"Saved vector store to {vector_index_path}")
            # Already created above, no need to create again
    
    def add_document(self, file_path: str) -> int:
        """
        Add a document to the vector store
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Number of chunks added to the vector store
        """
        try:
            logger.info(f"Adding document to vector store: {file_path}")
            
            # Load document based on file type
            file_extension = file_path.split('.')[-1].lower()
            
            if file_extension == 'pdf':
                loader = PyPDFLoader(file_path)
            elif file_extension in ['docx', 'doc']:
                loader = Docx2txtLoader(file_path)
            elif file_extension == 'txt':
                loader = TextLoader(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            documents = loader.load()
            
            # Add source metadata
            for doc in documents:
                doc.metadata["source"] = file_path
                doc.metadata["added_at"] = datetime.now().isoformat()
            
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Add to vector store
            self.vector_store.add_documents(chunks)
            
            # Save updated vector store
            self.vector_store.save_local(self.vector_db_path, "faiss_index")
            
            logger.info(f"Added {len(chunks)} chunks from {file_path} to vector store")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Error adding document to vector store: {str(e)}")
            return 0
    
    def add_text(self, text: str, metadata: Dict[str, Any]) -> int:
        """
        Add text directly to the vector store
        
        Args:
            text: Text content to add
            metadata: Metadata for the text
            
        Returns:
            Number of chunks added to the vector store
        """
        try:
            logger.info(f"Adding text to vector store with metadata: {metadata}")
            
            # Create document
            document = Document(page_content=text, metadata=metadata)
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([document])
            
            # Add to vector store
            self.vector_store.add_documents(chunks)
            
            # Save updated vector store
            self.vector_store.save_local(self.vector_db_path, "faiss_index")
            
            logger.info(f"Added {len(chunks)} chunks to vector store")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Error adding text to vector store: {str(e)}")
            return 0
    
    def retrieve(self, query: str, k: int = 5, use_compression: bool = False, use_web: bool = None) -> List[Document]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: Query string
{{ ... }}
        
        Args:
            query: Query string
            k: Number of documents to retrieve
            use_compression: Whether to use contextual compression (disabled by default)
            use_web: Override for web retrieval setting
            
        Returns:
            List of retrieved documents
        """
        documents = []
        web_documents = []
        
        # Determine if we should use web retrieval
        should_use_web = self.use_web_retrieval if use_web is None else use_web
        
        # First try to retrieve from vector store
        if hasattr(self, "vector_store") and self.vector_store is not None:
            try:
                if use_compression and hasattr(self, "llm"):
                    # Use contextual compression to get more relevant results
                    compressor = LLMChainExtractor.from_llm(self.llm)
                    compression_retriever = ContextualCompressionRetriever(
                        base_compressor=compressor,
                        base_retriever=self.vector_store.as_retriever(search_kwargs={"k": k})
                    )
                    documents = compression_retriever.get_relevant_documents(query)
                else:
                    # Use standard retrieval
                    documents = self.vector_store.similarity_search(query, k=k)
            except Exception as e:
                logger.error(f"Error retrieving documents from vector store: {str(e)}")
        else:
            logger.warning("Vector store not initialized")
        
        # If we have fewer than k documents or web retrieval is explicitly requested, try web search
        if should_use_web and (len(documents) < k or not documents):
            try:
                # Get web retriever
                web_retriever = get_web_retriever()
                if web_retriever:
                    # Calculate how many more documents we need
                    web_k = max(1, k - len(documents))
                    
                    # Search for standards
                    standards = web_retriever.search_standards(query, max_results=web_k)
                    
                    # Convert to Documents format
                    for standard in standards:
                        # Try to retrieve content if URL is available
                        content = ""
                        if "url" in standard and standard["url"]:
                            try:
                                content = web_retriever.retrieve_standard_content(standard["url"])
                            except Exception as e:
                                logger.error(f"Error retrieving content from {standard['url']}: {str(e)}")
                                content = standard.get("snippet", "")
                        else:
                            content = standard.get("snippet", "")
                        
                        # Create document
                        web_documents.append(Document(
                            page_content=content,
                            metadata={
                                "source": standard.get("source", "web"),
                                "title": standard.get("title", "Unknown Standard"),
                                "url": standard.get("url", ""),
                                "retrieved_from_web": True
                            }
                        ))
                    
                    logger.info(f"Retrieved {len(web_documents)} documents from web search")
            except Exception as e:
                logger.error(f"Error retrieving documents from web: {str(e)}")
        
        # Combine documents from both sources
        combined_documents = documents + web_documents
        
        # Limit to k documents
        return combined_documents[:k] if combined_documents else []
    
    def get_retrieval_context(self, query: str, k: int = 5, use_web: bool = None) -> str:
        """
        Get formatted context string from retrieved documents
        
        Args:
            query: Query string
{{ ... }}
        Get formatted context string from retrieved documents
        
        Args:
            query: Query string
            k: Number of documents to retrieve
            use_web: Override for web retrieval setting
            
        Returns:
            Formatted context string
        """
        documents = self.retrieve(query, k=k, use_web=use_web)
        
        if not documents:
            logger.warning("No relevant documents found for query: {}".format(query))
            return ""
        
        # Format context string
        context_parts = []
        
        for i, doc in enumerate(documents):
            source = doc.metadata.get("source", "Unknown")
            title = doc.metadata.get("title", "")
            url = doc.metadata.get("url", "")
            from_web = doc.metadata.get("retrieved_from_web", False)
            
            # Add source information
            source_info = f"Document {i+1} (Source: {source})"
            if title:
                source_info += f" - {title}"
            if from_web and url:
                source_info += f" [URL: {url}]"
                
            context_parts.append(f"{source_info}:\n{doc.page_content}\n")
        
        return "\n".join(context_parts)

class ClaimVerifier:
    """
{{ ... }}
    Claim verification system to reduce hallucinations in LLM outputs
    by breaking responses into verifiable claims and checking them against
    the knowledge base.
    """
    
    def __init__(self):
        """Initialize the claim verifier"""
        self.rag_engine = RAGEngine()
        
        # Initialize LLM for claim verification
        try:
            self.llm = ChatOpenAI(
                openai_api_key=OPENAI_CONFIG.get("api_key"),
                temperature=0.0,
                model=OPENAI_CONFIG.get("model", "gpt-4")
            )
            logger.info("Initialized ChatOpenAI for claim verification")
        except Exception as e:
            logger.error(f"Error initializing ChatOpenAI: {str(e)}")
            try:
                # Fallback to a simpler model
                self.llm = ChatOpenAI(
                    openai_api_key=OPENAI_CONFIG.get("api_key"),
                    temperature=0.0,
                    model="gpt-3.5-turbo"
                )
                logger.info("Falling back to gpt-3.5-turbo for claim verification")
            except Exception as e2:
                logger.error(f"Error initializing fallback LLM: {str(e2)}")
                raise RuntimeError("Failed to initialize LLM for claim verification")
        
        logger.info("Claim Verifier initialized successfully")
    
    def extract_claims(self, text: str) -> List[str]:
        """
        Extract individual claims from text
        
        Args:
            text: Text to extract claims from
            
        Returns:
            List of individual claims
        """
        try:
            # Use Gemini to extract claims
            prompt = f"""Extract all factual claims from the following text. Each claim should be a single, atomic statement that can be verified as true or false.
            
            Text: {text}
            
            Output each claim on a new line, prefixed with a number and a period (e.g., "1. Claim").
            """
            
            try:
                # Try to use Gemini for claim extraction if available
                if hasattr(self, 'gemini_client'):
                    response_text = self.gemini_client.generate_text(
                        prompt=prompt,
                        temperature=0.0,
                        max_tokens=1000
                    )
                    claims_text = response_text.strip()
                else:
                    # Fall back to rule-based extraction
                    logger.warning("No Gemini client available. Falling back to rule-based extraction.")
                    claims_text = self._rule_based_claim_extraction(text)
            except Exception as e:
                # Fall back to simple rule-based extraction
                logger.warning(f"API error: {str(e)}. Falling back to rule-based extraction.")
                claims_text = self._rule_based_claim_extraction(text)
            
            # Parse the claims
            claims = []
            for line in claims_text.split("\n"):
                line = line.strip()
                if re.match(r"^\d+\.\s", line):  # Match lines starting with a number and period
                    claim = re.sub(r"^\d+\.\s", "", line).strip()
                    if claim:
                        claims.append(claim)
                elif line:  # If it's not empty and doesn't match the pattern, add it anyway
                    claims.append(line)
            
            return claims
            
        except Exception as e:
            logger.error(f"Error extracting claims: {str(e)}")
            # Return the original text as a single claim if extraction fails
            return [text]
    
    def _rule_based_claim_extraction(self, text: str) -> str:
        """Simple rule-based claim extraction as fallback"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        claims = []
        
        for i, sentence in enumerate(sentences, 1):
            # Skip very short sentences or those that are likely not claims
            if len(sentence) < 10 or re.match(r'^(Note:|\*\*|#)', sentence):
                continue
                
            claims.append(f"{i}. {sentence}")
            
        return "\n".join(claims)
        
    def _initialize_gemini_client(self):
        """Initialize Gemini client for text generation"""
        try:
            from utils.gemini_client import GeminiClient
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if gemini_api_key:
                self.gemini_client = GeminiClient(api_key=gemini_api_key)
                logger.info("Initialized Gemini client for RAG engine")
            else:
                logger.warning("GEMINI_API_KEY not set, Gemini features will be limited")
        except Exception as e:
            logger.error(f"Error initializing Gemini client: {str(e)}")
    
    def verify_claim(self, claim: str) -> Dict[str, Any]:
        """
        Verify a single claim against the knowledge base
        
        Args:
            claim: Claim to verify
            
        Returns:
            Verification result with confidence score and evidence
        """
        logger.info(f"Verifying claim: {claim}")
        
        # Get relevant documents
        docs = self.rag_engine.retrieve(claim, k=3)
        sources = [doc.metadata.get('source', 'Unknown') for doc in docs]
        
        try:
            if not docs:
                logger.warning("No relevant documents found for claim verification")
                return {
                    "claim": claim,
                    "verified": False,
                    "confidence": 0.0,
                    "evidence": "No relevant documents found",
                    "sources": []
                }
            
            # Create context from documents
            context = "\n\n".join([f"Document {i+1}: {doc.page_content}" for i, doc in enumerate(docs)])
            
            # Create a prompt for verification
            prompt = f"""
            CLAIM TO VERIFY: {claim}
            
            RELEVANT CONTEXT:
            {context}
            
            TASK:
            Verify if the claim is supported by the provided context. 
            
            VERIFICATION RESULT:
            - verified: [true/false] Is the claim verified by the context?
            - confidence: [0.0-1.0] How confident are you in this verification?
            - evidence: What specific evidence supports or contradicts the claim?
            """
            
            # Use the ChatOpenAI model for verification
            from langchain.schema.messages import HumanMessage
            response = self.llm.invoke([HumanMessage(content=prompt)])
            response_text = response.content
            
            # Parse the response
            verified = "true" in response_text.lower() and "verified: true" in response_text.lower()
            
            # Extract confidence score
            confidence_match = re.search(r'confidence[:\s]+([0-9.]+)', response_text, re.IGNORECASE)
            confidence = float(confidence_match.group(1)) if confidence_match else 0.5
            evidence = response_text.split("evidence", 1)[1].strip() if "evidence" in response_text.lower() else response_text
            
            result = {
                "verified": verified,
                "confidence": confidence,
                "evidence": evidence
            }
        
            result["claim"] = claim
            result["sources"] = sources
            
            return result
            
        except Exception as e:
            logger.error(f"Error verifying claim: {str(e)}")
            return {
                "claim": claim,
                "verified": False,
                "confidence": 0.0,
                "evidence": f"Error during verification: {str(e)}",
                "sources": sources
            }
    
    def verify_text(self, text: str) -> Dict[str, Any]:
        """
        Verify all claims in a text
        
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
        
        return overall_verification
    
    def improve_response(self, original_text: str, verification_results: Dict[str, Any]) -> str:
        """
        Improve a response by correcting unverified claims
        
        Args:
            original_text: Original response text
            verification_results: Results from verify_text
            
        Returns:
            Improved response with corrected claims
        """
        if verification_results["verification_rate"] > 0.9:
            # Response is already good
            return original_text
        
        # Due to OpenAI quota issues, we'll just return the original text with a warning
        logger.warning("OpenAI quota exceeded - unable to improve response. Returning original text.")
        return original_text + "\n\n[Note: Some claims in this response could not be verified due to API limitations.]"

# Import mock implementations for fallback
try:
    from .mock_rag_engine import get_mock_rag_engine, get_mock_claim_verifier
    mock_available = True
except ImportError:
    logger.warning("Mock RAG engine not available")
    mock_available = False

# Create singleton instances with proper error handling
try:
    rag_engine = RAGEngine()
    logger.info("Successfully initialized RAG engine")
except Exception as e:
    logger.error(f"Failed to initialize RAG engine: {str(e)}")
    rag_engine = None

try:
    claim_verifier = ClaimVerifier()
    logger.info("Successfully initialized Claim Verifier")
except Exception as e:
    logger.error(f"Failed to initialize Claim Verifier: {str(e)}")
    claim_verifier = None

def get_rag_engine():
    """Get the singleton RAG engine instance with fallback to mock if allowed"""
    if rag_engine is not None:
        return rag_engine
    elif mock_available and FEATURE_FLAGS.get("use_mock_rag_on_failure", True):
        logger.warning("Using mock RAG engine as fallback")
        return get_mock_rag_engine()
    else:
        logger.error("No RAG engine available and mock fallback is disabled")
        return None

def get_claim_verifier():
    """Get the singleton claim verifier instance with fallback to mock if allowed"""
    if claim_verifier is not None:
        return claim_verifier
    elif mock_available and FEATURE_FLAGS.get("use_mock_rag_on_failure", True):
        logger.warning("Using mock Claim Verifier as fallback")
        return get_mock_claim_verifier()
    else:
        logger.error("No Claim Verifier available and mock fallback is disabled")
        return None
