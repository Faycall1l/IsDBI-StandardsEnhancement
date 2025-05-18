#!/usr/bin/env python
"""
Test script for the multi-agent pipeline in the Islamic Finance Standards Enhancement System.
This script demonstrates a complete test case for enhancing the FAS 7 (Salam) definition.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

# Import the agent factory and other necessary components
from IslamicFinanceStandardsAI.core.agents.agent_factory import AgentFactory
from IslamicFinanceStandardsAI.core.agents.document_agent import DocumentAgent
from IslamicFinanceStandardsAI.core.agents.enhancement_agent import EnhancementAgent
from IslamicFinanceStandardsAI.core.agents.validation_agent import ValidationAgent
from IslamicFinanceStandardsAI.database.factory import create_knowledge_graph
from IslamicFinanceStandardsAI.database.interfaces.knowledge_graph import IKnowledgeGraph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_full_pipeline():
    """
    Run a complete test of the multi-agent pipeline for enhancing the FAS 7 (Salam) definition.
    """
    logger.info("Starting multi-agent pipeline test for FAS 7 (Salam) enhancement")
    
    # Initialize knowledge graph
    knowledge_graph = create_knowledge_graph()
    await knowledge_graph.connect()
    
    # Create agent instances
    factory = AgentFactory()
    document_agent = factory.create_agent('document_agent', agent_id='doc_agent_1')
    enhancement_agent = factory.create_agent('enhancement_agent', agent_id='enh_agent_1')
    validation_agent = factory.create_agent('validation_agent', agent_id='val_agent_1')
    
    # Start all agents
    await document_agent.start()
    await enhancement_agent.start()
    await validation_agent.start()
    
    # Step 1: Document Processing
    logger.info("STEP 1: Document Agent processing FAS 7 (Salam) standard")
    document_path = "data/standards/FAS7_Salam/FAS7_Salam.txt"
    
    document_result = await document_agent.process_document(
        document_path=document_path,
        document_type="fas_7",
        extract_sections=True,
        identify_ambiguities=True
    )
    
    logger.info(f"Document processing result: {document_result.success}")
    if document_result.success:
        logger.info(f"Extracted {len(document_result.data.get('sections', []))} sections")
        logger.info(f"Identified {len(document_result.data.get('ambiguities', []))} ambiguities")
        
        # Print the first ambiguity found (if any)
        ambiguities = document_result.data.get('ambiguities', [])
        if ambiguities:
            logger.info(f"Sample ambiguity: {ambiguities[0]}")
    
    # Step 2: Enhancement Generation
    logger.info("STEP 2: Enhancement Agent generating proposal for Salam definition")
    
    # Target the Salam definition section specifically
    target_section = "1.2 Definition"
    
    enhancement_result = await enhancement_agent.generate_enhancement(
        standard_id="FAS7",
        section_id=target_section,
        enhancement_category="clarity",
        context={
            "ambiguities": document_result.data.get('ambiguities', []),
            "related_standards": ["FAS28"]  # Murabaha is related to Salam
        }
    )
    
    logger.info(f"Enhancement generation result: {enhancement_result.success}")
    if enhancement_result.success:
        proposal = enhancement_result.data.get('proposal', {})
        logger.info(f"Enhancement proposal: {proposal.get('title')}")
        logger.info(f"Current text: {proposal.get('current_text')}")
        logger.info(f"Proposed text: {proposal.get('proposed_text')}")
        logger.info(f"Rationale: {proposal.get('rationale')}")
    
    # Step 3: Validation
    logger.info("STEP 3: Validation Agent evaluating the enhancement proposal")
    
    validation_result = await validation_agent.validate_enhancement(
        proposal_id=enhancement_result.data.get('proposal', {}).get('id'),
        validation_criteria={
            "shariah_compliance": True,
            "aaoifi_alignment": True,
            "practical_implementation": True,
            "clarity_improvement": True
        }
    )
    
    logger.info(f"Validation result: {validation_result.success}")
    if validation_result.success:
        validation_data = validation_result.data
        logger.info(f"Overall score: {validation_data.get('overall_score')}/10")
        logger.info(f"Shariah compliance: {validation_data.get('shariah_compliance_score')}/10")
        logger.info(f"AAOIFI alignment: {validation_data.get('aaoifi_alignment_score')}/10")
        logger.info(f"Practical implementation: {validation_data.get('practical_implementation_score')}/10")
        logger.info(f"Clarity improvement: {validation_data.get('clarity_improvement_score')}/10")
        logger.info(f"Recommendation: {validation_data.get('recommendation')}")
        logger.info(f"Feedback: {validation_data.get('feedback')}")
    
    # Step 4: Store the validated proposal in the knowledge graph
    if validation_result.success and validation_result.data.get('recommendation') == 'approve':
        logger.info("STEP 4: Storing approved proposal in knowledge graph")
        
        # Create a simplified data structure for Neo4j storage
        proposal_data = {
            'id': enhancement_result.data.get('proposal', {}).get('id'),
            'title': enhancement_result.data.get('proposal', {}).get('title'),
            'standard_id': enhancement_result.data.get('proposal', {}).get('standard_id'),
            'section_id': enhancement_result.data.get('proposal', {}).get('section_id'),
            'category': enhancement_result.data.get('proposal', {}).get('category'),
            'status': 'approved',
            'timestamp': datetime.now().isoformat(),
            'current_text': enhancement_result.data.get('proposal', {}).get('current_text'),
            'proposed_text': enhancement_result.data.get('proposal', {}).get('proposed_text'),
            'rationale': enhancement_result.data.get('proposal', {}).get('rationale'),
            'validation_score': validation_result.data.get('overall_score'),
            'validation_recommendation': validation_result.data.get('recommendation'),
            'validation_feedback': validation_result.data.get('feedback')
        }
        
        try:
            store_result = await knowledge_graph.create_enhancement_proposal(proposal_data)
            logger.info(f"Proposal storage result: {store_result}")
        except Exception as e:
            logger.error(f"Error storing proposal: {str(e)}")
            logger.info("Continuing with test without storage...")
            store_result = None
    
    # Clean up
    await document_agent.stop()
    await enhancement_agent.stop()
    await validation_agent.stop()
    await knowledge_graph.close()
    
    logger.info("Multi-agent pipeline test completed")
    
    # Return the complete test results
    return {
        "document_processing": document_result.data if document_result.success else None,
        "enhancement_proposal": enhancement_result.data if enhancement_result.success else None,
        "validation_result": validation_result.data if validation_result.success else None
    }

if __name__ == "__main__":
    # Run the test
    test_results = asyncio.run(test_full_pipeline())
    
    # Print final summary
    print("\n" + "="*80)
    print("MULTI-AGENT PIPELINE TEST SUMMARY")
    print("="*80)
    
    if test_results["document_processing"]:
        print("\nDocument Processing:")
        print(f"- Sections extracted: {len(test_results['document_processing'].get('sections', []))}")
        print(f"- Ambiguities identified: {len(test_results['document_processing'].get('ambiguities', []))}")
    
    if test_results["enhancement_proposal"]:
        proposal = test_results["enhancement_proposal"].get('proposal', {})
        print("\nEnhancement Proposal:")
        print(f"- Title: {proposal.get('title')}")
        print(f"- Current text: {proposal.get('current_text')}")
        print(f"- Proposed text: {proposal.get('proposed_text')}")
        print(f"- Rationale: {proposal.get('rationale')}")
    
    if test_results["validation_result"]:
        print("\nValidation Results:")
        print(f"- Overall score: {test_results['validation_result'].get('overall_score')}/10")
        print(f"- Recommendation: {test_results['validation_result'].get('recommendation')}")
        print(f"- Feedback: {test_results['validation_result'].get('feedback')}")
    
    print("\nTest completed successfully!")
