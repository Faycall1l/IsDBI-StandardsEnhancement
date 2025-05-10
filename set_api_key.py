#!/usr/bin/env python
"""
API Key Setup Script for Islamic Finance Standards Enhancement System

This script prompts the user for their OpenAI API key and saves it to the .env file.
The API key is required for the enhancement generation and validation components.
"""

import os
import sys
from dotenv import load_dotenv, set_key

# Path to .env file
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')

# Create .env file if it doesn't exist
if not os.path.exists(env_path):
    with open(env_path, 'w') as f:
        f.write('# Environment variables for Islamic Finance Standards Enhancement System\n')

# Prompt for API key
print("\nIslamic Finance Standards Enhancement System - API Key Setup")
print("==========================================================\n")
print("This system uses OpenAI's API for enhancement generation and validation.")
print("You'll need to provide your OpenAI API key to proceed.\n")

api_key = input("Enter your OpenAI API key: ").strip()

if not api_key:
    print("\nError: API key cannot be empty. Please run this script again with a valid API key.")
    sys.exit(1)

# Set the API key
set_key(env_path, "OPENAI_API_KEY", api_key)

# Set default model
set_key(env_path, "OPENAI_MODEL", "gpt-4")

print(f"\nSuccessfully set OPENAI_API_KEY in {env_path}")
print("The API key will be loaded automatically when running the application.")
print("\nNote: Keep your API key secure and never share it with others.")
