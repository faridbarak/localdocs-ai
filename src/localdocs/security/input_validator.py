"""
Input Validation Module
=======================
Validates incoming requests to prevent malformed data attacks
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException
import re
import logging

logger = logging.getLogger(__name__)

class InputValidator:
    """Validates incoming request inputs."""
    
    MAX_PROMPT_LENGTH = 10000
    MAX_FILE_NAME_LENGTH = 255
    MAX_QUERY_LENGTH = 5000
    
    ALLOWED_FILE_EXTENSIONS = {'pdf', 'txt', 'md', 'doc', 'docx', 'csv', 'json'}
    
    DANGEROUS_PATTERNS = [
        r'<\s*script',
        r'<\s*iframe',
        r'<\s*object',
        r'<\s*embed',
        r'javascript:',
        r'vbscript:',
        r'on\w+\s*=',
    ]
    
    def __init__(self):
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.DANGEROUS_PATTERNS]
    
    def validate_prompt(self, prompt: str) -> str:
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        if len(prompt) > self.MAX_PROMPT_LENGTH:
            raise HTTPException(
                status_code=400, 
                detail=f"Prompt too long (max {self.MAX_PROMPT_LENGTH} characters)"
            )
        
        for pattern in self.compiled_patterns:
            if pattern.search(prompt):
                raise HTTPException(
                    status_code=400,
                    detail="Prompt contains dangerous content"
                )
        
        return prompt
    
    def validate_file_name(self, filename: str) -> str:
        if not filename:
            raise HTTPException(status_code=400, detail="File name is required")
        
        if len(filename) > self.MAX_FILE_NAME_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"File name too long (max {self.MAX_FILE_NAME_LENGTH} characters)"
            )
        
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        
        if ext not in self.ALLOWED_FILE_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type '{ext}' not allowed"
            )
        
        dangerous_chars = ['/', ':', '*', '?', '"', '<', '>', '|']
        for char in dangerous_chars:
            if char in filename:
                raise HTTPException(status_code=400, detail="File name contains invalid characters")
        
        return filename
    
    def validate_query(self, query: str) -> str:
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        if len(query) > self.MAX_QUERY_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Query too long (max {self.MAX_QUERY_LENGTH} characters)"
            )
        
        return query
    
    def validate_api_key(self, api_key: str) -> str:
        if not api_key:
            raise HTTPException(status_code=400, detail="API key is required")
        
        if len(api_key) < 8:
            raise HTTPException(status_code=400, detail="API key too short")
        
        if len(api_key) > 128:
            raise HTTPException(status_code=400, detail="API key too long")
        
        return api_key
    
    def sanitize_input(self, text: str) -> str:
        if not text:
            return ""
        
        text = text.strip()
        return text

_validator = None

def get_input_validator() -> InputValidator:
    global _validator
    if _validator is None:
        _validator = InputValidator()
    return _validator

def validate_prompt(prompt: str) -> str:
    validator = get_input_validator()
    return validator.validate_prompt(prompt)

def validate_file_name(filename: str) -> str:
    validator = get_input_validator()
    return validator.validate_file_name(filename)

def validate_query(query: str) -> str:
    validator = get_input_validator()
    return validator.validate_query(query)

def validate_and_sanitize_input(text: str) -> str:
    validator = get_input_validator()
    validator.validate_prompt(text)
    return validator.sanitize_input(text)
