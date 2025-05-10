def _enhance_accounting_treatments(self, standard_info: Dict, treatment_nodes: List[Dict]) -> List[EnhancementProposal]:
    """Generate enhancements for accounting treatments"""
    enhancements = []
    
    for treatment in treatment_nodes:
        # Prepare context for the LLM
        context = {
            "standard_title": standard_info["properties"]["title"],
            "standard_type": standard_info["properties"]["standard_type"],
            "standard_number": standard_info["properties"]["standard_number"],
            "treatment_title": treatment["properties"]["title"],
            "treatment_description": treatment["properties"]["description"]
        }
        
        # Generate enhancement using LLM
        enhancement = self._generate_enhancement_with_llm(
            enhancement_type="ACCOUNTING_TREATMENT",
            context=context,
            prompt_template="""
            You are an expert in Islamic finance and accounting standards. 
            
            CONTEXT:
            Standard: {standard_title} ({standard_type} {standard_number})
            Accounting Treatment: {treatment_title}
            Current Description: {treatment_description}
            
            TASK:
            Analyze the current accounting treatment and propose enhancements that:
            1. Improve clarity and precision
            2. Address potential implementation challenges
            3. Ensure Shariah compliance
            4. Align with international accounting best practices where applicable
            
            Provide:
            1. Enhanced accounting treatment description
            2. A detailed explanation of your changes and their benefits
            3. References to Islamic finance principles and accounting standards that support your enhancement
            """
        )
        
        if enhancement:
            proposal = EnhancementProposal(
                standard_id=standard_info["id"],
                enhancement_type="ACCOUNTING_TREATMENT",
                target_id=treatment["id"],
                original_content=treatment["properties"]["description"],
                enhanced_content=enhancement["content"],
                reasoning=enhancement["reasoning"],
                references=enhancement["references"],
                status="PROPOSED"
            )
            enhancements.append(proposal)
    
    return enhancements
