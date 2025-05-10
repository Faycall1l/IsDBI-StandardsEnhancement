#!/usr/bin/env python3
"""
Component Testing Script

This script provides functions to test individual components of the
Islamic Finance Standards AI system.
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("component_tests.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import system components
from database.mock_knowledge_graph import MockKnowledgeGraph
from database.knowledge_graph import KnowledgeGraph
from agents.document_agent.document_agent import DocumentAgent
from agents.enhancement_agent.enhancement_agent import EnhancementAgent
from agents.validation_agent.validation_agent import ValidationAgent

# Monkey patch the knowledge graph to use our mock implementation
def use_mock_knowledge_graph():
    """Patch the KnowledgeGraph class to use our mock implementation"""
    import types
    from database.knowledge_graph import KnowledgeGraph
    original_init = KnowledgeGraph.__init__
    
    def mock_init(self):
        """Mock initialization that doesn't require Neo4j"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Using mock knowledge graph implementation")
        
        # Use the mock implementation
        mock_kg = MockKnowledgeGraph()
        
        # Copy all attributes and methods from mock to self
        for attr_name in dir(mock_kg):
            if not attr_name.startswith('__'):
                attr = getattr(mock_kg, attr_name)
                if callable(attr):
                    setattr(self, attr_name, types.MethodType(attr.__func__, self))
                else:
                    setattr(self, attr_name, attr)
    
    # Apply the monkey patch
    KnowledgeGraph.__init__ = mock_init
    logger.info("Knowledge graph monkey patched to use mock implementation")

