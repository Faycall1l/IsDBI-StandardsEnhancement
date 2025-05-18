#!/usr/bin/env python3
"""
Run Frontend Script for Islamic Finance Standards Enhancement System

This script runs the Flask frontend application with the enhanced dashboard, proposal bank,
and news monitoring features.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import the Flask app
from IslamicFinanceStandardsAI.frontend.app import app

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 5004))
    
    # Run the app in debug mode
    app.run(host="0.0.0.0", port=port, debug=True)
