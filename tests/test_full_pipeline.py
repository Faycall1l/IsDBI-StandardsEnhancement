#!/usr/bin/env python3
"""
Full Pipeline Test for Islamic Finance Standards Enhancement System

This test simulates a complete workflow:
1. Detecting a news article about Islamic finance
2. Parsing and extracting relevant information
3. Identifying related FAS standards
4. Generating enhancement proposals
5. Validating the proposals
6. Flagging ambiguous content
"""
import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from IslamicFinanceStandardsAI.core.agents.agent_manager import AgentManager
from IslamicFinanceStandardsAI.core.agents.agent_factory import AgentFactory
from IslamicFinanceStandardsAI.core.agents.base_agent import AgentMessage
from IslamicFinanceStandardsAI.database.factory import create_knowledge_graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Sample news article about Islamic finance
SAMPLE_NEWS = {
    "title": "Central Bank Issues New Guidelines on Murabaha Transactions",
    "source": "Financial Times",
    "date": "2025-05-17",
    "url": "https://example.com/news/islamic-finance/murabaha-guidelines",
    "content": """
    The Central Bank has issued new guidelines on Murabaha transactions to address 
    growing concerns about transparency and disclosure requirements. The guidelines 
    emphasize that Islamic financial institutions must clearly disclose all costs 
    and profit margins to clients before finalizing Murabaha contracts.
    
    Industry experts note that this addresses a gap in current practices where some 
    institutions have been criticized for inadequate disclosure of markup rates and 
    associated fees. The new guidelines specifically require:
    
    1. Detailed breakdown of the asset's original cost
    2. Clear disclosure of the markup rate and calculation method
    3. Separation of genuine costs from profit margins
    4. Documentation of all stages of the transaction
    
    The guidelines will take effect in three months, giving institutions time to 
    update their processes and documentation. Non-compliance may result in penalties.
    
    Some scholars have questioned whether the current FAS 28 standard on Murabaha 
    adequately addresses these transparency concerns, suggesting that accounting 
    standards may need to be enhanced to align with these regulatory developments.
    """
}