# Test functions
def test_document_processing(file_path: str, use_mock: bool = True):
    """Test document processing functionality"""
    logger.info(f"Testing document processing with file: {file_path}")
    
    try:
        # Use mock knowledge graph if requested
        if use_mock:
            use_mock_knowledge_graph()
        
        # Initialize components
        kg = KnowledgeGraph()
        document_agent = DocumentAgent(kg)
        
        # Process document
        document = document_agent.process_document(file_path)
        
        # Log results
        logger.info(f"Successfully processed document: {document.title}")
        logger.info(f"Standard type: {document.standard_type}")
        logger.info(f"Standard number: {document.standard_number}")
        logger.info(f"Extracted {len(document.definitions)} definitions")
        logger.info(f"Extracted {len(document.accounting_treatments)} accounting treatments")
        logger.info(f"Extracted {len(document.transaction_structures)} transaction structures")
        logger.info(f"Identified {len(document.ambiguities)} ambiguities")
        
        # Print sample data
        if document.definitions:
            logger.info("\nSample definitions:")
            for i, definition in enumerate(document.definitions[:2]):
                logger.info(f"{i+1}. {definition.term}: {definition.definition[:100]}...")
        
        return {
            "title": document.title,
            "standard_type": document.standard_type,
            "standard_number": document.standard_number,
            "definitions_count": len(document.definitions),
            "accounting_treatments_count": len(document.accounting_treatments),
            "transaction_structures_count": len(document.transaction_structures),
            "ambiguities_count": len(document.ambiguities)
        }
        
    except Exception as e:
        logger.error(f"Error testing document processing: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise

def test_enhancement_generation(standard_id: str, use_mock: bool = True, max_count: int = 2):
    """Test enhancement generation functionality"""
    logger.info(f"Testing enhancement generation for standard ID: {standard_id}")
    
    try:
        # Use mock knowledge graph if requested
        if use_mock:
            use_mock_knowledge_graph()
        
        # Initialize components
        kg = KnowledgeGraph()
        enhancement_agent = EnhancementAgent(kg)
        
        # Generate enhancements (limited to max_count for testing)
        all_proposals = enhancement_agent.generate_enhancements(standard_id)
        proposals = all_proposals[:max_count]
        
        # Log results
        logger.info(f"Generated {len(proposals)} enhancement proposals")
        
        for i, proposal in enumerate(proposals):
            logger.info(f"Proposal {i+1}: {proposal.enhancement_type}")
            logger.info(f"  Target: {proposal.target_id}")
            logger.info(f"  Original: {proposal.original_content[:50]}...")
            logger.info(f"  Enhanced: {proposal.enhanced_content[:50]}...")
        
        return {
            "standard_id": standard_id,
            "proposals_count": len(proposals),
            "proposals": [
                {
                    "enhancement_type": p.enhancement_type,
                    "target_id": p.target_id,
                }
                for p in proposals
            ]
        }
        
    except Exception as e:
        logger.error(f"Error testing enhancement generation: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise

def test_validation(proposal_id: str, use_mock: bool = True):
    """Test validation functionality"""
    logger.info(f"Testing validation for proposal ID: {proposal_id}")
    
    try:
        # Use mock knowledge graph if requested
        if use_mock:
            use_mock_knowledge_graph()
        
        # Initialize components
        kg = KnowledgeGraph()
        validation_agent = ValidationAgent(kg)
        
        # Validate proposal
        result = validation_agent.validate_proposal(proposal_id)
        
        # Log results
        logger.info(f"Validation result: {result.status.value}")
        logger.info(f"Overall score: {result.overall_score:.2f}")
        logger.info(f"Feedback: {result.feedback[:100]}...")
        
        if result.modified_content:
            logger.info(f"Modified content: {result.modified_content[:100]}...")
        
        return {
            "proposal_id": proposal_id,
            "status": result.status.value,
            "overall_score": result.overall_score,
            "has_feedback": bool(result.feedback),
            "has_modified_content": bool(result.modified_content)
        }
        
    except Exception as e:
        logger.error(f"Error testing validation: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise

def test_full_workflow(file_path: str, use_mock: bool = True):
    """Test the full workflow from document processing to validation"""
    logger.info(f"Testing full workflow with file: {file_path}")
    
    try:
        # Use mock knowledge graph if requested
        if use_mock:
            use_mock_knowledge_graph()
        
        # Initialize components
        kg = KnowledgeGraph()
        document_agent = DocumentAgent(kg)
        enhancement_agent = EnhancementAgent(kg)
        validation_agent = ValidationAgent(kg)
        
        # Step 1: Process document
        logger.info("Step 1: Processing document")
        document = document_agent.process_document(file_path)
        
        # Get the standard ID
        standards = kg.search_nodes(
            label="Standard",
            properties={
                "title": document.title
            }
        )
        
        if not standards:
            raise ValueError(f"Standard not found in knowledge graph: {document.title}")
        
        standard_id = standards[0]["id"]
        
        # Step 2: Generate enhancements (limit to 2 for testing)
        logger.info(f"Step 2: Generating enhancements for standard ID: {standard_id}")
        all_proposals = enhancement_agent.generate_enhancements(standard_id)
        proposals = all_proposals[:2]
        
        if not proposals:
            logger.warning("No enhancement proposals generated")
            return {
                "document": document.title,
                "standard_id": standard_id,
                "proposals": [],
                "validations": []
            }
        
        # Get proposal IDs
        proposal_ids = []
        for proposal in proposals:
            # Search for the proposal
            found_proposals = kg.search_nodes(
                label="EnhancementProposal",
                properties={
                    "standard_id": standard_id,
                    "enhancement_type": proposal.enhancement_type
                }
            )
            
            if found_proposals:
                proposal_ids.append(found_proposals[0]["id"])
        
        # Step 3: Validate proposals
        logger.info(f"Step 3: Validating {len(proposal_ids)} proposals")
        validation_results = []
        
        for proposal_id in proposal_ids:
            validation_result = validation_agent.validate_proposal(proposal_id)
            validation_results.append(validation_result)
        
        # Log results
        logger.info("Workflow completed successfully")
        logger.info(f"Processed document: {document.title}")
        logger.info(f"Generated {len(proposals)} enhancement proposals")
        logger.info(f"Validated {len(validation_results)} proposals")
        
        return {
            "document": document.title,
            "standard_id": standard_id,
            "proposals_count": len(proposals),
            "validations_count": len(validation_results),
            "validation_statuses": [r.status.value for r in validation_results]
        }
        
    except Exception as e:
        logger.error(f"Error testing full workflow: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test components of the Islamic Finance Standards AI system")
    parser.add_argument("--component", choices=["document", "enhancement", "validation", "workflow"], 
                        required=True, help="Component to test")
    parser.add_argument("--file", help="Path to document file (for document processing and workflow tests)")
    parser.add_argument("--standard-id", help="Standard ID (for enhancement generation test)")
    parser.add_argument("--proposal-id", help="Proposal ID (for validation test)")
    parser.add_argument("--use-mock", action="store_true", default=True, 
                        help="Use mock knowledge graph instead of Neo4j")
    
    args = parser.parse_args()
    
    if args.component == "document":
        if not args.file:
            print("Error: --file is required for document testing")
            sys.exit(1)
        test_document_processing(args.file, args.use_mock)
        
    elif args.component == "enhancement":
        if not args.standard_id:
            print("Error: --standard-id is required for enhancement testing")
            sys.exit(1)
        test_enhancement_generation(args.standard_id, args.use_mock)
        
    elif args.component == "validation":
        if not args.proposal_id:
            print("Error: --proposal-id is required for validation testing")
            sys.exit(1)
        test_validation(args.proposal_id, args.use_mock)
        
    elif args.component == "workflow":
        if not args.file:
            print("Error: --file is required for workflow testing")
            sys.exit(1)
        test_full_workflow(args.file, args.use_mock)
