#!/usr/bin/env python3
"""
Extract Enhancement Proposals

This script extracts and displays the enhancement proposals from the event logs.
"""

import os
import sys
import json
import glob
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

__all__ = ['extract_enhancements_from_logs', 'display_enhancements']

def display_enhancements(proposals):
    """Display enhancement proposals in a readable format"""
    if not proposals:
        print("No enhancement proposals found.")
        return
    
    print("\n" + "=" * 80)
    print("ENHANCEMENT PROPOSALS")
    print("=" * 80)
    
    for idx, proposal in enumerate(proposals, 1):
        print(f"\nProposal {idx}:")
        print(f"Standard ID: {proposal.get('standard_id', 'N/A')}")
        print(f"Enhancement Type: {proposal.get('enhancement_type', 'N/A')}")
        print(f"Status: {proposal.get('status', 'N/A')}")
        print("\nOriginal Content:")
        print(proposal.get('original_content', 'N/A'))
        print("\nEnhanced Content:")
        print(proposal.get('enhanced_content', 'N/A'))
        print("\nReasoning:")
        print(proposal.get('reasoning', 'N/A'))
        print("-" * 80)

def extract_enhancements_from_logs():
    """Extract enhancement proposals from event logs"""
    logger.info("Extracting enhancement proposals from event logs")
    
    # Find all event log files
    event_logs = glob.glob("event_log_*.json") + glob.glob("enhancement_event_log_*.json")
    if not event_logs:
        logger.error("No event log files found")
        return []
    
    logger.info(f"Found {len(event_logs)} event log files")
    
    # Extract enhancement proposals from all logs
    all_proposals = []
    
    for log_file in event_logs:
        logger.info(f"Processing log file: {log_file}")
        
        try:
            with open(log_file, "r") as f:
                events = json.load(f)
            
            # Find enhancement proposal events
            for event in events:
                if event.get("topic") == "enhancement-proposed":
                    # Extract proposals from the event data
                    if "proposals" in event.get("data", {}):
                        proposals = event["data"]["proposals"]
                        all_proposals.extend(proposals)
                        logger.info(f"Found {len(proposals)} proposals in event {event['id']}")
                
                # Also check for enhancement proposals in audit logs
                if event.get("event_type") == "ENHANCEMENT_PROPOSED":
                    if "proposals" in event.get("data", {}):
                        proposals = event["data"]["proposals"]
                        all_proposals.extend(proposals)
                        logger.info(f"Found {len(proposals)} proposals in audit event {event['id']}")
        
        except Exception as e:
            logger.error(f"Error processing log file {log_file}: {str(e)}")
    
    if not all_proposals:
        logger.info("No enhancement proposals found in event logs")
        
        # Try to extract from test output logs
        test_logs = glob.glob("multi_agent_workflow_*.log")
        for log_file in test_logs:
            logger.info(f"Searching test log file: {log_file}")
            try:
                with open(log_file, "r") as f:
                    log_content = f.read()
                
                # Look for enhancement proposal sections in the log
                if "ENHANCED CONTENT:" in log_content:
                    logger.info(f"Found enhancement proposals in test log {log_file}")
                    
                    # Extract and display the proposals
                    print("\n" + "=" * 80)
                    print("ENHANCEMENT PROPOSALS FOUND IN TEST LOGS")
                    print("=" * 80 + "\n")
                    
                    # Extract sections between "ENHANCED CONTENT:" and "REASONING:"
                    import re
                    enhanced_content_sections = re.findall(r"ENHANCED CONTENT:(.*?)REASONING:", log_content, re.DOTALL)
                    reasoning_sections = re.findall(r"REASONING:(.*?)REFERENCES:", log_content, re.DOTALL)
                    references_sections = re.findall(r"REFERENCES:(.*?)(?=ANALYSIS:|ENHANCED CONTENT:|$)", log_content, re.DOTALL)
                    
                    for i, content in enumerate(enhanced_content_sections):
                        print(f"PROPOSAL {i+1}")
                        print("-" * 80)
                        print("ENHANCED CONTENT:")
                        print(content.strip())
                        
                        if i < len(reasoning_sections):
                            print("\nREASONING:")
                            print(reasoning_sections[i].strip())
                        
                        if i < len(references_sections):
                            print("\nREFERENCES:")
                            print(references_sections[i].strip())
                        
                        print("\n" + "=" * 80 + "\n")
                    
                    return
            
            except Exception as e:
                logger.error(f"Error processing test log file {log_file}: {str(e)}")
        
        logger.info("No enhancement proposals found in test logs either")
        return
    
    # Display the proposals
    display_enhancements(all_proposals)
    
    # Save to file for easier viewing
    output_file = f"extracted_proposals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(all_proposals, f, indent=2, default=str)
    
    logger.info(f"Extracted proposals saved to {output_file}")
    
    return all_proposals

if __name__ == "__main__":
    extract_enhancements_from_logs()
