import pytest
import os
from unittest.mock import AsyncMock

# Conditional import for OpenAI
try:
    from langchain_openai import ChatOpenAI
    OPENAI_API_KEY_AVAILABLE = bool(os.environ.get("OPENAI_API_KEY"))
except ImportError:
    OPENAI_API_KEY_AVAILABLE = False

from src.enhancement_agent.enhancer import EnhancementAgent
from src.common.models import StandardDocument, EnhancementProposal

# Skip all tests in this module if OpenAI API key is not available
pytestmark = pytest.mark.skipif(not OPENAI_API_KEY_AVAILABLE, reason="OPENAI_API_KEY not set or langchain-openai not installed")

@pytest.fixture
def llm_service():
    if OPENAI_API_KEY_AVAILABLE:
        # You can specify model_name, temperature, etc. as needed
        return ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
    return None # Should be skipped by pytestmark if we reach here without key

@pytest.fixture
def sample_fas_4_document():
    return StandardDocument(
        id="fas4-doc1",
        title="Financial Accounting Standard No. 4",
        source_standard="FAS 4",
        content="This standard deals with Murabaha transactions. It requires clear disclosure of cost and profit margin.",
        identified_ambiguities=["Lack of clarity on deferred payment sales.", "Guidance needed for profit recognition over time."]
    )

@pytest.fixture
def sample_fas_10_document():
    return StandardDocument(
        id="fas10-doc1",
        title="Financial Accounting Standard No. 10",
        source_standard="FAS 10",
        content="This standard addresses Istisna'a contracts. It outlines recognition criteria for Istisna'a revenue and costs.",
        identified_ambiguities=["Complexities in percentage of completion method for long-term contracts."]
    )

@pytest.fixture
def sample_fas_32_document():
    return StandardDocument(
        id="fas32-doc1",
        title="Financial Accounting Standard No. 32",
        source_standard="FAS 32",
        content="This standard covers Ijarah and Ijarah Muntahia Bittamleek. It specifies accounting for lessors and lessees.",
        identified_ambiguities=[] # No ambiguities identified for this test case
    )

@pytest.mark.asyncio
async def test_generate_proposal_fas4(sample_fas_4_document, llm_service):
    if not llm_service: # Should be caught by pytestmark, but as a safeguard
        pytest.skip("OpenAI LLM service not available.")

    agent = EnhancementAgent(llm=llm_service)
    
    proposal = await agent.generate_proposal(sample_fas_4_document)

    assert isinstance(proposal, EnhancementProposal)
    assert proposal.original_standard_id == sample_fas_4_document.id
    assert proposal.original_standard_title == sample_fas_4_document.title
    
    # For real LLM, assertions need to be more flexible
    assert "Proposed Enhancement Text:" in proposal.proposed_enhancement_text or proposal.proposed_enhancement_text # Check if not empty
    assert "Chain-of-Thought Reasoning:" in proposal.chain_of_thought_reasoning or proposal.chain_of_thought_reasoning # Check if not empty
    
    # More specific checks can be added if consistent patterns are expected
    # For example, checking if the source standard (FAS 4) is mentioned in reasoning.
    assert "FAS 4" in proposal.chain_of_thought_reasoning or "Murabaha" in proposal.chain_of_thought_reasoning
    assert proposal.status == "generated"
    print(f"\nFAS4 Proposal:\n{proposal.proposed_enhancement_text}\nReasoning:\n{proposal.chain_of_thought_reasoning}")

@pytest.mark.asyncio
async def test_generate_proposal_fas10_with_ambiguities(sample_fas_10_document, llm_service):
    if not llm_service:
        pytest.skip("OpenAI LLM service not available.")
        
    agent = EnhancementAgent(llm=llm_service)
    
    proposal = await agent.generate_proposal(sample_fas_10_document)

    assert isinstance(proposal, EnhancementProposal)
    assert proposal.original_standard_id == sample_fas_10_document.id
    assert "FAS 10" in proposal.chain_of_thought_reasoning or "Istisna'a" in proposal.chain_of_thought_reasoning
    print(f"\nFAS10 Proposal:\n{proposal.proposed_enhancement_text}\nReasoning:\n{proposal.chain_of_thought_reasoning}")

@pytest.mark.asyncio
async def test_generate_proposal_fas32_no_ambiguities(sample_fas_32_document, llm_service):
    if not llm_service:
        pytest.skip("OpenAI LLM service not available.")

    agent = EnhancementAgent(llm=llm_service)

    proposal = await agent.generate_proposal(sample_fas_32_document)

    assert isinstance(proposal, EnhancementProposal)
    assert "FAS 32" in proposal.chain_of_thought_reasoning or "Ijarah" in proposal.chain_of_thought_reasoning
    print(f"\nFAS32 Proposal:\n{proposal.proposed_enhancement_text}\nReasoning:\n{proposal.chain_of_thought_reasoning}")
