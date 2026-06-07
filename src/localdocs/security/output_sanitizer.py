"""
Output Sanitizer Module
=======================
Sanitizes LLM output to prevent XSS attacks
"""

import html
import re
import logging
from typing import Optional
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class OutputSanitizer:
    """Sanitizes output to prevent XSS and injection attacks."""
    
    # Dangerous HTML tags to block
    DANGEROUS_TAGS = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>',
        r'<link[^>]*>',
        r'<style[^>]*>.*?</style>',
    ]
    
    # Dangerous event handlers
    DANGEROUS_EVENTS = [
        r'onclicks*=',
        r'onloads*=',
        r'onerrors*=',
        r'onmouseovers*=',
        r'onfocuss*=',
        r'onblurs*=',
    ]
    
    def __init__(self):
        self.compiled_tags = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in self.DANGEROUS_TAGS]
        self.compiled_events = [re.compile(p, re.IGNORECASE) for p in self.DANGEROUS_EVENTS]
    
    def escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return html.escape(text)
    
    def remove_dangerous_tags(self, text: str) -> str:
        """Remove dangerous HTML tags."""
        sanitized = text
        for pattern in self.compiled_tags:
            sanitized = pattern.sub('[REMOVED]', sanitized)
        return sanitized
    
    def remove_dangerous_events(self, text: str) -> str:
        """Remove dangerous event handlers."""
        sanitized = text
        for pattern in self.compiled_events:
            sanitized = pattern.sub('', sanitized)
        return sanitized
    
    def sanitize(self, text: str, escape_html: bool = True) -> str:
        """
        Fully sanitize output.
        
        Args:
            text: Raw output text
            escape_html: Whether to escape HTML (default True)
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove dangerous tags
        sanitized = self.remove_dangerous_tags(text)
        
        # Remove dangerous events
        sanitized = self.remove_dangerous_events(sanitized)
        
        # Escape HTML if requested
        if escape_html:
            sanitized = self.escape_html(sanitized)
        
        return sanitized
    
    def validate_output(self, text: str, max_length: int = 50000) -> tuple:
        """
        Validate output for safety and length.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text:
            return False, "Output is empty"
        
        if len(text) > max_length:
            return False, f"Output exceeds maximum length of {max_length}"
        
        # Check for dangerous patterns
        for i, pattern in enumerate(self.compiled_tags):
            if pattern.search(text):
                return False, f"Contains dangerous HTML tag"
        
        for i, pattern in enumerate(self.compiled_events):
            if pattern.search(text):
                return False, f"Contains dangerous event handler"
        
        return True, "Output validated successfully"

# Global sanitizer instance
_sanitizer = None

def get_output_sanitizer() -> OutputSanitizer:
    """Get global sanitizer instance."""
    global _sanitizer
    if _sanitizer is None:
        _sanitizer = OutputSanitizer()
    return _sanitizer

def sanitize_output(text: str, escape_html: bool = True) -> str:
    """
    Sanitize output.
    
    Args:
        text: Raw output
        escape_html: Whether to escape HTML
        
    Returns:
        Sanitized text
    """
    sanitizer = get_output_sanitizer()
    return sanitizer.sanitize(text, escape_html)

def validate_and_sanitize_output(text: str) -> str:
    """
    Validate and sanitize output.
    Raises HTTPException if invalid.
    
    Args:
        text: Raw output
        
    Returns:
        Sanitized text
        
    Raises:
        HTTPException: If validation fails
    """
    sanitizer = get_output_sanitizer()
    is_valid, error_msg = sanitizer.validate_output(text)
    
    if not is_valid:
        raise HTTPException(
            status_code=500,
            detail=f"Output validation failed: {error_msg}"
        )
    
    return sanitizer.sanitize(text)
