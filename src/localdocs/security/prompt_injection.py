import re
import string
from typing import Tuple, Optional
from fastapi import HTTPException

class PromptInjectionDetector:
    INJECTION_PATTERNS = [
        r"ignores+previouss+instructions",
        r"disregards+previouss+instructions",
        r"forgets+everythings+before",
        r"starts+froms+now",
        r"froms+nows+ons+ignore",
        r"whats+iss+yours+systems+prompt",
        r"reveals+yours+instructions",
        r"shows+yours+systems+message",
        r"prints+yours+prompt",
        r"acts+ass+ifs+yous+ares+unrestricted",
        r"pretends+tos+bes+unrestricted",
        r"becomes+unrestricted",
        r"executes+command",
        r"runs+systems+command",
        r"accesss+files+system",
        r"deletes+files",
        r"rms+-rf",
        r"'s+ORs+'1's*=s*'1",
        r"--s*$",
        r";s*DROPs+TABLE",
        r"<script[^>]*>",
        r"javascript:",
        r"on(load|error|click)s*=",
    ]
    
    def __init__(self):
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]
    
    def detect_injection(self, user_input: str) -> Tuple[bool, Optional[str]]:
        if not user_input or not user_input.strip():
            return False, None
        for i, pattern in enumerate(self.compiled_patterns):
            if pattern.search(user_input):
                return True, self.INJECTION_PATTERNS[i]
        return False, None
    
    def validate_input(self, user_input: str, max_length: int = 10000) -> Tuple[bool, str]:
        if not user_input:
            return False, "Input cannot be empty"
        if len(user_input) > max_length:
            return False, f"Input exceeds maximum length of {max_length} characters"
        is_injection, pattern = self.detect_injection(user_input)
        if is_injection:
            return False, f"Potentially malicious input detected (pattern: {pattern})"
        return True, "Input validated successfully"
    
    def sanitize_input(self, user_input: str) -> str:
        if not user_input:
            return ""
        return user_input.replace("\\x00", "").replace("\\0", "")

_injection_detector = None

def get_injection_detector() -> PromptInjectionDetector:
    global _injection_detector
    if _injection_detector is None:
        _injection_detector = PromptInjectionDetector()
    return _injection_detector

def validate_and_sanitize_prompt(user_input: str) -> str:
    detector = get_injection_detector()
    is_valid, error_msg = detector.validate_input(user_input)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid input: {error_msg}")
    return detector.sanitize_input(user_input)
