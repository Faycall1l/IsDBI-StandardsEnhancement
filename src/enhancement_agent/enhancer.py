from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models import BaseChatModel # For type hinting, actual LLM to be injected

from ..common.models import StandardDocument, EnhancementProposal
import json # For potential structured output parsing if LLM supports it

class EnhancementAgent:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", 
                 "You are an AI assistant specialized in Islamic Finance standards. "
                 "Your task is to propose enhancements to existing standards. "
                 "Provide a clear enhancement proposal and a detailed chain-of-thought reasoning for your proposal. "
                 "Focus on clarity, compliance with Shariah principles, and practical applicability."),
                ("human", 
                 "Standard Title: {standard_title}\n"
                 "Source Standard: {source_standard}\n"
                 "Standard Content Snippet:\n{standard_content}\n\n"
                 "Identified Ambiguities/Areas for Improvement:\n{ambiguities}\n\n"
                 "Based on the above information, please generate an enhancement proposal. "
                 "Structure your response with:\n"
                 "1. Proposed Enhancement Text: [Your proposed text for the enhancement]\n"
                 "2. Chain-of-Thought Reasoning: [Step-by-step reasoning explaining why this enhancement is needed, how it addresses issues, and its benefits, ensuring it aligns with Shariah principles.]")
            ]
        )
        self.output_parser = StrOutputParser()
        self.chain = self.prompt_template | self.llm | self.output_parser

    def _parse_llm_output(self, llm_response: str, original_doc: StandardDocument) -> EnhancementProposal:
        """
        Parses the LLM's string output into an EnhancementProposal object.
        This is a basic parser; more robust parsing might be needed for complex LLM outputs.
        """
        try:
            enhancement_text_marker = "Proposed Enhancement Text:"
            reasoning_marker = "Chain-of-Thought Reasoning:"

            enhancement_start = llm_response.find(enhancement_text_marker)
            reasoning_start = llm_response.find(reasoning_marker)

            if enhancement_start == -1 or reasoning_start == -1:
                # Fallback if markers are not found
                proposed_enhancement = "Could not parse enhancement text from LLM response."
                reasoning = llm_response # Put the whole response as reasoning if parsing fails
            else:
                enhancement_text_start_index = enhancement_start + len(enhancement_text_marker)
                reasoning_text_start_index = reasoning_start + len(reasoning_marker)

                proposed_enhancement = llm_response[enhancement_text_start_index:reasoning_start].strip()
                reasoning = llm_response[reasoning_text_start_index:].strip()
            
            return EnhancementProposal(
                original_standard_id=original_doc.id,
                original_standard_title=original_doc.title,
                proposed_enhancement_text=proposed_enhancement,
                chain_of_thought_reasoning=reasoning,
            )
        except Exception as e:
            # Log error e
            print(f"Error parsing LLM output: {e}") # Replace with proper logging
            return EnhancementProposal(
                original_standard_id=original_doc.id,
                original_standard_title=original_doc.title,
                proposed_enhancement_text="Error: Could not parse LLM output.",
                chain_of_thought_reasoning=f"Parsing error: {str(e)}. Original LLM response: {llm_response}",
            )


    async def generate_proposal(self, document: StandardDocument) -> EnhancementProposal:
        """
        Generates an enhancement proposal for a given standard document.
        """
        ambiguities_str = "\n- ".join(document.identified_ambiguities) if document.identified_ambiguities else "None specified."
        
        llm_response = await self.chain.ainvoke({
            "standard_title": document.title,
            "source_standard": document.source_standard,
            "standard_content": document.content,
            "ambiguities": ambiguities_str
        })
        
        proposal = self._parse_llm_output(llm_response, document)
        return proposal
