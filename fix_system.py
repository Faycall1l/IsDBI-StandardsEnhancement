#!/usr/bin/env python3

import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to the system_integrator.py file
file_path = 'IslamicFinanceStandardsAI/integration/system_integrator.py'

# Create a backup
backup_path = file_path + '.backup_' + str(os.getpid())
os.system(f"cp {file_path} {backup_path}")
logger.info(f"Created backup at {backup_path}")

# Read the file content
with open(file_path, 'r') as f:
    lines = f.readlines()

# Fix the duplicate method definition
fixed_lines = []
skip_next = False
for i, line in enumerate(lines):
    if skip_next:
        skip_next = False
        continue
    
    # Check for duplicate method definition
    if i < len(lines) - 1 and line.strip().startswith('def update_proposal_status') and lines[i+1].strip().startswith('def update_proposal_status'):
        fixed_lines.append(line)
        skip_next = True
        logger.info(f"Found and fixed duplicate method definition at line {i+1}")
    else:
        fixed_lines.append(line)

# Write the fixed content back to the file
with open(file_path, 'w') as f:
    f.writelines(fixed_lines)

logger.info("Fixed the duplicate method definition in system_integrator.py")

# Now fix the generate_enhancement method
with open(file_path, 'r') as f:
    content = f.read()

# Find the generate_enhancement method
start_index = content.find('def generate_enhancement')
if start_index == -1:
    logger.error("Could not find generate_enhancement method")
    sys.exit(1)

# Find the end of the method
end_index = content.find('def validate_enhancement', start_index)
if end_index == -1:
    logger.error("Could not find the end of generate_enhancement method")
    sys.exit(1)

# Extract the method
method = content[start_index:end_index]

# Replace the method with a fixed version
fixed_method = '''def generate_enhancement(self, standard_id, standard_text, use_web_search=True):
        """Generate an enhancement for a standard"""
        self.logger.info(f"Generating enhancement for standard: {standard_id}")
        
        # Get standard from database if it exists
        standard = self.shared_db.get_standard_by_id(standard_id)
        if not standard and not standard_text:
            self.logger.error(f"Standard not found: {standard_id}")
            return {"success": False, "message": "Standard not found"}
        
        # Use enhancement generator to generate enhancement
        enhancement_result = self.enhancement_generator.generate_enhancement(
            standard_id, standard_text, use_web_search
        )
        
        # Create a proposal ID
        proposal_id = f"prop-{standard_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Save enhancement to database
        try:
            self.shared_db.create_enhancement_proposal({
                "id": proposal_id,
                "standard_id": standard_id,
                "title": enhancement_result.get("title", f"Enhancement Proposal for {standard_id}"),
                "description": enhancement_result.get("description", ""),
                "proposed_text": enhancement_result.get("proposed_text", ""),
                "rationale": enhancement_result.get("rationale", ""),
                "status": "pending_validation",
                "created_at": datetime.now().isoformat()
            })
            
            # Save to file system
            enhancement_result["id"] = proposal_id
            enhancement_result["standard_id"] = standard_id
            self.file_manager.save_enhancement_proposal(proposal_id, enhancement_result)
            
            # Add proposal ID to result
            enhancement_result["proposal_id"] = proposal_id
            
            # Publish event
            self.event_bus.publish(
                "enhancements",
                EventType.ENHANCEMENT_GENERATED,
                {
                    "standard_id": standard_id,
                    "enhancement_id": proposal_id,
                    "enhancement_data": enhancement_result
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error saving enhancement: {e}")
        
        return enhancement_result
'''

# Replace the method
fixed_content = content[:start_index] + fixed_method + content[end_index:]

# Write the fixed content back to the file
with open(file_path, 'w') as f:
    f.write(fixed_content)

logger.info("Fixed the generate_enhancement method in system_integrator.py")
logger.info("All fixes applied successfully")
