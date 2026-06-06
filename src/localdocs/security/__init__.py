"""
Security Module for LocalDocs AI
================================
Prompt injection protection and API authentication
"""

from .prompt_injection import (
    PromptInjectionDetector,
    get_injection_detector,
    validate_and_sanitize_prompt
)
from .api_auth import (
    verify_api_key,
    generate_api_key,
    get_valid_api_keys,
    get_api_key_config,
    API_KEY_HEADER
)

__all__ = [
    "PromptInjectionDetector",
    "get_injection_detector",
    "validate_and_sanitize_prompt",
    "verify_api_key",
    "generate_api_key",
    "get_valid_api_keys",
    "get_api_key_config",
    "API_KEY_HEADER"
]
