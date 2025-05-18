import random
from typing import List
from src.common.models import StandardDocument

def generate_synthetic_standard_document() -> StandardDocument:
    """Generates a single synthetic StandardDocument."""
    
    standard_types = ["FAS", "GS", "SS"] # Financial Accounting, General, Shariah
    standard_number = random.randint(1, 50)
    
    topics = {
        "FAS": [
            ("Murabaha", "Covers accounting for Murabaha sales, including profit recognition and disclosure requirements for deferred sales."),
            ("Ijarah", "Details accounting treatment for Ijarah and Ijarah Muntahia Bittamleek, focusing on lessor and lessee perspectives."),
            ("Istisna'a", "Outlines revenue and cost recognition for Istisna'a contracts, particularly for long-term manufacturing projects."),
            ("Sukuk", "Specifies the accounting and reporting standards for various types of Sukuk (Islamic bonds)."),
            ("Takaful", "Addresses accounting principles for Takaful (Islamic insurance) operations, including participant and operator funds.")
        ],
        "GS": [
            ("Corporate Governance", "Provides guidelines for ethical corporate governance in Islamic Financial Institutions (IFIs)."),
            ("Shariah Supervisory Board", "Sets standards for the appointment, composition, and reporting of Shariah Supervisory Boards."),
            ("Risk Management", "Outlines principles for risk management in IFIs, covering credit, market, and operational risks.")
        ],
        "SS": [
            ("Zakat", "Details the calculation and distribution of Zakat by IFIs."),
            ("Waqf", "Provides Shariah rulings and guidance on the management and development of Waqf (endowment) properties."),
            ("Qard Hasan", "Specifies the principles governing benevolent loans (Qard Hasan).")
        ]
    }
    
    selected_type = random.choice(standard_types)
    selected_topic, topic_description = random.choice(topics[selected_type])
    
    title = f"{selected_type} No. {standard_number} - {selected_topic}"
    source_standard = f"{selected_type} {standard_number}"
    
    content_intro = f"This standard, {title}, addresses key aspects of {selected_topic.lower()} within Islamic finance. "
    content_body = topic_description
    content_focus = f" It particularly focuses on ensuring compliance with Shariah principles while providing clear guidance for practitioners."
    full_content = content_intro + content_body + content_focus

    possible_ambiguities = [
        f"Lack of clarity on the application of {selected_topic} in digital/fintech contexts.",
        "Guidance needed for cross-border transaction complexities related to this standard.",
        "Insufficient detail on disclosure requirements for complex instruments under this standard.",
        "Potential conflict with certain local regulatory interpretations.",
        "Ambiguity in defining 'significant influence' or 'control' for related party transactions under this standard.",
        "Need for more illustrative examples for practical application.",
        "Harmonization challenges with international non-Islamic accounting standards."
    ]
    
    num_ambiguities = random.randint(0, 2)
    identified_ambiguities = random.sample(possible_ambiguities, num_ambiguities)
    
    return StandardDocument(
        title=title,
        source_standard=source_standard,
        content=full_content,
        identified_ambiguities=identified_ambiguities
    )

if __name__ == '__main__':
    # Example of generating a few synthetic documents
    for i in range(3):
        doc = generate_synthetic_standard_document()
        print(f"--- Synthetic Document {i+1} ---")
        print(f"ID: {doc.id}")
        print(f"Title: {doc.title}")
        print(f"Source: {doc.source_standard}")
        print(f"Content: {doc.content[:150]}...") # Print snippet
        print(f"Ambiguities: {doc.identified_ambiguities}")
        print("-" * 30)
