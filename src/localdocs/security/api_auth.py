"""
API Authentication Module
=========================
API Key authentication for protecting endpoints
"""

import os
import secrets
from typing import Optional, List
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
import logging

logger = logging.getLogger(__name__)

# API Key authentication
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Generate a secure API key (store this securely!)
def generate_api_key() -> str:
    """Generate a secure random API key."""
    return secrets.token_hex(32)

# Load API keys from environment or config
def get_valid_api_keys() -> List[str]:
    """Get list of valid API keys from environment variable."""
    api_keys_env = os.getenv("LOCALDOCS_API_KEYS", "")
    if not api_keys_env:
        # If no API keys set, generate one and warn
        default_key = generate_api_key()
        logger.warning(f"⚠️ NO API KEYS SET! Generated default key: {default_key}")
        logger.warning("Set LOCALDOCS_API_KEYS environment variable with your API key(s)")
        return [default_key]
    
    # Support multiple keys separated by comma
    return [key.strip() for key in api_keys_env.split(",") if key.strip()]

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> bool:
    """
    Verify if the provided API key is valid.
    
    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not api_key:
        logger.warning("[AUTH] Missing API key")
        raise HTTPException(
            status_code=401,
            detail="API key is required. Set X-API-Key header"
        )
    
    valid_keys = get_valid_api_keys()
    
    if api_key not in valid_keys:
        logger.warning(f"[AUTH] Invalid API key attempt: {api_key[:8]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    logger.info(f"[AUTH] Valid API key authenticated")
    return True

def get_api_key_config() -> dict:
    """Get API key configuration info (without exposing keys)."""
    keys = get_valid_api_keys()
    return {
        "api_keys_configured": len(keys) > 0,
        "num_keys": len(keys),
        "key_masked": keys[0][:8] + "..." if keys else None,
        "env_var": "LOCALDOCS_API_KEYS"
    }
