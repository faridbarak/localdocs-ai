"""Security Module for LocalDocs AI"""

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
from .rate_limiter import (
    RateLimiter,
    get_rate_limiter,
    check_rate_limit
)
from .output_sanitizer import (
    OutputSanitizer,
    get_output_sanitizer,
    sanitize_output,
    validate_and_sanitize_output
)
from .logger import (
    SecurityLogger,
    get_security_logger
)
from .input_validator import (
    InputValidator,
    get_input_validator,
    validate_prompt,
    validate_file_name,
    validate_query,
    validate_and_sanitize_input
)

__all__ = [
    "PromptInjectionDetector",
    "get_injection_detector",
    "validate_and_sanitize_prompt",
    "verify_api_key",
    "generate_api_key",
    "get_valid_api_keys",
    "get_api_key_config",
    "API_KEY_HEADER",
    "RateLimiter",
    "get_rate_limiter",
    "check_rate_limit",
    "OutputSanitizer",
    "get_output_sanitizer",
    "sanitize_output",
    "validate_and_sanitize_output",
    "SecurityLogger",
    "get_security_logger",
    "InputValidator",
    "get_input_validator",
    "validate_prompt",
    "validate_file_name",
    "validate_query",
    "validate_and_sanitize_input"
]
