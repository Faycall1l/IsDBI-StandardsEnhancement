import asyncio
import os
import sys

# Ensure the src directory is in the Python path
# This allows direct execution of cli.py from the project root
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from langchain_openai import ChatOpenAI
    OPENAI_API_KEY_AVAILABLE = bool(os.environ.get("OPENAI_API_KEY"))
except ImportError:
    print("Error: langchain-openai package not found. Please install it by running: pip install langchain-openai")
    OPENAI_API_KEY_AVAILABLE = False
    # sys.exit(1) # Exit if essential package is missing, or handle gracefully

from src.enhancement_agent.enhancer import EnhancementAgent
from src.utils.synthetic_data import generate_synthetic_standard_document
from src.common.models import StandardDocument, EnhancementProposal

async def run_enhancement_simulation():
    """
    Runs a simulation of the enhancement process using synthetic data.
    """
    print("Islamic Finance Standards Enhancement AI - CLI Simulation")
    print("=" * 60)

    if not OPENAI_API_KEY_AVAILABLE:
        print("\nERROR: OPENAI_API_KEY environment variable is not set, or langchain-openai is not installed.")
        print("Please set the API key and ensure the package is installed to use the LLM.")
        print("Example: export OPENAI_API_KEY='your_key_here'")
        return

    print("\nInitializing LLM Service (ChatOpenAI)...")
    try:
        # You can customize model_name, temperature, etc.
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
        print("LLM Service Initialized.")
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        return

    print("\nInitializing Enhancement Agent...")
    agent = EnhancementAgent(llm=llm)
    print("Enhancement Agent Initialized.")

    while True:
        print("\n--- Generating Synthetic Standard Document ---")
        synthetic_doc = generate_synthetic_standard_document()
        
        print(f"\nGenerated Document Details:")
        print(f"  ID: {synthetic_doc.id}")
        print(f"  Title: {synthetic_doc.title}")
        print(f"  Source Standard: {synthetic_doc.source_standard}")
        print(f"  Content Snippet: {synthetic_doc.content[:200]}...")
        if synthetic_doc.identified_ambiguities:
            print(f"  Identified Ambiguities:")