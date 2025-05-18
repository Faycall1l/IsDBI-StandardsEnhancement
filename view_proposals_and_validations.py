#!/usr/bin/env python3
"""
View Proposals and Validations Script

This script connects to the Neo4j database and retrieves the enhancement proposals
and validation results stored there.
"""
import os
import sys
import asyncio
import logging
import json
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Terminal formatting functions
def print_header(title, width=80):
    """Print a formatted header"""
    print("\n" + "=" * width)
    print(f"{title.center(width)}")
    print("=" * width)

def print_subheader(title, width=80):
    """Print a formatted subheader"""
    print("\n" + "-" * width)
    print(f"{title.center(width)}")
    print("-" * width)

def print_json(data, indent=2):
    """Print formatted JSON data"""
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            print(data)
            return
    
    print(json.dumps(data, indent=indent))

async def view_proposals_and_validations():
    """Connect to Neo4j and retrieve proposals and validations"""
    from IslamicFinanceStandardsAI.database.factory import create_knowledge_graph
    
    # Initialize knowledge graph
    kg = create_knowledge_graph()
    await kg.connect()
    logger.info("Connected to Neo4j knowledge graph")
    
    try:
        # Retrieve enhancement proposals
        print_header("ENHANCEMENT PROPOSALS")
        
        # Get enhancement proposals
        proposals = await kg.get_enhancement_proposals()
        
        if not proposals:
            print("No enhancement proposals found in the database.")
        else:
            for i, proposal in enumerate(proposals):
                proposal_data = proposal.get('p', {})
                
                # Extract proposal properties
                proposal_id = proposal_data.get('proposal_id', 'Unknown')
                standard_id = proposal_data.get('standard_id', 'Unknown')
                status = proposal_data.get('status', 'Unknown')
                timestamp = proposal_data.get('timestamp', 'Unknown')
                
                # Get proposal content
                proposal_content = proposal_data.get('proposal', {})
                if isinstance(proposal_content, str):
                    try:
                        proposal_content = json.loads(proposal_content)
                    except json.JSONDecodeError:
                        pass
                
                print_subheader(f"Proposal {i+1}: {proposal_id}")
                print(f"Standard: {standard_id}")
                print(f"Status: {status}")
                print(f"Timestamp: {timestamp}")
                print("\nProposal Content:")
                print_json(proposal_content)
                
                # Get changes
                changes = proposal_content.get('changes', [])
                if changes:
                    print("\nProposed Changes:")
                    for j, change in enumerate(changes):
                        print(f"\n  Change {j+1}:")
                        print(f"  Section: {change.get('section', 'Unknown')}")
                        print(f"  Original: {change.get('original_text', 'Unknown')}")
                        print(f"  Proposed: {change.get('proposed_text', 'Unknown')}")
                        print(f"  Justification: {change.get('justification', 'N/A')}")
        
        # Retrieve validation results
        print_header("VALIDATION RESULTS")
        
        # Get validation results using direct query with session
        validations = []
        with kg.driver.session() as session:
            result = session.run("""
            MATCH (v:ValidationResult)
            RETURN v
            ORDER BY v.timestamp DESC
            LIMIT 10
            """)
            validations = [record for record in result]
        
        if not validations:
            print("No validation results found in the database.")
        else:
            for i, validation in enumerate(validations):
                validation_data = validation.get('v', {})
                
                # Extract validation properties
                validation_id = validation_data.get('validation_id', 'Unknown')
                proposal_id = validation_data.get('proposal_id', 'Unknown')
                status = validation_data.get('status', 'Unknown')
                timestamp = validation_data.get('timestamp', 'Unknown')
                
                # Get validation result content
                validation_result = validation_data.get('validation_result', {})
                if isinstance(validation_result, str):
                    try:
                        validation_result = json.loads(validation_result)
                    except json.JSONDecodeError:
                        pass
                
                print_subheader(f"Validation {i+1}: {validation_id}")
                print(f"Proposal ID: {proposal_id}")
                print(f"Status: {status}")
                print(f"Timestamp: {timestamp}")
                
                if validation_result:
                    print("\nValidation Result:")
                    print(f"  Overall Status: {validation_result.get('overall_status', 'Unknown')}")
                    print(f"  Comments: {validation_result.get('comments', 'N/A')}")
                    
                    # Print compliance scores
                    scores = validation_result.get('compliance_scores', {})
                    if scores:
                        print("\n  Compliance Scores:")
                        for category, score in scores.items():
                            print(f"    {category}: {score}")
                    
                    # Print issues
                    issues = validation_result.get('issues', [])
                    if issues:
                        print("\n  Issues:")
                        for j, issue in enumerate(issues):
                            print(f"\n    Issue {j+1}:")
                            print(f"      Category: {issue.get('category', 'Unknown')}")
                            print(f"      Severity: {issue.get('severity', 'Unknown')}")
                            print(f"      Description: {issue.get('description', 'Unknown')}")
                            print(f"      Recommendation: {issue.get('recommendation', 'N/A')}")
        
        # Retrieve blockchain records
        print_header("BLOCKCHAIN RECORDS")
        
        # Get blockchain records using direct query with session
        blockchain_records = []
        with kg.driver.session() as session:
            result = session.run("""
            MATCH (b:BlockchainRecord)
            RETURN b
            ORDER BY b.timestamp DESC
            LIMIT 10
            """)
            blockchain_records = [record for record in result]
        
        if not blockchain_records:
            print("No blockchain records found in the database.")
        else:
            for i, record in enumerate(blockchain_records):
                record_data = record.get('b', {})
                
                # Extract record properties
                version_id = record_data.get('version_id', 'Unknown')
                standard_id = record_data.get('standard_id', 'Unknown')
                version = record_data.get('version', 'Unknown')
                author = record_data.get('author', 'Unknown')
                timestamp = record_data.get('timestamp', 'Unknown')
                status = record_data.get('status', 'Unknown')
                
                print_subheader(f"Record {i+1}: {version_id}")
                print(f"Standard ID: {standard_id}")
                print(f"Version: {version}")
                print(f"Author: {author}")
                print(f"Status: {status}")
                print(f"Timestamp: {timestamp}")
                
                # Get changes
                changes = record_data.get('changes', [])
                if changes:
                    print("\nRecorded Changes:")
                    for j, change in enumerate(changes):
                        print(f"\n  Change {j+1}:")
                        print(f"  Section: {change.get('section', 'Unknown')}")
                        print(f"  Original: {change.get('original_text', 'Unknown')}")
                        print(f"  New: {change.get('new_text', 'Unknown')}")
    
    finally:
        # Close the connection
        await kg.close()
        logger.info("Disconnected from Neo4j knowledge graph")

async def main():
    """Main function"""
    try:
        await view_proposals_and_validations()
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
