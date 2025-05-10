"""
Enhancement Agent

This agent is responsible for:
1. Analyzing extracted data from AAOIFI standards
2. Proposing AI-driven updates to the standards
3. Using chain-of-thought reasoning for generating enhancements
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

from database.knowledge_graph import KnowledgeGraph
from models.enhancement_schema import EnhancementProposal, EnhancementStatus, EnhancementType
from utils.gemini_client import GeminiClient
from utils.rag_engine import get_rag_engine, get_claim_verifier
from config.production import FEATURE_FLAGS, RAG_CONFIG

# Import hybrid storage manager if available
try:
    from integration.hybrid_storage_manager import get_hybrid_storage_manager
    HYBRID_STORAGE_AVAILABLE = True
except ImportError:
    HYBRID_STORAGE_AVAILABLE = False

# Import Neo4j integration
from agents.enhancement_agent.neo4j_integration import get_neo4j_enhancement_store

# Load environment variables
load_dotenv()

class EnhancementAgent:
    """Agent for proposing enhancements to AAOIFI standards"""
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        """
        Initialize the Enhancement Agent
        
        Args:
            knowledge_graph: The knowledge graph instance for retrieving context
        """
        self.knowledge_graph = knowledge_graph
        self.logger = logging.getLogger(__name__)
        
        # Initialize RAG engine if enabled
        self.use_rag = FEATURE_FLAGS.get("enable_rag", False)
        if self.use_rag:
            self.logger.info("Initializing RAG engine for enhancement agent")
            try:
                self.rag_engine = get_rag_engine()
            except Exception as e:
                self.logger.warning(f"Failed to initialize RAG engine: {str(e)}. Some features may be limited.")
                self.rag_engine = None
        
        # Initialize claim verifier if enabled
        self.use_claim_verification = FEATURE_FLAGS.get("enable_claim_verification", False)
        if self.use_claim_verification:
            self.logger.info("Initializing claim verifier for enhancement agent")
            try:
                self.claim_verifier = get_claim_verifier()
            except Exception as e:
                self.logger.warning(f"Failed to initialize claim verifier: {str(e)}. Some features may be limited.")
                self.claim_verifier = None
        
        # Initialize Neo4j integration if enabled
        self.use_neo4j = os.getenv("USE_NEO4J", "false").lower() == "true"
        if self.use_neo4j:
            self.logger.info("Initializing Neo4j integration for enhancement agent")
            self.neo4j_store = get_neo4j_enhancement_store()
            
            # Initialize hybrid storage manager if available
            self.use_hybrid_storage = HYBRID_STORAGE_AVAILABLE
            if self.use_hybrid_storage:
                try:
                    self.hybrid_storage = get_hybrid_storage_manager()
                    self.logger.info("Initialized hybrid storage manager for Neo4j integration")
                except Exception as e:
                    self.logger.error(f"Failed to initialize hybrid storage: {str(e)}")
                    self.use_hybrid_storage = False
            else:
                self.logger.warning("Hybrid storage not available, using Neo4j directly")
        else:
            self.use_hybrid_storage = False
        
        # Initialize Gemini client
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            self.gemini_client = GeminiClient(api_key=gemini_api_key)
            self.logger.info("Initialized Gemini client for enhancement agent")
        else:
            self.logger.error("GEMINI_API_KEY not set, cannot proceed without Gemini")
            raise ValueError("GEMINI_API_KEY environment variable must be set")
        
        # Enhancement types
        self.enhancement_types = {
            "DEFINITION": "Improvement to a definition for clarity and precision",
            "ACCOUNTING_TREATMENT": "Enhancement to accounting treatment procedures",
            "TRANSACTION_STRUCTURE": "Refinement of transaction structure or steps",
            "AMBIGUITY_RESOLUTION": "Resolution of identified ambiguities",
            "NEW_GUIDANCE": "Addition of new guidance for emerging scenarios"
        }
        
    def generate_enhancements(self, standard_id: str) -> List[EnhancementProposal]:
        """
        Generate enhancement proposals for a standard
        
        Args:
            standard_id: ID of the standard in the knowledge graph
            
        Returns:
            List of enhancement proposals
        """
        self.logger.info(f"Generating enhancements for standard ID: {standard_id}")
        
        # Retrieve standard information from knowledge graph
        standard_info = self.knowledge_graph.get_node_by_id(standard_id)
        if not standard_info:
            raise ValueError(f"Standard with ID {standard_id} not found in knowledge graph")
        
        # Retrieve related nodes (definitions, accounting treatments, etc.)
        related_nodes = self.knowledge_graph.get_related_nodes(standard_id)
        
        # Generate enhancements for different components
        proposals = []
        
        # Process definitions
        definition_nodes = [node for node in related_nodes if node["label"] == "Definition"]
        definition_enhancements = self._enhance_definitions(standard_info, definition_nodes)
        proposals.extend(definition_enhancements)
        
        # Process accounting treatments
        treatment_nodes = [node for node in related_nodes if node["label"] == "AccountingTreatment"]
        treatment_enhancements = self._enhance_accounting_treatments(standard_info, treatment_nodes)
        proposals.extend(treatment_enhancements)
        
        # Process transaction structures
        structure_nodes = [node for node in related_nodes if node["label"] == "TransactionStructure"]
        structure_enhancements = self._enhance_transaction_structures(standard_info, structure_nodes)
        proposals.extend(structure_enhancements)
        
        # Store proposals in hybrid storage if enabled
        if self.use_hybrid_storage:
            self.logger.info(f"Storing {len(proposals)} enhancement proposals using hybrid storage")
            for proposal in proposals:
                result = self._store_enhancement_proposal(proposal)
                if result:
                    self.logger.info(f"Stored proposal with ID {result} using hybrid storage")
        
        # Process ambiguities
        ambiguity_nodes = [node for node in related_nodes if node["label"] == "Ambiguity"]
        ambiguity_enhancements = self._resolve_ambiguities(standard_info, ambiguity_nodes)
        proposals.extend(ambiguity_enhancements)
        
        # Generate new guidance based on the overall standard
        new_guidance = self._generate_new_guidance(standard_info, related_nodes)
        proposals.extend(new_guidance)
        
        return proposals
    
    def _store_enhancement_proposal(self, proposal: EnhancementProposal) -> str:
        """
        Store an enhancement proposal in the knowledge graph and Neo4j (if enabled)
        
        Args:
            proposal: The enhancement proposal to store
            
        Returns:
            ID of the stored proposal in the knowledge graph
        """
        try:
            # Use hybrid storage if available and enabled
            if self.use_hybrid_storage:
                try:
                    # Store in both knowledge graph and Neo4j
                    result = self.hybrid_storage.store_enhancement(proposal, self.knowledge_graph)
                    self.logger.info(f"Stored enhancement proposal using hybrid storage: KG ID: {result['kg_id']}, Neo4j ID: {result['neo4j_id']}")
                    return result['kg_id']
                except Exception as e:
                    self.logger.error(f"Failed to store using hybrid storage: {str(e)}. Falling back to knowledge graph only.")
            
            # Fall back to knowledge graph only if hybrid storage fails or is not available
            # Store the proposal node
            proposal_id = self.knowledge_graph.create_node(
                label="EnhancementProposal",
                properties={
                    "standard_id": proposal.standard_id,
                    "enhancement_type": proposal.enhancement_type,
                    "target_id": proposal.target_id,
                    "original_content": proposal.original_content,
                    "enhanced_content": proposal.enhanced_content,
                    "reasoning": proposal.reasoning,
                    "references": proposal.references,
                    "status": proposal.status,
                    "proposal_id": f"proposal-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                }
            )
            
            # Link proposal to standard
            self.knowledge_graph.create_relationship(
                start_node_id=proposal.standard_id,
                end_node_id=proposal_id,
                relationship_type="HAS_ENHANCEMENT"
            )
            
            # Link proposal to target node
            self.knowledge_graph.create_relationship(
                start_node_id=proposal_id,
                end_node_id=proposal.target_id,
                relationship_type="ENHANCES"
            )
            
            # Also store in Neo4j directly if hybrid storage is not available but Neo4j is enabled
            if self.use_neo4j and not self.use_hybrid_storage:
                try:
                    neo4j_id = self.neo4j_store.store_enhancement_proposal(proposal, proposal.standard_id)
                    if neo4j_id:
                        self.logger.info(f"Stored proposal {proposal_id} in Neo4j with ID: {neo4j_id}")
                except Exception as e:
                    self.logger.error(f"Failed to store proposal in Neo4j: {str(e)}")
            
            self.logger.info(f"Stored enhancement proposal with ID: {proposal_id} in knowledge graph")
            return proposal_id
            
        except Exception as e:
            self.logger.error(f"Failed to store enhancement proposal: {str(e)}")
            return None
    
    def _enhance_accounting_treatments(self, standard_info: Dict, treatment_nodes: List[Dict]) -> List[EnhancementProposal]:
        """Generate enhancements for accounting treatments"""
        enhancements = []
        
        for treatment in treatment_nodes:
            # Prepare context for the LLM
            context = {
                "standard_title": standard_info["properties"]["title"],
                "standard_type": standard_info["properties"]["standard_type"],
                "standard_number": standard_info["properties"]["standard_number"],
                "treatment_title": treatment["properties"]["title"],
                "treatment_description": treatment["properties"]["description"]
            }
            
            # Generate enhancement using LLM
            enhancement = self._generate_enhancement_with_llm(
                enhancement_type="ACCOUNTING_TREATMENT",
                context=context,
                prompt_template="""
                You are an expert in Islamic finance and accounting standards. 
                
                CONTEXT:
                Standard: {standard_title} ({standard_type} {standard_number})
                Accounting Treatment: {treatment_title}
                Current Description: {treatment_description}
                
                TASK:
                Analyze the current accounting treatment and propose enhancements that:
                1. Improve clarity and precision
                2. Address potential implementation challenges
                3. Ensure Shariah compliance
                4. Align with international accounting best practices where applicable
                
                Provide:
                1. Enhanced accounting treatment description
                2. A detailed explanation of your changes and their benefits
                3. References to Islamic finance principles and accounting standards that support your enhancement
                """
            )
            
            if enhancement:
                proposal = EnhancementProposal(
                    standard_id=standard_info["id"],
                    enhancement_type="ACCOUNTING_TREATMENT",
                    target_id=treatment["id"],
                    original_content=treatment["properties"]["description"],
                    enhanced_content=enhancement["content"],
                    reasoning=enhancement["reasoning"],
                    references=enhancement["references"],
                    status="PROPOSED"
                )
                enhancements.append(proposal)
        
        return enhancements
    
    def _enhance_definitions(self, standard_info: Dict, definition_nodes: List[Dict]) -> List[EnhancementProposal]:
        """Generate enhancements for definitions"""
        enhancements = []
        
        for definition in definition_nodes:
            # Prepare context for the LLM
            context = {
                "standard_title": standard_info["properties"]["title"],
                "standard_type": standard_info["properties"]["standard_type"],
                "standard_number": standard_info["properties"]["standard_number"],
                "term": definition["properties"]["term"],
                "current_definition": definition["properties"]["definition"]
            }
            
            # Generate enhancement using LLM
            enhancement = self._generate_enhancement_with_llm(
                enhancement_type="DEFINITION",
                context=context,
                prompt_template="""
                You are an expert in Islamic finance and accounting standards. 
                
                CONTEXT:
                Standard: {standard_title} ({standard_type} {standard_number})
                Term: {term}
                Current Definition: {current_definition}
                
                TASK:
                Analyze the current definition and propose an enhanced version that:
                1. Is more precise and clear
                2. Eliminates potential ambiguities
                3. Aligns with Shariah principles
                4. Incorporates modern financial practices where relevant
                
                Provide:
                1. An enhanced definition
                2. A detailed explanation of your changes and their benefits
                3. References to Islamic finance principles that support your enhancement
                """
            )
            
            if enhancement:
                proposal = EnhancementProposal(
                    standard_id=standard_info["id"],
                    enhancement_type="DEFINITION",
                    target_id=definition["id"],
                    original_content=definition["properties"]["definition"],
                    enhanced_content=enhancement["content"],
                    reasoning=enhancement["reasoning"],
                    references=enhancement["references"],
                    status="PROPOSED"
                )
                enhancements.append(proposal)
        
        return enhancements
    
    def _enhance_transaction_structures(self, standard_info: Dict, structure_nodes: List[Dict]) -> List[EnhancementProposal]:
        """Generate enhancements for transaction structures"""
        enhancements = []
        
        for structure in structure_nodes:
            # Prepare context for the LLM
            context = {
                "standard_title": standard_info["properties"]["title"],
                "standard_type": standard_info["properties"]["standard_type"],
                "standard_number": standard_info["properties"]["standard_number"],
                "structure_title": structure["properties"]["title"],
                "structure_description": structure["properties"]["description"],
                "structure_steps": json.loads(structure["properties"]["steps"]) if isinstance(structure["properties"]["steps"], str) else structure["properties"]["steps"]
            }
            
            # Generate enhancement using LLM
            enhancement = self._generate_enhancement_with_llm(
                enhancement_type="TRANSACTION_STRUCTURE",
                context=context,
                prompt_template="""
                You are an expert in Islamic finance and accounting standards. 
                
                CONTEXT:
                Standard: {standard_title} ({standard_type} {standard_number})
                Transaction Structure: {structure_title}
                Current Description: {structure_description}
                Current Steps: {structure_steps}
                
                TASK:
                Analyze the current transaction structure and propose enhancements that:
                1. Improve clarity and precision of steps
                2. Address potential implementation challenges
                3. Ensure Shariah compliance
                4. Optimize the transaction flow
                
                Provide:
                1. Enhanced transaction structure description
                2. Enhanced transaction steps (numbered list)
                3. A detailed explanation of your changes and their benefits
                4. References to Islamic finance principles that support your enhancement
                """
            )
            
            if enhancement:
                proposal = EnhancementProposal(
                    standard_id=standard_info["id"],
                    enhancement_type="TRANSACTION_STRUCTURE",
                    target_id=structure["id"],
                    original_content=json.dumps({
                        "description": structure["properties"]["description"],
                        "steps": structure["properties"]["steps"]
                    }),
                    enhanced_content=enhancement["content"],
                    reasoning=enhancement["reasoning"],
                    references=enhancement["references"],
                    status="PROPOSED"
                )
                enhancements.append(proposal)
        
        return enhancements
    
    def _resolve_ambiguities(self, standard_info: Dict, ambiguity_nodes: List[Dict]) -> List[EnhancementProposal]:
        """Generate resolutions for identified ambiguities"""
        enhancements = []
        
        for ambiguity in ambiguity_nodes:
            # Prepare context for the LLM
            context = {
                "standard_title": standard_info["properties"]["title"],
                "standard_type": standard_info["properties"]["standard_type"],
                "standard_number": standard_info["properties"]["standard_number"],
                "ambiguity_text": ambiguity["properties"]["text"],
                "ambiguity_context": ambiguity["properties"]["context"],
                "ambiguity_indicator": ambiguity["properties"]["indicator"]
            }
            
            # Generate enhancement using LLM
            enhancement = self._generate_enhancement_with_llm(
                enhancement_type="AMBIGUITY_RESOLUTION",
                context=context,
                prompt_template="""
                You are an expert in Islamic finance and accounting standards. 
                
                CONTEXT:
                Standard: {standard_title} ({standard_type} {standard_number})
                Ambiguous Text: {ambiguity_text}
                Context: {ambiguity_context}
                Ambiguity Indicator: {ambiguity_indicator}
                
                TASK:
                Resolve the identified ambiguity by:
                1. Analyzing the source of ambiguity
                2. Proposing clear and precise language to replace the ambiguous text
                3. Ensuring Shariah compliance
                4. Providing guidance for consistent application
                
                Provide:
                1. Resolved text (to replace the ambiguous text)
                2. A detailed explanation of how your resolution addresses the ambiguity
                3. References to Islamic finance principles that support your resolution
                """
            )
            
            if enhancement:
                proposal = EnhancementProposal(
                    standard_id=standard_info["id"],
                    enhancement_type="AMBIGUITY_RESOLUTION",
                    target_id=ambiguity["id"],
                    original_content=ambiguity["properties"]["text"],
                    enhanced_content=enhancement["content"],
                    reasoning=enhancement["reasoning"],
                    references=enhancement["references"],
                    status="PROPOSED"
                )
                enhancements.append(proposal)
        
        return enhancements
    
    def _generate_new_guidance(self, standard_info: Dict, related_nodes: List[Dict]) -> List[EnhancementProposal]:
        """Generate new guidance based on the overall standard"""
        # Prepare context for the LLM
        context = {
            "standard_title": standard_info["properties"].get("title", "Islamic Finance Standard"),
            "standard_type": standard_info["properties"].get("standard_type", "FAS"),
            "standard_number": standard_info["properties"].get("standard_number", "4"),
            "definitions": [node["properties"] for node in related_nodes if node["label"] == "Definition"],
            "accounting_treatments": [node["properties"] for node in related_nodes if node["label"] == "AccountingTreatment"],
            "transaction_structures": [node["properties"] for node in related_nodes if node["label"] == "TransactionStructure"]
        }
        
        # Generate enhancement using LLM
        enhancement = self._generate_enhancement_with_llm(
            enhancement_type="NEW_GUIDANCE",
            context=context,
            prompt_template="""
            You are an expert in Islamic finance and accounting standards. 
            
            CONTEXT:
            Standard: {standard_title} ({standard_type} {standard_number})
            
            TASK:
            Based on your analysis of the standard, identify areas where new guidance is needed to:
            1. Address emerging financial practices or instruments
            2. Clarify application in digital/fintech contexts
            3. Harmonize with international accounting standards while maintaining Shariah compliance
            4. Provide guidance for complex or edge cases
            
            Provide:
            1. Title for the new guidance section
            2. Detailed content for the new guidance
            3. A detailed explanation of why this guidance is necessary
            4. References to Islamic finance principles and modern practices that support this guidance
            """
        )
        
        if enhancement:
            proposal = EnhancementProposal(
                standard_id=standard_info["id"],
                enhancement_type="NEW_GUIDANCE",
                target_id=standard_info["id"],  # The target is the standard itself
                original_content="",  # No original content as this is new guidance
                enhanced_content=enhancement["content"],
                reasoning=enhancement["reasoning"],
                references=enhancement["references"],
                status="PROPOSED"
            )
            return [proposal]
        
        return []
    
    def _generate_enhancement_with_llm(self, enhancement_type: str, context: Dict, prompt_template: str) -> Optional[Dict]:
        """
        Generate enhancement using LLM with chain-of-thought reasoning
        
        Args:
            enhancement_type: Type of enhancement to generate
            context: Context information for the prompt
            prompt_template: Template for the prompt
            
        Returns:
            Dictionary with enhancement content, reasoning, and references
        """
        try:
            # Format the prompt with context
            prompt = prompt_template.format(**context)
            
            # Check for large text fields and truncate if necessary
            max_content_length = 2000  # Characters, not tokens
            for key, value in context.items():
                if isinstance(value, str) and len(value) > max_content_length:
                    self.logger.warning(f"Truncating large content field: {key} from {len(value)} to {max_content_length} characters")
                    context[key] = value[:max_content_length] + "... [content truncated due to length]"
            
            # Reformat prompt with truncated context
            prompt = prompt_template.format(**context)
            
            # Add RAG context if enabled and available
            if self.use_rag and hasattr(self, 'rag_engine') and self.rag_engine is not None:
                try:
                    # Create a query based on the enhancement type and context
                    query = f"Islamic finance standard {enhancement_type.lower()} for {context.get('title', '')} {context.get('content', '')}"
                    self.logger.info(f"Retrieving RAG context for query: {query}")
                    
                    # Get relevant context from RAG engine
                    if hasattr(self.rag_engine, 'get_retrieval_context'):
                        rag_context = self.rag_engine.get_retrieval_context(query, k=RAG_CONFIG.get("retrieval_k", 5))
                        
                        # Add RAG context to the prompt
                        prompt = f"""
                        {prompt}
                        
                        RELEVANT ISLAMIC FINANCE CONTEXT FROM KNOWLEDGE BASE:
                        {rag_context}
                        """
                except Exception as e:
                    self.logger.warning(f"Error retrieving RAG context: {str(e)}. Proceeding without RAG context.")
            
            # Add chain-of-thought instructions
            cot_prompt = f"""
            {prompt}
            
            IMPORTANT: Use chain-of-thought reasoning to arrive at your enhancement.
            
            1. First, analyze the current content and identify specific issues or areas for improvement.
            2. For each issue, consider multiple alternative approaches to address it.
            3. Evaluate each approach based on Shariah compliance, clarity, and practical implementation.
            4. Select the best approach and formulate your enhancement.
            5. Ensure all factual claims are accurate and supported by Islamic finance principles.
            
            Format your response as follows:
            
            ANALYSIS:
            [Your step-by-step analysis of the current content]
            
            ALTERNATIVE APPROACHES:
            [List and brief evaluation of alternative approaches]
            
            ENHANCED CONTENT:
            [Your proposed enhancement]
            
            REASONING:
            [Detailed explanation of why your enhancement improves the standard]
            
            REFERENCES:
            [Relevant Islamic finance principles, sources, or standards that support your enhancement]
            """
            
            # Check if the prompt is still too long and truncate if necessary
            if len(cot_prompt) > 6000:  # Conservative limit to avoid token issues
                self.logger.warning(f"Prompt is too long ({len(cot_prompt)} chars). Truncating...")
                # Keep instructions but truncate the context part
                instruction_part = cot_prompt[cot_prompt.find("IMPORTANT:"):]
                context_part = cot_prompt[:cot_prompt.find("IMPORTANT:")]
                truncated_context = context_part[:2000] + "... [content truncated due to length]"
                cot_prompt = truncated_context + instruction_part
            
            # Use Gemini for text generation
            try:
                self.logger.info("Generating enhancement with Gemini")
                # Make sure Gemini client is initialized
                if not hasattr(self, 'gemini_client') or self.gemini_client is None:
                    gemini_api_key = os.getenv("GEMINI_API_KEY")
                    if gemini_api_key:
                        self.gemini_client = GeminiClient(api_key=gemini_api_key)
                        self.logger.info("Initialized Gemini client on demand")
                    else:
                        raise ValueError("GEMINI_API_KEY not set, cannot proceed without Gemini")
                
                response_text = self.gemini_client.generate_text(
                    prompt=cot_prompt,
                    temperature=0.7,
                    max_tokens=2000,
                    system_prompt="You are an expert in Islamic finance and accounting standards."
                )
                self.logger.info("Successfully generated enhancement with Gemini")
            except Exception as e:
                self.logger.error(f"Error generating enhancement with Gemini: {str(e)}")
                # Return a placeholder response since API call failed
                response_text = f"""ENHANCED CONTENT:
