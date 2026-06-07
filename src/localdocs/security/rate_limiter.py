"""
Rate Limiter Module
===================
Prevents API abuse and DoS attacks by limiting request frequency
"""

from typing import Dict
from datetime import datetime
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple rate limiter using token bucket algorithm."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_counts: Dict[str, list] = {}
    
    def is_allowed(self, client_id: str) -> bool:
        """
        Check if client is allowed to make a request.
        
        Args:
            client_id: Unique client identifier (IP address or API key)
            
        Returns:
            True if request is allowed, False if rate limited
        """
        now = datetime.now()
        
        # Initialize client if not seen
        if client_id not in self.request_counts:
            self.request_counts[client_id] = []
        
        # Get requests in current window
        window_start = now - datetime.timedelta(seconds=self.window_seconds)
        recent_requests = [
            ts for ts in self.request_counts[client_id]
            if ts > window_start
        ]
        
        # Check if over limit
        if len(recent_requests) >= self.max_requests:
            logger.warning(f"[RATE_LIMIT] Client {client_id} exceeded {self.max_requests} requests/minute")
            self.request_counts[client_id] = recent_requests  # Keep for logging
            return False
        
        # Add current request
        recent_requests.append(now)
        self.request_counts[client_id] = recent_requests
        
        return True
    
    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for client in current window."""
        if client_id not in self.request_counts:
            return self.max_requests
        
        now = datetime.now()
        window_start = now - datetime.timedelta(seconds=self.window_seconds)
        recent_requests = [
            ts for ts in self.request_counts[client_id]
            if ts > window_start
        ]
        
        return max(0, self.max_requests - len(recent_requests))

# Global rate limiter instance
# 100 requests per minute per client
_rate_limiter = RateLimiter(max_requests=100, window_seconds=60)

def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    return _rate_limiter

def check_rate_limit(client_id: str) -> bool:
    """
    Check rate limit for client.
    Raises HTTPException if rate limited.
    
    Args:
        client_id: Client identifier (IP or API key)
        
    Returns:
        True if allowed
        
    Raises:
        HTTPException: If rate limited (429 status)
    """
    limiter = get_rate_limiter()
    
    if not limiter.is_allowed(client_id):
        remaining = limiter.get_remaining(client_id)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. {remaining} requests remaining in window"
        )
    
    return True
