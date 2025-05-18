#!/usr/bin/env python3
"""
Trigger Pipeline Script

This script simulates a change in Islamic finance data that triggers
the entire agent pipeline, from search to validation and storage.
"""
import os
import sys
import asyncio
import logging
import json
import uuid
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Mock data change that would trigger the system
MOCK_TRIGGER = {
    "source": "AAOIFI Website",
    "type": "regulatory_update",
    "title": "Updated Guidance on Murabaha Transactions",
    "content": "AAOIFI has released updated guidance on Murabaha transactions, emphasizing enhanced disclosure requirements for financial institutions.",
    "url": "https://aaoifi.com/announcements/2025/05/updated-murabaha-guidance",
    "timestamp": "2025-05-17T15:30:00Z",
    "relevance": {
        "standards": ["FAS28"],
        "topics": ["disclosure", "transparency", "markup_calculation"]
    }
}

async def trigger_pipeline():
    """Trigger the entire agent pipeline with a mock data change"""
    from IslamicFinanceStandardsAI.core.agents.agent_manager import AgentManager
    from IslamicFinanceStandardsAI.core.agents.base_agent import AgentMessage
    from IslamicFinanceStandardsAI.core.agents.team_config import get_team_members
    from IslamicFinanceStandardsAI.database.factory import create_knowledge_graph
    
    # Connect to Neo4j
    kg = create_knowledge_graph()
    await kg.connect()
    logger.info("Connected to Neo4j")
    
    # Initialize agent manager
    agent_manager = AgentManager()
    await agent_manager.initialize()
    logger.info("Agent manager initialized")
    
    try:
        # STEP 1: Store the trigger in Neo4j
        logger.info("Storing trigger in Neo4j...")
        with kg.driver.session() as session:
            query = """
            CREATE (t:Trigger {
                id: $id,
                source: $source,
                type: $type,
                title: $title,
                content: $content,
                url: $url,
                timestamp: $timestamp,
                processed: false
            })
            RETURN t.id as id
            """
            result = session.run(
                query,
                id=str(uuid.uuid4()),
                source=MOCK_TRIGGER["source"],
                type=MOCK_TRIGGER["type"],
                title=MOCK_TRIGGER["title"],
                content=MOCK_TRIGGER["content"],
                url=MOCK_TRIGGER["url"],
                timestamp=MOCK_TRIGGER["timestamp"]
            )
            trigger_id = result.single()["id"]
            logger.info(f"Trigger stored with ID: {trigger_id}")
        
        # STEP 2: Notify search agents
        logger.info("Notifying search agents...")
        document_team = get_team_members("document_team")
        search_agent_id = None
        
        # Find search specialist
        for agent_id in document_team:
            if "search" in agent_id:
                search_agent_id = agent_id
                break
        
        if not search_agent_id:
            search_agent_id = document_team[0]
        
        # Send message to search agent
        search_message = AgentMessage(
            message_type="process_document",
            payload={
                "trigger_id": trigger_id,
                "document_type": MOCK_TRIGGER["type"],
                "content": MOCK_TRIGGER["content"],
                "url": MOCK_TRIGGER["url"]
            }
        )
        
        search_response = await agent_manager.send_message(search_agent_id, search_message)
        
        if not search_response.success:
            logger.error(f"Search agent failed: {search_response.error}")
            return
        
        document_id = search_response.data.get("document_id")
        logger.info(f"Document processed with ID: {document_id}")
        
        # STEP 3: Trigger enhancement agents
        logger.info("Triggering enhancement agents...")
        enhancement_team = get_team_members("enhancement_team")
        enhancement_agent_id = enhancement_team[0]
        
        # Send message to enhancement agent
        enhancement_message = AgentMessage(
            message_type="analyze_standard",
            payload={
                "standard_id": "FAS28",
                "document_id": document_id,
                "focus_areas": MOCK_TRIGGER["relevance"]["topics"]
            }
        )
        
        enhancement_response = await agent_manager.send_message(enhancement_agent_id, enhancement_message)
        
        if not enhancement_response.success:
            logger.error(f"Enhancement agent failed: {enhancement_response.error}")
            return
        
        opportunities = enhancement_response.data.get("analysis", {}).get("enhancement_opportunities", [])
        logger.info(f"Found {len(opportunities)} enhancement opportunities")
        
        # STEP 4: Generate proposals for each opportunity
        proposals = []
        for opportunity in opportunities[:2]:  # Limit to 2 for brevity
            opportunity_id = opportunity.get("id")
            logger.info(f"Generating proposal for opportunity {opportunity_id}")
            
            proposal_message = AgentMessage(
                message_type="generate_proposal",
                payload={
                    "standard_id": "FAS28",
                    "opportunity_id": opportunity_id
                }
            )
            
            proposal_response = await agent_manager.send_message(enhancement_agent_id, proposal_message)
            
            if not proposal_response.success:
                logger.error(f"Proposal generation failed: {proposal_response.error}")
                continue
            
            proposal_id = proposal_response.data.get("proposal_id")
            proposals.append(proposal_id)
            logger.info(f"Generated proposal with ID: {proposal_id}")
        
        # STEP 5: Validate proposals
        validation_team = get_team_members("validation_team")
        validation_agent_id = validation_team[0]
        
        validation_results = {"approved": [], "rejected": [], "ambiguous": []}
        
        for proposal_id in proposals:
            logger.info(f"Validating proposal {proposal_id}")
            
            validation_message = AgentMessage(
                message_type="validate_proposal",
                payload={
                    "proposal_id": proposal_id,
                    "validation_criteria": ["shariah_compliance", "accounting_standards"]
                }
            )
            
            validation_response = await agent_manager.send_message(validation_agent_id, validation_message)
            
            if not validation_response.success:
                logger.error(f"Validation failed: {validation_response.error}")
                continue
            
            validation_id = validation_response.data.get("validation_id")
            status = validation_response.data.get("validation_result", {}).get("overall_status")
            
            if status == "approved":
                validation_results["approved"].append(proposal_id)
            elif status == "rejected":
                validation_results["rejected"].append(proposal_id)
            else:
                validation_results["ambiguous"].append(proposal_id)
            
            logger.info(f"Validation completed with ID: {validation_id}, Status: {status}")
        
        # STEP 6: Record approved proposals in blockchain
        blockchain_team = get_team_members("blockchain_team")
        blockchain_agent_id = blockchain_team[0]
        
        for proposal_id in validation_results["approved"]:
            logger.info(f"Recording approved proposal {proposal_id} in blockchain")
            
            blockchain_message = AgentMessage(
                message_type="record_version",
                payload={
                    "proposal_id": proposal_id,
                    "standard_id": "FAS28",
                    "version": "1.1"
                }
            )
            
            blockchain_response = await agent_manager.send_message(blockchain_agent_id, blockchain_message)
            
            if not blockchain_response.success:
                logger.error(f"Blockchain recording failed: {blockchain_response.error}")
                continue
            
            version_id = blockchain_response.data.get("version_record", {}).get("version_id")
            logger.info(f"Recorded in blockchain with version ID: {version_id}")
        
        # STEP 7: Store results in Neo4j
        logger.info("Storing final results in Neo4j...")
        with kg.driver.session() as session:
            query = """
            CREATE (r:PipelineResult {
                id: $id,
                trigger_id: $trigger_id,
                timestamp: $timestamp,
                approved_count: $approved_count,
                rejected_count: $rejected_count,
                ambiguous_count: $ambiguous_count,
                approved_proposals: $approved_proposals,
                rejected_proposals: $rejected_proposals,
                ambiguous_proposals: $ambiguous_proposals
            })
            RETURN r.id as id
            """
            result = session.run(
                query,
                id=str(uuid.uuid4()),
                trigger_id=trigger_id,
                timestamp=datetime.utcnow().isoformat(),
                approved_count=len(validation_results["approved"]),
                rejected_count=len(validation_results["rejected"]),
                ambiguous_count=len(validation_results["ambiguous"]),
                approved_proposals=json.dumps(validation_results["approved"]),
                rejected_proposals=json.dumps(validation_results["rejected"]),
                ambiguous_proposals=json.dumps(validation_results["ambiguous"])
            )
            result_id = result.single()["id"]
            logger.info(f"Pipeline results stored with ID: {result_id}")
        
        # Print summary
        print("\n=== PIPELINE EXECUTION SUMMARY ===")
        print(f"Trigger: {MOCK_TRIGGER['title']}")
        print(f"Document ID: {document_id}")
        print(f"Enhancement Opportunities: {len(opportunities)}")
        print(f"Proposals Generated: {len(proposals)}")
        print(f"Validation Results:")
        print(f"  - Approved: {len(validation_results['approved'])}")
        print(f"  - Rejected: {len(validation_results['rejected'])}")
        print(f"  - Ambiguous: {len(validation_results['ambiguous'])}")
        print("================================\n")
        
        # Provide Neo4j query to view results
        print("To view results in Neo4j Browser (http://localhost:7474), run:")
        print("MATCH (r:PipelineResult) RETURN r ORDER BY r.timestamp DESC LIMIT 1")
        
    finally:
        # Clean up
        await agent_manager.shutdown()
        await kg.close()
        logger.info("Resources cleaned up")

if __name__ == "__main__":
    asyncio.run(trigger_pipeline())
