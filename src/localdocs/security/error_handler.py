"""
Error Handler Module
====================
Safe error handling that doesn't leak sensitive information
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Union
import logging
import traceback

logger = logging.getLogger(__name__)

class SafeErrorHandler:
    """Handles errors safely without leaking sensitive data."""
    
    # Don't expose these in error messages
    SENSITIVE_PATTERNS = [
        'password',
        'api_key',
        'secret',
        'token',
        'credential',
    ]
    
    def __init__(self):
        pass
    
    def sanitize_error_message(self, message: str) -> str:
        """Remove sensitive information from error messages."""
        if not message:
            return "Internal error"
        
        # Lowercase for checking
        lower_msg = message.lower()
        
        # Check for sensitive patterns
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in lower_msg:
                return "Internal error"
        
        # Remove file paths
        message = message.replace('/data/', '')
        message = message.replace('/home/', '')
        message = message.replace('\\', '/')
        
        # Truncate long messages
        if len(message) > 200:
            message = message[:200] + "..."
        
        return message
    
    def handle_exception(self, request: Request, exception: Exception) -> JSONResponse:
        """
        Handle any exception safely.
        
        Args:
            request: FastAPI request
            exception: Exception object
            
        Returns:
            Safe JSON response
        """
        # Log full error for debugging
        logger.error(f"Error on {request.url}: {str(exception)}")
        logger.error(traceback.format_exc())
        
        # Handle HTTPException
        if isinstance(exception, HTTPException):
            return JSONResponse(
                status_code=exception.status_code,
                content={
                    "error": exception.detail if exception.status_code < 500 else "Request failed",
                    "status": exception.status_code
                }
            )
        
        # Handle all other exceptions safely
        safe_message = self.sanitize_error_message(str(exception))
        
        return JSONResponse(
            status_code=500,
            content={
                "error": safe_message,
                "status": 500
            }
        )

# Global error handler
_error_handler = SafeErrorHandler()

def get_error_handler() -> SafeErrorHandler:
    """Get error handler instance."""
    return _error_handler

# Exception handler decorator
async def safe_exception_handler(request: Request, exception: Exception):
    """FastAPI exception handler."""
    return _error_handler.handle_exception(request, exception)
