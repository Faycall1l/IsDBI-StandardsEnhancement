"""
Validation and Approval Agent

This agent is responsible for:
1. Reviewing proposed updates for Shariah compliance and financial best practices
2. Cross-checking proposals against the Knowledge Graph
3. Providing detailed feedback on accepted, rejected, or modified proposals
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime
from dotenv import load_dotenv

from database.knowledge_graph import KnowledgeGraph
from models.validation_schema import ValidationResult, ValidationStatus, ValidationCriteria
from utils.rag_engine import get_rag_engine, get_claim_verifier
from utils.web_retriever import get_web_retriever, get_claim_classifier
from utils.gemini_client import GeminiClient
from config.production import FEATURE_FLAGS, RAG_CONFIG

# Load environment variables
load_dotenv()

class ValidationAgent:
    """Agent for validating proposed enhancements to AAOIFI standards"""
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        """
        Initialize the Validation Agent
        
        Args:
            knowledge_graph: The knowledge graph instance for cross-checking proposals
        """
        self.knowledge_graph = knowledge_graph
        self.logger = logging.getLogger(__name__)
        
        # Initialize RAG engine and claim verifier if enabled
        self.use_rag = FEATURE_FLAGS.get("enable_rag", False)
        self.use_claim_verification = FEATURE_FLAGS.get("enable_claim_verification", False)
        self.use_web_retrieval = FEATURE_FLAGS.get("enable_web_retrieval", False)
        
        # Initialize Gemini client
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            self.gemini_client = GeminiClient(api_key=gemini_api_key)
            self.logger.info("Initialized Gemini client for validation agent")
        else:
            self.logger.error("GEMINI_API_KEY not set, cannot proceed without Gemini")
            raise ValueError("GEMINI_API_KEY environment variable must be set")
        
        if self.use_rag:
            self.logger.info("Initializing RAG engine for validation agent")
            try:
                self.rag_engine = get_rag_engine()
            except Exception as e:
                self.logger.warning(f"Failed to initialize RAG engine: {str(e)}. Some features may be limited.")
                self.rag_engine = None
        
        if self.use_claim_verification:
            self.logger.info("Initializing claim verifier for validation agent")
            try:
                self.claim_verifier = get_claim_verifier()
            except Exception as e:
                self.logger.warning(f"Failed to initialize claim verifier: {str(e)}. Some features may be limited.")
                self.claim_verifier = None
            
        # Initialize web retriever and claim classifier
        if self.use_web_retrieval:
            self.logger.info("Initializing web retriever for validation agent")
            self.web_retriever = get_web_retriever()
            self.claim_classifier = get_claim_classifier()
        
        # Define validation criteria
        self.validation_criteria = {
            "SHARIAH_COMPLIANCE": {
                "description": "Compliance with Islamic principles and Shariah requirements",
                "weight": 0.35
            },
            "TECHNICAL_ACCURACY": {
                "description": "Accuracy of accounting treatments and financial concepts",
                "weight": 0.25
            },
            "CLARITY_AND_PRECISION": {
                "description": "Clarity, precision, and lack of ambiguity in language",
                "weight": 0.20
            },
            "PRACTICAL_IMPLEMENTATION": {
                "description": "Feasibility of implementation in real-world scenarios",
                "weight": 0.15
            },
            "CONSISTENCY": {
                "description": "Consistency with other standards and established practices",
                "weight": 0.05
            },
            "FACTUAL_ACCURACY": {
                "description": "Accuracy of factual claims and references to Islamic finance principles",
                "weight": 0.10  # Adding a new criterion for factual accuracy
            }
        }
        
        # Normalize weights to ensure they sum to 1.0
        total_weight = sum(criterion["weight"] for criterion in self.validation_criteria.values())
        for criterion in self.validation_criteria.values():
            criterion["weight"] = criterion["weight"] / total_weight
        
        # Define prompts for each criterion
        self.criterion_prompts = {
            "SHARIAH_COMPLIANCE": """
            CRITERION: SHARIAH COMPLIANCE
            
            CONTEXT:
            Standard: {standard_title} ({standard_type} {standard_number})
            Enhancement Type: {enhancement_type}
            Original Content: {original_content}
            Enhanced Content: {enhanced_content}
            
            TASK:
            Evaluate the enhanced content for compliance with Islamic principles and Shariah requirements.
            
            Consider:
            1. Adherence to fundamental Islamic principles (e.g., prohibition of riba, gharar, maysir)
            2. Alignment with established Shariah rulings and fatwas
            3. Consistency with AAOIFI Shariah standards and guidelines
            4. Appropriateness of Islamic finance terminology
            
            INSTRUCTIONS:
            1. Provide a score from 0.0 to 1.0, where 1.0 indicates perfect Shariah compliance
            2. Explain your reasoning for the score
            3. Identify any specific Shariah concerns or strengths
            
            FORMAT YOUR RESPONSE AS:
            Score: [0.0-1.0]
            
            Reasoning:
            [Your detailed evaluation]
            """,
            
            "TECHNICAL_ACCURACY": """
            CRITERION: TECHNICAL ACCURACY
            
            CONTEXT:
            Standard: {standard_title} ({standard_type} {standard_number})
            Enhancement Type: {enhancement_type}
            Original Content: {original_content}
            Enhanced Content: {enhanced_content}
            
            TASK:
            Evaluate the enhanced content for technical accuracy in accounting treatments and financial concepts.
            
            Consider:
            1. Correctness of accounting principles and treatments
            2. Accuracy of financial calculations or formulas
            3. Precision in describing financial mechanisms
            4. Alignment with established accounting standards (where applicable)
            
            INSTRUCTIONS:
            1. Provide a score from 0.0 to 1.0, where 1.0 indicates perfect technical accuracy
            2. Explain your reasoning for the score
            3. Identify any technical errors or strengths
            
            FORMAT YOUR RESPONSE AS:
            Score: [0.0-1.0]
            
            Reasoning:
            [Your detailed evaluation]
            """,
            
            "CLARITY_AND_PRECISION": """
            CRITERION: CLARITY AND PRECISION
            
            CONTEXT:
            Standard: {standard_title} ({standard_type} {standard_number})
            Enhancement Type: {enhancement_type}
            Original Content: {original_content}
            Enhanced Content: {enhanced_content}
            
            TASK:
            Evaluate the enhanced content for clarity, precision, and lack of ambiguity in language.
            
            Consider:
            1. Clear and unambiguous language
            2. Logical structure and flow
            3. Precision in terminology
            4. Absence of vague or confusing statements
            
            INSTRUCTIONS:
            1. Provide a score from 0.0 to 1.0, where 1.0 indicates perfect clarity and precision
            2. Explain your reasoning for the score
            3. Identify any unclear passages or particularly clear improvements
            
            FORMAT YOUR RESPONSE AS:
            Score: [0.0-1.0]
            
            Reasoning:
            [Your detailed evaluation]
            """,
            
            "PRACTICAL_IMPLEMENTATION": """
            CRITERION: PRACTICAL IMPLEMENTATION
            
            CONTEXT:
            Standard: {standard_title} ({standard_type} {standard_number})
            Enhancement Type: {enhancement_type}
            Original Content: {original_content}
            Enhanced Content: {enhanced_content}
            
            TASK:
            Evaluate the enhanced content for feasibility of implementation in real-world scenarios.
            
            Consider:
            1. Practicality for financial institutions to implement
            2. Clarity of implementation steps or requirements
            3. Consideration of operational challenges
            4. Adaptability to different market contexts
            
            INSTRUCTIONS:
            1. Provide a score from 0.0 to 1.0, where 1.0 indicates perfect practical implementability
            2. Explain your reasoning for the score
            3. Identify any implementation challenges or practical strengths
            
            FORMAT YOUR RESPONSE AS:
            Score: [0.0-1.0]
            
            Reasoning:
            [Your detailed evaluation]
            """,
            
            "CONSISTENCY": """
            CRITERION: CONSISTENCY
            
            CONTEXT:
            Standard: {standard_title} ({standard_type} {standard_number})
            Enhancement Type: {enhancement_type}
            Original Content: {original_content}
            Enhanced Content: {enhanced_content}
            
            TASK:
            Evaluate the enhanced content for consistency with other standards and established practices.
            
            Consider:
            1. Alignment with other AAOIFI standards
            2. Consistency with established Islamic finance practices
            3. Coherence with the rest of the standard document
            4. Avoidance of contradictions with existing guidelines
            
            INSTRUCTIONS:
            1. Provide a score from 0.0 to 1.0, where 1.0 indicates perfect consistency
            2. Explain your reasoning for the score
            3. Identify any inconsistencies or areas of strong alignment
            
            FORMAT YOUR RESPONSE AS:
            Score: [0.0-1.0]
            
            Reasoning:
            [Your detailed evaluation]
            """,
            
            "FACTUAL_ACCURACY": """
            CRITERION: FACTUAL ACCURACY
            
            CONTEXT:
            Standard: {standard_title} ({standard_type} {standard_number})
            Enhancement Type: {enhancement_type}
            Original Content: {original_content}
            Enhanced Content: {enhanced_content}
            
            TASK:
            Evaluate the enhanced content for factual accuracy of claims and references.
            
            Consider:
            1. Accuracy of factual statements
            2. Correctness of references to Islamic finance principles
            3. Validity of citations or sources
            4. Absence of misleading or incorrect information
            
            INSTRUCTIONS:
            1. Provide a score from 0.0 to 1.0, where 1.0 indicates perfect factual accuracy
            2. Explain your reasoning for the score
            3. Identify any factual errors or particularly well-supported claims
            
            FORMAT YOUR RESPONSE AS:
            Score: [0.0-1.0]
            
            Reasoning:
            [Your detailed evaluation]
            """
        }
    
    def validate_proposal(self, proposal_id: str) -> ValidationResult:
        """
        Validate an enhancement proposal
        
        Args:
            proposal_id: ID of the proposal to validate
            
        Returns:
            ValidationResult object with validation details
        """
        self.logger.info(f"Validating proposal with ID: {proposal_id}")
        
        # Retrieve proposal from knowledge graph
        proposal = self.knowledge_graph.get_node_by_id(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal with ID {proposal_id} not found in knowledge graph")
        
        # Retrieve standard information
        standard_id = proposal["properties"]["standard_id"]
        standard_info = self.knowledge_graph.get_node_by_id(standard_id)
        if not standard_info:
            raise ValueError(f"Standard with ID {standard_id} not found in knowledge graph")
        
        # Retrieve target node information
        target_id = proposal["properties"]["target_id"]
        target_node = self.knowledge_graph.get_node_by_id(target_id)
        if not target_node:
            raise ValueError(f"Target node with ID {target_id} not found in knowledge graph")
        
        # Evaluate proposal against validation criteria
        validation_scores = self._evaluate_proposal(proposal, standard_info, target_node)
        
        # Calculate overall score (weighted average)
        overall_score = sum(
            score * self.validation_criteria[criterion]["weight"]
            for criterion, score in validation_scores.items()
        )
        
        # Determine validation status based on overall score
        status = ValidationStatus.REJECTED
        if overall_score >= 0.8:
            status = ValidationStatus.APPROVED
        elif overall_score >= 0.6:
            status = ValidationStatus.NEEDS_REVISION
        
        # Generate feedback based on validation scores
        feedback = self._generate_feedback(proposal, validation_scores, overall_score, status)
        
        # Generate modified content if status is NEEDS_REVISION
        modified_content = None
        if status == ValidationStatus.NEEDS_REVISION:
            modified_content = self._generate_modified_content(proposal, feedback)
        
        # Create validation result
        result = ValidationResult(
            proposal_id=proposal_id,
            validation_date=datetime.now().isoformat(),
            validation_scores=validation_scores,
            overall_score=overall_score,
            status=status,
            feedback=feedback,
            modified_content=modified_content
        )
        
        # Store validation result in knowledge graph
        self._store_validation_result(result)
        
        self.logger.info(f"Validation completed for proposal {proposal_id}. Status: {status.value}, Score: {overall_score:.2f}")
        return result
    
    def _evaluate_proposal(self, proposal: Dict, standard_info: Dict, target_node: Dict) -> Dict[str, float]:
        """
        Evaluate a proposal against validation criteria
        
        Args:
            proposal: The proposal to evaluate
            standard_info: Information about the related standard
            target_node: The target node being modified
            
        Returns:
            Dictionary mapping criteria to scores (0.0 to 1.0)
        """
        self.logger.info("Evaluating proposal against validation criteria")
        
        # Prepare context for evaluation
        context = {
            "standard_title": standard_info["properties"].get("title", "Islamic Finance Standard"),
            "standard_type": standard_info["properties"].get("standard_type", "FAS"),
            "standard_number": standard_info["properties"].get("standard_number", "4"),
            "enhancement_type": proposal["properties"]["enhancement_type"],
            "original_content": proposal["properties"]["original_content"],
            "enhanced_content": proposal["properties"]["enhanced_content"],
            "reasoning": proposal["properties"]["reasoning"],
            "references": proposal["properties"]["references"]
        }
        
        # Evaluate each criterion
        validation_scores = {}
        for criterion in self.validation_criteria.keys():
            score = self._evaluate_criterion(criterion, context)
            validation_scores[criterion] = score
            self.logger.info(f"Criterion {criterion}: Score = {score:.2f}")
        
        return validation_scores
    
    def _evaluate_criterion(self, criterion: str, context: Dict) -> float:
        """
        Evaluate a proposal against a specific criterion using Gemini
        
        Args:
            criterion: The criterion to evaluate
            context: Context information for evaluation
            
        Returns:
            Score for the criterion (0.0 to 1.0)
        """
        self.logger.info(f"Evaluating criterion: {criterion}")
        
        try:
            # Get the appropriate prompt for this criterion
            prompt = self.criterion_prompts[criterion].format(**context)
            
            # Get context from RAG if enabled and available
            if self.use_rag and criterion in ["CONSISTENCY", "FACTUAL_ACCURACY"] and hasattr(self, 'rag_engine') and self.rag_engine is not None:
                try:
                    query = f"Islamic finance {criterion.lower()} for {context['standard_title']} {context['enhancement_type']} {context['enhanced_content'][:200]}"
                    self.logger.info(f"Retrieving RAG context for criterion {criterion} with query: {query}")
                    
                    if hasattr(self.rag_engine, 'get_retrieval_context'):
                        rag_context = self.rag_engine.get_retrieval_context(query, k=5)
                        prompt += f"""
                        
                        RELEVANT CONTEXT FROM ISLAMIC FINANCE KNOWLEDGE BASE:
                        {rag_context}
                        """
                except Exception as e:
                    self.logger.warning(f"Error retrieving RAG context for {criterion}: {str(e)}. Proceeding without RAG context.")
            
            # Perform claim verification for factual accuracy if available
            if criterion == "FACTUAL_ACCURACY" and self.use_claim_verification and hasattr(self, 'claim_verifier') and self.claim_verifier is not None:
                try:
                    self.logger.info("Performing claim verification for factual accuracy evaluation")
                    verification_results = self.claim_verifier.verify_text(context["enhanced_content"])
                    verification_rate = verification_results.get("verification_rate", 0.0)
                    self.logger.info(f"Claim verification rate: {verification_rate:.2f}")
                    
                    if verification_rate < 0.3:
                        self.logger.warning(f"Very low verification rate ({verification_rate:.2f}) for factual accuracy")
                        return 0.0  # Fail the criterion if most claims can't be verified
                    
                    # Adjust score based on verification rate
                    factual_score = min(1.0, verification_rate * 1.25)  # Scale up slightly, max at 1.0
                    return factual_score
                except Exception as e:
                    self.logger.warning(f"Error during claim verification: {str(e)}. Falling back to LLM evaluation.")
                # If verification rate is very low, we can return it directly
                if verification_results['verification_rate'] < 0.5:
                    self.logger.warning(f"Very low verification rate ({verification_results['verification_rate']:.2f}) for factual accuracy")
                    return verification_results['verification_rate']
            
            # Use Gemini for criterion evaluation
            try:
                # Generate response with Gemini
                response_text = self.gemini_client.generate_text(
                    prompt=prompt,
                    temperature=0.3,  # Lower temperature for more deterministic responses
                    max_tokens=1000,
                    system_prompt="You are an expert in Islamic finance and Shariah compliance. Evaluate the proposal against the specified criterion and provide a score from 0.0 to 1.0, where 1.0 is perfect compliance with the criterion."
                )
                self.logger.info(f"Successfully evaluated criterion '{criterion}' with Gemini")
            except Exception as e:
                self.logger.error(f"Error evaluating criterion with Gemini: {str(e)}")
                # Return a default score since we can't evaluate
                return 0.5  # Neutral score
            
            # Parse score from response
            score_text = response_text.strip().split('\n')[0]
            score_match = re.search(r'([0-9.]+)', score_text)
            
            if score_match:
                score = float(score_match.group(1))
                # Ensure score is in range [0.0, 1.0]
                score = max(0.0, min(1.0, score))
                return score
            else:
                self.logger.warning(f"Could not parse score from response: {score_text}")
                return 0.5  # Default to neutral score if parsing fails
                
        except Exception as e:
            self.logger.error(f"Error evaluating criterion {criterion}: {str(e)}")
            return 0.5  # Default to neutral score on error
    
    def _generate_feedback(self, proposal: Dict, validation_scores: Dict[str, float], 
                          overall_score: float, status: ValidationStatus, 
                          claim_verification_results: Dict[str, Any] = None) -> str:
        """
        Generate feedback based on validation scores
        
        Args:
            proposal: The proposal being validated
            validation_scores: Dictionary mapping criteria to scores
            overall_score: Overall weighted score
            status: Validation status (APPROVED, NEEDS_REVISION, REJECTED)
            claim_verification_results: Optional results from claim verification
            
        Returns:
            Feedback text
        """
        self.logger.info(f"Generating feedback for proposal with status: {status.value}")
        
        # Prepare context for feedback generation
        context = {
            "enhancement_type": proposal["properties"]["enhancement_type"],
            "original_content": proposal["properties"]["original_content"],
            "enhanced_content": proposal["properties"]["enhanced_content"],
            "reasoning": proposal["properties"]["reasoning"],
            "references": proposal["properties"]["references"],
            "overall_score": overall_score,
            "status": status.value,
            "validation_scores": json.dumps(validation_scores, indent=2)
        }
        
        # Add claim verification results if available
        if claim_verification_results:
            context["claim_verification"] = json.dumps(claim_verification_results, indent=2)
        
        # Prepare prompt for feedback generation
        prompt = f"""
        CONTEXT:
        Enhancement Type: {context["enhancement_type"]}
        
        Original Content:
        {context["original_content"]}
        
        Enhanced Content:
        {context["enhanced_content"]}
        
        Reasoning:
        {context["reasoning"]}
        
        References:
        {context["references"]}
        
        Validation Scores:
        {context["validation_scores"]}
        
        Overall Score: {context["overall_score"]:.2f}
        Status: {context["status"]}
        
        TASK:
        Generate detailed feedback for this enhancement proposal based on the validation scores and status.
        
        The feedback should:
        1. Start with a brief summary of the proposal's strengths and weaknesses
        2. Provide specific feedback for each criterion, especially those with low scores
        3. For NEEDS_REVISION status, include clear recommendations for improvement
        4. For REJECTED status, explain the primary reasons for rejection
        5. For APPROVED status, note any minor suggestions for further refinement
        
        FORMAT:
        Please structure the feedback in sections with clear headings.
        """
        
        # Check if the prompt is too long and truncate if necessary
        if len(prompt) > 6000:  # Conservative limit to avoid token issues
            self.logger.warning(f"Prompt is too long ({len(prompt)} chars). Truncating...")
            # Keep task instructions but truncate the context part
            task_part = prompt[prompt.find("TASK:"):]
            context_part = prompt[:prompt.find("TASK:")]
            truncated_context = context_part[:2000] + "... [content truncated due to length]"
            prompt = truncated_context + task_part
        
        # Use Gemini for feedback generation
        try:
            # Generate response with Gemini
            response_text = self.gemini_client.generate_text(
                prompt=prompt,
                temperature=0.7,
                max_tokens=2000,
                system_prompt="You are an expert in Islamic finance, Shariah compliance, and accounting standards."
            )
            self.logger.info("Generated feedback with Gemini")
            return response_text
        except Exception as e:
            self.logger.error(f"Error generating feedback with Gemini: {str(e)}")
            # Return a basic feedback if generation fails
            return f"""
            Validation Status: {status.value}
            Overall Score: {overall_score:.2f}
            
            Summary:
            The proposal has been {status.value.lower()} based on the validation criteria.
            
            Scores:
            {', '.join([f"{criterion}: {score:.2f}" for criterion, score in validation_scores.items()])}
            
            Note: Detailed feedback could not be generated due to a technical issue.
            """
    
    def _generate_modified_content(self, proposal: Dict, feedback: str) -> str:
        """
        Generate modified content for proposals that need revision
        
        Args:
            proposal: The proposal being validated
            feedback: Validation feedback
            
        Returns:
            Modified content text
        """
        self.logger.info("Generating modified content for proposal that needs revision")
        
        try:
            # Prepare context for generating modified content
            context = {
                "enhancement_type": proposal["properties"]["enhancement_type"],
                "original_content": proposal["properties"]["original_content"],
                "enhanced_content": proposal["properties"]["enhanced_content"],
                "feedback": feedback
            }
            
            # Prepare prompt for generating modified content
            prompt = f"""
            CONTEXT:
            Enhancement Type: {context["enhancement_type"]}
            
            Original Content:
            {context["original_content"]}
            
            Proposed Enhanced Content:
            {context["enhanced_content"]}
            
            Validation Feedback:
            {context["feedback"]}
            
            TASK:
            Based on the validation feedback, generate a modified version of the enhanced content that addresses the concerns while preserving the valuable aspects of the proposal.
            
            The modified content should:
            1. Address all concerns mentioned in the feedback
            2. Maintain Shariah compliance
            3. Ensure technical accuracy
            4. Provide clarity and precision
            5. Be practically implementable
            
            PROVIDE ONLY THE MODIFIED CONTENT, formatted appropriately for its type (definition, accounting treatment, etc.).
            """
            
            # Check if the prompt is still too long and truncate if necessary
            if len(prompt) > 6000:  # Conservative limit to avoid token issues
                self.logger.warning(f"Prompt is too long ({len(prompt)} chars). Truncating...")
                # Keep task instructions but truncate the context part
                task_part = prompt[prompt.find("TASK:"):]
                context_part = prompt[:prompt.find("TASK:")]
                truncated_context = context_part[:2000] + "... [content truncated due to length]"
                prompt = truncated_context + task_part
            
            # Use Gemini for text generation
            try:
                # Generate response with Gemini
                response_text = self.gemini_client.generate_text(
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=1000,
                    system_prompt="You are an expert in Islamic finance, Shariah compliance, and accounting standards."
                )
                self.logger.info(f"Generated modified content with Gemini")
            except Exception as e:
                self.logger.error(f"Error using Gemini: {str(e)}")
                # Return a default response if Gemini fails
                return proposal["properties"]["enhanced_content"]  # Return original enhanced content if modification fails
            
            return response_text
            
        except Exception as e:
            self.logger.error(f"Error generating modified content: {str(e)}")
            return proposal["properties"]["enhanced_content"]  # Return original enhanced content if modification fails
    
    def _store_validation_result(self, result: ValidationResult) -> None:
        """
        Store validation result in the knowledge graph
        
        Args:
            result: ValidationResult object to store
        """
        # Convert to dictionary for storage
        result_dict = result.dict()
        
        # Store the validation result node
        result_node_id = self.knowledge_graph.create_node(
            label="ValidationResult",
            properties={
                "proposal_id": result.proposal_id,
                "validation_date": result.validation_date,
                "overall_score": result.overall_score,
                "status": result.status.value,
                "feedback": result.feedback,
                "modified_content": result.modified_content if result.modified_content else ""
            }
        )
        
        # Store validation scores as separate nodes
        for criterion, score in result.validation_scores.items():
            score_node_id = self.knowledge_graph.create_node(
                label="ValidationScore",
                properties={
                    "criterion": criterion,
                    "score": score,
                    "description": self.validation_criteria[criterion]["description"]
                }
            )
            
            # Link score to validation result
            self.knowledge_graph.create_relationship(
                start_node_id=result_node_id,
                end_node_id=score_node_id,
                relationship_type="HAS_SCORE"
            )
        
        # Link validation result to proposal
        self.knowledge_graph.create_relationship(
            start_node_id=result.proposal_id,
            end_node_id=result_node_id,
            relationship_type="HAS_VALIDATION"
        )
        
        self.logger.info(f"Successfully stored validation result in knowledge graph")
