"""
Document Parser Utilities

This module provides parsers for different document formats (PDF, DOCX, TXT).
"""

import os
import logging
from typing import Dict, List, Any, Optional
import PyPDF2
import docx
import re


class BaseParser:
    """Base class for document parsers"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a document
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text as a string
        """
        raise NotImplementedError("Subclasses must implement extract_text method")


class PDFParser(BaseParser):
    """Parser for PDF documents"""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from a PDF document"""
        self.logger.info(f"Extracting text from PDF: {file_path}")
        
        try:
            text = ""
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
                
                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
            
            # Clean up the text
            text = self._clean_text(text)
            
            return text
            
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {str(e)}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """Clean up extracted PDF text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common PDF extraction issues
        text = text.replace('- ', '')  # Remove hyphenation
        
        # Split into paragraphs
        paragraphs = []
        for line in text.split('\n'):
            line = line.strip()
            if line:
                paragraphs.append(line)
        
        return '\n\n'.join(paragraphs)


class DOCXParser(BaseParser):
    """Parser for DOCX documents"""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from a DOCX document"""
        self.logger.info(f"Extracting text from DOCX: {file_path}")
        
        try:
            doc = docx.Document(file_path)
            text = ""
            
            for para in doc.paragraphs:
                if para.text.strip():
                    text += para.text.strip() + "\n\n"
            
            return text
            
        except Exception as e:
            self.logger.error(f"Error extracting text from DOCX: {str(e)}")
            return ""


class TextParser(BaseParser):
    """Parser for plain text documents"""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from a plain text document"""
        self.logger.info(f"Extracting text from text file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            return text
            
        except Exception as e:
            self.logger.error(f"Error extracting text from text file: {str(e)}")
            return ""