class TestFullPipeline:
    """Test the full pipeline of the Islamic Finance Standards Enhancement System"""
    
    def __init__(self):
        """Initialize the test"""
        self.agent_manager = None
        self.knowledge_graph = None
        self.test_results = {
            "search_results": None,
            "verification_results": None,
            "content_analysis": None,
            "credibility_assessment": None,
            "consensus_results": None,
            "related_standards": None,
            "enhancement_proposals": None,
            "validation_results": None,
            "ambiguities_flagged": None
        }
    
    async def setup(self):
        """Set up the test environment"""
        logger.info("Setting up test environment...")
        
        # Initialize knowledge graph
        self.knowledge_graph = create_knowledge_graph()
        await self.knowledge_graph.connect()
        
        # Initialize agent manager
        self.agent_manager = AgentManager()
        await self.agent_manager.initialize()
        
        logger.info("Test environment set up successfully")
    
    async def teardown(self):
        """Clean up after the test"""
        logger.info("Cleaning up test environment...")
        
        if self.agent_manager:
            await self.agent_manager.shutdown()
        
        if self.knowledge_graph:
            await self.knowledge_graph.close()
        
        logger.info("Test environment cleaned up successfully")
    
    async def run_test(self):
        """Run the full pipeline test"""
        try:
            await self.setup()
            
            logger.info("Starting full pipeline test...")
            
            # Step 1: Simulate news detection and search
            await self.simulate_news_detection()
            
            # Step 2: Verify the information across sources
            await self.verify_information()
            
            # Step 3: Analyze content and extract key information
            await self.analyze_content()
            
            # Step 4: Assess credibility of the source
            await self.assess_credibility()
            
            # Step 5: Build consensus from multiple sources
            await self.build_consensus()
            
            # Step 6: Identify related FAS standards
            await self.identify_related_standards()
            
            # Step 7: Generate enhancement proposals
            await self.generate_enhancements()
            
            # Step 8: Validate the proposals
            await self.validate_proposals()
            
            # Step 9: Flag ambiguities
            await self.flag_ambiguities()
            
            # Output results
            self.output_results()
            
            logger.info("Full pipeline test completed successfully")
            
        except Exception as e:
            logger.error(f"Error running test: {str(e)}", exc_info=True)
        finally:
            await self.teardown()
    
    async def simulate_news_detection(self):
        """Simulate detecting a news article online"""
        logger.info("Step 1: Simulating news detection...")
        
        # Create a message for the search specialist agent
        message = AgentMessage(
            message_type="search_news",
            payload={
                "news_article": SAMPLE_NEWS,
                "search_parameters": {
                    "topics": ["Islamic finance", "Murabaha", "regulations"],
                    "date_range": "last_week",
                    "sources": ["reputable_financial_news"]
                }
            }
        )
        
        # Send the message to the search specialist agent
        response = await self.agent_manager.send_message("document_agent_1", message)
        
        if response.success:
            self.test_results["search_results"] = response.data
            logger.info("News detection simulation successful")
        else:
            logger.error(f"News detection failed: {response.error}")
    
    async def verify_information(self):
        """Verify the information across multiple sources"""
        logger.info("Step 2: Verifying information across sources...")
        
        # Skip if previous step failed
        if not self.test_results["search_results"]:
            logger.warning("Skipping verification step as search results are missing")
            return
        
        # Create a message for the verification specialist agent
        message = AgentMessage(
            message_type="verify_information",
            payload={
                "primary_source": self.test_results["search_results"],
                "verification_parameters": {
                    "min_sources_required": 3,
                    "credibility_threshold": 0.7,
                    "cross_check_methods": ["content_matching", "source_reliability"]
                }
            }
        )
        
        # Send the message to the verification specialist agent
        response = await self.agent_manager.send_message("document_agent_2", message)
        
        if response.success:
            self.test_results["verification_results"] = response.data
            logger.info("Information verification successful")
        else:
            logger.error(f"Information verification failed: {response.error}")
    
    async def analyze_content(self):
        """Analyze content and extract key information"""
        logger.info("Step 3: Analyzing content...")
        
        # Create a message for the content analyzer agent
        message = AgentMessage(
            message_type="analyze_content",
            payload={
                "news_article": SAMPLE_NEWS,
                "analysis_parameters": {
                    "extract_entities": True,
                    "identify_key_points": True,
                    "summarize": True
                }
            }
        )
        
        # Send the message to the content analyzer agent
        response = await self.agent_manager.send_message("document_agent_3", message)
        
        if response.success:
            self.test_results["content_analysis"] = response.data
            logger.info("Content analysis successful")
        else:
            logger.error(f"Content analysis failed: {response.error}")
    
    async def assess_credibility(self):
        """Assess the credibility of the source"""
        logger.info("Step 4: Assessing credibility...")
        
        # Create a message for the credibility assessor agent
        message = AgentMessage(
            message_type="assess_credibility",
            payload={
                "source": SAMPLE_NEWS["source"],
                "content": SAMPLE_NEWS["content"],
                "assessment_parameters": {
                    "check_source_history": True,
                    "evaluate_bias": True,
                    "expert_verification": True
                }
            }
        )
        
        # Send the message to the credibility assessor agent
        response = await self.agent_manager.send_message("document_agent_4", message)
        
        if response.success:
            self.test_results["credibility_assessment"] = response.data
            logger.info("Credibility assessment successful")
        else:
            logger.error(f"Credibility assessment failed: {response.error}")
    
    async def build_consensus(self):
        """Build consensus from multiple sources"""
        logger.info("Step 5: Building consensus...")
        
        # Create a message for the consensus builder agent
        message = AgentMessage(
            message_type="build_consensus",
            payload={
                "verification_results": self.test_results.get("verification_results", {}),
                "content_analysis": self.test_results.get("content_analysis", {}),
                "credibility_assessment": self.test_results.get("credibility_assessment", {}),
                "consensus_parameters": {
                    "confidence_threshold": 0.8,
                    "resolution_strategy": "weighted_majority"
                }
            }
        )
        
        # Send the message to the consensus builder agent
        response = await self.agent_manager.send_message("document_agent_5", message)
        
        if response.success:
            self.test_results["consensus_results"] = response.data
            logger.info("Consensus building successful")
        else:
            logger.error(f"Consensus building failed: {response.error}")
    
    async def identify_related_standards(self):
        """Identify related FAS standards"""
        logger.info("Step 6: Identifying related FAS standards...")
        
        # Skip if consensus results are missing
        if not self.test_results["consensus_results"]:
            logger.warning("Skipping standards identification as consensus results are missing")
            return
        
        # Create a message for the enhancement agent
        message = AgentMessage(
            message_type="identify_standards",
            payload={
                "consensus_results": self.test_results["consensus_results"],
                "search_parameters": {
                    "standard_types": ["FAS"],
                    "topics": ["Murabaha", "disclosure", "transparency"]
                }
            }
        )
        
        # Send the message to the enhancement agent
        response = await self.agent_manager.send_message("enhancement_agent_1", message)
        
        if response.success:
            self.test_results["related_standards"] = response.data
            logger.info("Standards identification successful")
        else:
            logger.error(f"Standards identification failed: {response.error}")
    
    async def generate_enhancements(self):
        """Generate enhancement proposals"""
        logger.info("Step 7: Generating enhancement proposals...")
        
        # Skip if related standards are missing
        if not self.test_results["related_standards"]:
            logger.warning("Skipping enhancement generation as related standards are missing")
            return
        
        # Create a message for the enhancement agent
        message = AgentMessage(
            message_type="generate_enhancements",
            payload={
                "related_standards": self.test_results["related_standards"],
                "consensus_results": self.test_results["consensus_results"],
                "enhancement_parameters": {
                    "focus_areas": ["transparency", "disclosure", "documentation"],
                    "max_proposals": 5
                }
            }
        )
        
        # Send the message to the enhancement agent
        response = await self.agent_manager.send_message("enhancement_agent_2", message)
        
        if response.success:
            self.test_results["enhancement_proposals"] = response.data
            logger.info("Enhancement generation successful")
        else:
            logger.error(f"Enhancement generation failed: {response.error}")
    
    async def validate_proposals(self):
        """Validate the enhancement proposals"""
        logger.info("Step 8: Validating enhancement proposals...")
        
        # Skip if enhancement proposals are missing
        if not self.test_results["enhancement_proposals"]:
            logger.warning("Skipping validation as enhancement proposals are missing")
            return
        
        # Create a message for the validation agent
        message = AgentMessage(
            message_type="validate_proposals",
            payload={
                "enhancement_proposals": self.test_results["enhancement_proposals"],
                "validation_parameters": {
                    "validation_criteria": [
                        "compliance_with_sharia",
                        "practical_implementation",
                        "regulatory_alignment",
                        "industry_impact"
                    ],
                    "provide_reasoning": True
                }
            }
        )
        
        # Send the message to the validation agent
        response = await self.agent_manager.send_message("validation_agent_1", message)
        
        if response.success:
            self.test_results["validation_results"] = response.data
            logger.info("Proposal validation successful")
        else:
            logger.error(f"Proposal validation failed: {response.error}")
    
    async def flag_ambiguities(self):
        """Flag ambiguous content"""
        logger.info("Step 9: Flagging ambiguities...")
        
        # Skip if validation results are missing
        if not self.test_results["validation_results"]:
            logger.warning("Skipping ambiguity flagging as validation results are missing")
            return
        
        # Create a message for the validation agent
        message = AgentMessage(
            message_type="flag_ambiguities",
            payload={
                "validation_results": self.test_results["validation_results"],
                "flagging_parameters": {
                    "ambiguity_threshold": 0.7,
                    "categorize_ambiguities": True
                }
            }
        )
        
        # Send the message to the validation agent
        response = await self.agent_manager.send_message("validation_agent_2", message)
        
        if response.success:
            self.test_results["ambiguities_flagged"] = response.data
            logger.info("Ambiguity flagging successful")
        else:
            logger.error(f"Ambiguity flagging failed: {response.error}")
    
    def output_results(self):
        """Output the test results"""
        logger.info("Test Results Summary:")
        
        # Format the results for better readability
        formatted_results = json.dumps(self.test_results, indent=2)
        
        # Save results to file
        with open("test_results.json", "w") as f:
            f.write(formatted_results)
        
        logger.info(f"Test results saved to test_results.json")
        
        # Print key findings
        if self.test_results["enhancement_proposals"]:
            logger.info("\nKey Enhancement Proposals:")
            for i, proposal in enumerate(self.test_results["enhancement_proposals"].get("proposals", [])):
                logger.info(f"  {i+1}. {proposal.get('title', 'Unnamed proposal')}")
        
        if self.test_results["validation_results"]:
            logger.info("\nValidation Summary:")
            validation_summary = self.test_results["validation_results"].get("summary", {})
            logger.info(f"  Accepted: {validation_summary.get('accepted', 0)}")
            logger.info(f"  Rejected: {validation_summary.get('rejected', 0)}")
            logger.info(f"  Needs revision: {validation_summary.get('needs_revision', 0)}")
        
        if self.test_results["ambiguities_flagged"]:
            logger.info("\nAmbiguities Flagged:")
            for i, ambiguity in enumerate(self.test_results["ambiguities_flagged"].get("ambiguities", [])):
                logger.info(f"  {i+1}. {ambiguity.get('description', 'Unnamed ambiguity')}")

async def main():
    """Run the test"""
    test = TestFullPipeline()
    await test.run_test()

if __name__ == "__main__":
    asyncio.run(main())