Unable to generate enhancement with Gemini. Please check your API key and connection.

REASONING:
The system encountered an error when calling the Gemini API.

REFERENCES:
N/A"""
                self.logger.warning("Returning placeholder response due to API limitations")
            
            # Verify claims if enabled
            if self.use_claim_verification:
                self.logger.info("Verifying claims in enhancement response")
                
                # Extract the enhanced content and reasoning sections for verification
                enhanced_content = self._extract_section(response_text, "ENHANCED CONTENT:")
                reasoning = self._extract_section(response_text, "REASONING:")
                
                # Verify claims in both sections
                content_verification = self.claim_verifier.verify_text(enhanced_content)
                reasoning_verification = self.claim_verifier.verify_text(reasoning)
                
                # Log verification results
                self.logger.info(f"Enhanced content verification rate: {content_verification['verification_rate']:.2f}")
                self.logger.info(f"Reasoning verification rate: {reasoning_verification['verification_rate']:.2f}")
                
                # If verification rate is too low, improve the response
                if content_verification['verification_rate'] < 0.8:
                    self.logger.warning("Low verification rate for enhanced content, improving response")
                    enhanced_content = self.claim_verifier.improve_response(enhanced_content, content_verification)
                
                if reasoning_verification['verification_rate'] < 0.8:
                    self.logger.warning("Low verification rate for reasoning, improving response")
                    reasoning = self.claim_verifier.improve_response(reasoning, reasoning_verification)
            else:
                # Parse the response to extract the components without verification
                enhanced_content = self._extract_section(response_text, "ENHANCED CONTENT:")
                reasoning = self._extract_section(response_text, "REASONING:")
            
            # Extract references section
            references = self._extract_section(response_text, "REFERENCES:")
            
            return {
                "content": enhanced_content,
                "reasoning": reasoning,
                "references": references
            }
            
        except Exception as e:
            self.logger.error(f"Error generating enhancement with LLM: {str(e)}")
            return None
    
    def _extract_section(self, text: str, section_header: str) -> str:
        """Extract a section from the LLM response"""
        if section_header not in text:
            return ""
        
        start_idx = text.find(section_header) + len(section_header)
        next_section_idx = float('inf')
        
        # Find the start of the next section
        for header in ["ANALYSIS:", "ALTERNATIVE APPROACHES:", "ENHANCED CONTENT:", "REASONING:", "REFERENCES:"]:
            if header == section_header:
                continue
            
            idx = text.find(header, start_idx)
            if idx != -1 and idx < next_section_idx:
                next_section_idx = idx
        
        # Extract the section content
        if next_section_idx == float('inf'):
            section_content = text[start_idx:].strip()
        else:
            section_content = text[start_idx:next_section_idx].strip()
        
        return section_content
