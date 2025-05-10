"""
Document Ingestion and Parsing Agent

This agent is responsible for:
1. Reading and extracting key elements from AAOIFI standards
2. Identifying critical definitions, accounting treatments, and transaction structures
3. Feeding extracted data into the Knowledge Graph
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
import PyPDF2
import docx
import spacy
from transformers import pipeline
import logging

from database.knowledge_graph import KnowledgeGraph
from utils.document_parser import PDFParser, DOCXParser, TextParser
from models.document_schema import StandardDocument, Definition, AccountingTreatment, TransactionStructure

class DocumentAgent:
    """Agent for ingesting and parsing AAOIFI standards documents"""
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        """
        Initialize the Document Agent
        
        Args:
            knowledge_graph: The knowledge graph instance for storing extracted data
        """
        self.knowledge_graph = knowledge_graph
        self.logger = logging.getLogger(__name__)
        
        # Load NLP models
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except:
            self.logger.warning("Downloading Spacy model...")
            os.system("python -m spacy download en_core_web_lg")
            self.nlp = spacy.load("en_core_web_lg")
        
        self.ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")
        
        # Initialize parsers
        self.parsers = {
            "pdf": PDFParser(),
            "docx": DOCXParser(),
            "txt": TextParser()
        }
    
    def process_document(self, file_path: str) -> StandardDocument:
        """
        Process a document and extract structured information
        
        Args:
            file_path: Path to the document file
            
        Returns:
            StandardDocument object containing extracted information
        """
        self.logger.info(f"Processing document: {file_path}")
        
        # Determine file type and use appropriate parser
        file_extension = file_path.split('.')[-1].lower()
        if file_extension in self.parsers:
            parser = self.parsers[file_extension]
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Extract raw text
        raw_text = parser.extract_text(file_path)
        
        # Extract document metadata
        metadata = self._extract_metadata(raw_text, file_path)
        
        # Extract key elements
        definitions = self._extract_definitions(raw_text)
        accounting_treatments = self._extract_accounting_treatments(raw_text)
        transaction_structures = self._extract_transaction_structures(raw_text)
        ambiguities = self._identify_ambiguities(raw_text)
        
        # Create structured document
        document = StandardDocument(
            title=metadata.get("title", ""),
            standard_type=metadata.get("standard_type", ""),
            standard_number=metadata.get("standard_number", ""),
            publication_date=metadata.get("publication_date", ""),
            definitions=definitions,
            accounting_treatments=accounting_treatments,
            transaction_structures=transaction_structures,
            ambiguities=ambiguities,
            raw_text=raw_text
        )
        
        # Store in knowledge graph
        self._store_in_knowledge_graph(document)
        
        return document
    
    def _extract_metadata(self, text: str, file_path: str) -> Dict[str, str]:
        """Extract metadata from document text using regex patterns"""
        import re
        filename = os.path.basename(file_path)
        
        metadata = {
            "title": "",
            "standard_type": "",
            "standard_number": "",
            "publication_date": ""
        }
        
        # Extract title from the first few lines of text
        title_match = re.search(r'(?i)(financial accounting standard|shariah standard|fas|ss)[\s\n]*(no\.|number)?[\s\n]*(\()?\s*([0-9]+)', text[:1000])
        if title_match:
            standard_text = title_match.group(1).strip()
            number_text = title_match.group(4).strip() if title_match.group(4) else ""
            
            # Determine standard type
            if re.search(r'(?i)financial accounting standard|fas', standard_text):
                metadata["standard_type"] = "FAS"
            elif re.search(r'(?i)shariah standard|ss', standard_text):
                metadata["standard_type"] = "SS"
            
            # Set standard number
            metadata["standard_number"] = number_text
            
            # Extract title - look for the main subject after the standard number
            subject_match = re.search(r'(?i)(financial accounting standard|shariah standard|fas|ss)[\s\n]*(no\.|number)?[\s\n]*(\()?\s*([0-9]+)(\))?[\s\n]*(.*?)(?=\n\n|$)', text[:1000])
            if subject_match and subject_match.group(6):
                subject = subject_match.group(6).strip()
                if subject:
                    metadata["title"] = f"{metadata['standard_type']} {metadata['standard_number']}: {subject}"
                else:
                    metadata["title"] = f"{metadata['standard_type']} {metadata['standard_number']}"
        
        # If we couldn't extract from text, try from filename
        # Set title if not already determined
        if not metadata["title"]:
            # Try to extract from filename
            file_match = re.search(r'(?i)(fas|ss|fi)[\s_-]*(\d+)', filename)
            if file_match:
                std_type = file_match.group(1).upper()
                std_number = file_match.group(2)
                
                if std_type == "FI" or std_type == "FAS":
                    metadata["standard_type"] = "FAS"
                elif std_type == "SS":
                    metadata["standard_type"] = "SS"
                
                metadata["standard_number"] = std_number
                
                # Extract subject from filename
                subject_match = re.search(r'(?i)(fas|ss|fi)[\s_-]*(\d+)[\s_-]*(.*?)\.(pdf|PDF)', filename)
                if subject_match and subject_match.group(3):
                    subject = subject_match.group(3).replace('_', ' ').strip()
                    metadata["title"] = f"{metadata['standard_type']} {metadata['standard_number']}: {subject}"
                else:
                    metadata["title"] = f"{metadata['standard_type']} {metadata['standard_number']}"
            
            # If still no title, use the first line of text as title, limited to 100 characters
            if not metadata["title"]:
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        metadata["title"] = line[:100]
                        break
        
        return metadata
    
    def _extract_definitions(self, text: str) -> List[Definition]:
        """Extract key definitions from text"""
        definitions = []
        
        # Look for definition sections
        definition_section = self._extract_section(text, ["definitions", "terminology", "terms used"])
        
        if definition_section:
            # Process the definition section to extract individual definitions
            doc = self.nlp(definition_section)
            
            current_term = ""
            current_definition = ""
            
            for para in definition_section.split('\n\n'):
                if not para.strip():
                    continue
                    
                # Check if paragraph starts with a term-like pattern
                if len(para.split(':')) > 1 or len(para.split(' - ')) > 1:
                    # Save previous definition if exists
                    if current_term and current_definition:
                        definitions.append(Definition(
                            term=current_term.strip(),
                            definition=current_definition.strip(),
                            source_text=f"{current_term}: {current_definition}"
                        ))
                    
                    # Start new definition
                    if ':' in para:
                        parts = para.split(':', 1)
                        current_term = parts[0]
                        current_definition = parts[1]
                    else:
                        parts = para.split(' - ', 1)
                        current_term = parts[0]
                        current_definition = parts[1]
                else:
                    # Continue previous definition
                    current_definition += " " + para
        
            # Add the last definition
            if current_term and current_definition:
                definitions.append(Definition(
                    term=current_term.strip(),
                    definition=current_definition.strip(),
                    source_text=f"{current_term}: {current_definition}"
                ))
        
        return definitions
    
    def _extract_accounting_treatments(self, text: str) -> List[AccountingTreatment]:
        """Extract accounting treatments from text"""
        treatments = []
        
        # Look for accounting treatment sections
        treatment_section = self._extract_section(text, ["accounting treatment", "recognition", "measurement", "disclosure"])
        
        if treatment_section:
            # Split into paragraphs and process
            paragraphs = treatment_section.split('\n\n')
            
            current_title = ""
            current_description = ""
            
            for i, para in enumerate(paragraphs):
                if not para.strip():
                    continue
                
                # Check if this looks like a heading
                if len(para) < 100 and (para.isupper() or para.endswith(':')):
                    # Save previous treatment if exists
                    if current_title and current_description:
                        treatments.append(AccountingTreatment(
                            title=current_title.strip(),
                            description=current_description.strip(),
                            source_text=f"{current_title}\n{current_description}"
                        ))
                    
                    # Start new treatment
                    current_title = para
                    current_description = ""
                else:
                    # Continue previous treatment description
                    if current_title:
                        current_description += " " + para
                    else:
                        # If no title yet, this might be the first treatment
                        current_title = "General Accounting Treatment"
                        current_description = para
            
            # Add the last treatment
            if current_title and current_description:
                treatments.append(AccountingTreatment(
                    title=current_title.strip(),
                    description=current_description.strip(),
                    source_text=f"{current_title}\n{current_description}"
                ))
        
        return treatments
    
    def _extract_transaction_structures(self, text: str) -> List[TransactionStructure]:
        """Extract transaction structures from text"""
        structures = []
        
        # Look for transaction structure sections
        structure_section = self._extract_section(text, ["transaction structure", "structure of", "steps of", "procedure"])
        
        if structure_section:
            # Process to find numbered steps or bullet points
            lines = structure_section.split('\n')
            
            current_structure = {
                "title": "",
                "steps": [],
                "description": ""
            }
            
            in_steps = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line looks like a heading
                if len(line) < 100 and (line.isupper() or line.endswith(':')):
                    # Save previous structure if exists
                    if current_structure["title"] and (current_structure["steps"] or current_structure["description"]):
                        structures.append(TransactionStructure(
                            title=current_structure["title"].strip(),
                            steps=current_structure["steps"],
                            description=current_structure["description"].strip(),
                            source_text=structure_section
                        ))
                    
                    # Start new structure
                    current_structure = {
                        "title": line,
                        "steps": [],
                        "description": ""
                    }
                    in_steps = False
                
                # Check if line looks like a step (starts with number or bullet)
                elif line[0].isdigit() or line[0] in ['•', '-', '*']:
                    in_steps = True
                    current_structure["steps"].append(line)
                
                # Otherwise, it's part of the description
                else:
                    if in_steps:
                        # If we were in steps and now we're not, it might be a continuation of the last step
                        if current_structure["steps"]:
                            current_structure["steps"][-1] += " " + line
                    else:
                        current_structure["description"] += " " + line
            
            # Add the last structure
            if current_structure["title"] and (current_structure["steps"] or current_structure["description"]):
                structures.append(TransactionStructure(
                    title=current_structure["title"].strip(),
                    steps=current_structure["steps"],
                    description=current_structure["description"].strip(),
                    source_text=structure_section
                ))
        
        return structures
    
    def _identify_ambiguities(self, text: str) -> List[Dict[str, str]]:
        """Identify potential ambiguities in the text"""
        ambiguities = []
        
        # Look for phrases indicating ambiguity
        ambiguity_indicators = [
            "may be", "could be", "might be", "is not clear", "ambiguous",
            "depending on", "in some cases", "not specified", "not defined",
            "at the discretion of", "as appropriate", "as applicable"
        ]
        
        # Process text in chunks to handle large documents
        chunk_size = 5000
        overlap = 200
        
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            doc = self.nlp(chunk)
            
            for sent in doc.sents:
                for indicator in ambiguity_indicators:
                    if indicator in sent.text.lower():
                        # Find the paragraph containing this sentence
                        para_start = max(0, chunk.rfind('\n\n', 0, sent.start_char))
                        para_end = chunk.find('\n\n', sent.end_char)
                        if para_end == -1:
                            para_end = len(chunk)
                        
                        paragraph = chunk[para_start:para_end].strip()
                        
                        ambiguities.append({
                            "text": sent.text,
                            "context": paragraph,
                            "indicator": indicator
                        })
                        break
        
        return ambiguities
    
    def _extract_section(self, text: str, section_indicators: List[str]) -> str:
        """
        Extract a section from text based on section indicators
        
        Args:
            text: The full document text
            section_indicators: List of phrases that might indicate the start of the section
            
        Returns:
            The extracted section text, or empty string if not found
        """
        lines = text.split('\n')
        section_text = ""
        in_section = False
        section_indent = 0
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check if this line indicates the start of our target section
            if not in_section:
                for indicator in section_indicators:
                    if indicator.lower() in line_lower:
                        in_section = True
                        section_text = line + "\n"
                        # Calculate indentation level
                        section_indent = len(line) - len(line.lstrip())
                        break
            
            # If we're in the section, keep adding lines until we hit another section
            elif in_section:
                # Check if this is a new section header (less or equal indentation)
                if line.strip() and len(line) - len(line.lstrip()) <= section_indent:
                    # This might be a new section header, check if it's long enough
                    if len(line.strip()) < 100:  # Typical section headers aren't very long
                        # Look ahead to see if this is followed by content
                        if i + 1 < len(lines) and lines[i + 1].strip():
                            # This is likely a new section, so we're done
                            break
                
                # Still in our section, add the line
                section_text += line + "\n"
        
        return section_text
    
    def _store_in_knowledge_graph(self, document: StandardDocument) -> None:
        """Store the extracted document information in the knowledge graph"""
        self.logger.info(f"Storing document in knowledge graph: {document.title}")
        
        # Convert to dictionary for storage
        doc_dict = document.dict()
        
        # Store the document node
        doc_node_id = self.knowledge_graph.create_node(
            label="Standard",
            properties={
                "title": document.title,
                "standard_type": document.standard_type,
                "standard_number": document.standard_number,
                "publication_date": document.publication_date
            }
        )
        
        # Store definitions and link to document
        for definition in document.definitions:
            def_node_id = self.knowledge_graph.create_node(
                label="Definition",
                properties={
                    "term": definition.term,
                    "definition": definition.definition
                }
            )
            self.knowledge_graph.create_relationship(
                start_node_id=doc_node_id,
                end_node_id=def_node_id,
                relationship_type="HAS_DEFINITION"
            )
        
        # Store accounting treatments and link to document
        for treatment in document.accounting_treatments:
            treatment_node_id = self.knowledge_graph.create_node(
                label="AccountingTreatment",
                properties={
                    "title": treatment.title,
                    "description": treatment.description
                }
            )
            self.knowledge_graph.create_relationship(
                start_node_id=doc_node_id,
                end_node_id=treatment_node_id,
                relationship_type="HAS_ACCOUNTING_TREATMENT"
            )
        
        # Store transaction structures and link to document
        for structure in document.transaction_structures:
            structure_node_id = self.knowledge_graph.create_node(
                label="TransactionStructure",
                properties={
                    "title": structure.title,
                    "description": structure.description,
                    "steps": json.dumps(structure.steps)
                }
            )
            self.knowledge_graph.create_relationship(
                start_node_id=doc_node_id,
                end_node_id=structure_node_id,
                relationship_type="HAS_TRANSACTION_STRUCTURE"
            )
        
        # Store ambiguities and link to document
        for i, ambiguity in enumerate(document.ambiguities):
            ambiguity_node_id = self.knowledge_graph.create_node(
                label="Ambiguity",
                properties={
                    "text": ambiguity["text"],
                    "context": ambiguity["context"],
                    "indicator": ambiguity["indicator"]
                }
            )
            self.knowledge_graph.create_relationship(
                start_node_id=doc_node_id,
                end_node_id=ambiguity_node_id,
                relationship_type="HAS_AMBIGUITY"
            )
        
        self.logger.info(f"Successfully stored document in knowledge graph")
