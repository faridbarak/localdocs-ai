from fastapi import APIRouter, HTTPException, Security
from typing import List, Dict, Any
import logging

from localdocs.api.schemas import GenerateDocsRequest, GenerateDocsResponse, HealthCheckResponse
from localdocs.parsers.python_parser import PythonParser
from localdocs.security.prompt_injection import validate_and_sanitize_prompt, get_injection_detector
from localdocs.security.api_auth import verify_api_key, get_api_key_config

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=HealthCheckResponse)
async def root():
    return HealthCheckResponse(message="Welcome to LocalDocs AI", version="1.0.0", docs="/docs")

@router.get("/api/v1/security/status")
async def security_status():
    detector = get_injection_detector()
    api_config = get_api_key_config()
    return {"security_enabled": True, "prompt_injection_protection": True, "api_authentication": api_config["api_keys_configured"]}

@router.post("/api/v1/test-security")
async def test_security(request: dict):
    test_input = request.get("test_input", "")
    detector = get_injection_detector()
    is_injection, pattern = detector.detect_injection(test_input)
    return {"is_malicious": is_injection, "pattern_matched": pattern}

@router.post("/api/v1/generate-docs", response_model=GenerateDocsResponse)
async def generate_docs(request: GenerateDocsRequest, api_key: str = Security(verify_api_key)):
    try:
        sanitized_code = validate_and_sanitize_prompt(request.code)
        parser = PythonParser(sanitized_code)
        elements = parser.parse()
        return GenerateDocsResponse(success=True, documentation="Ollama docs", elements_count=len(elements), elements=[{"name": e.name, "type": e.type, "description": e.description} for e in elements])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/parse-code")
async def parse_code(code: str, language: str = "python", api_key: str = Security(verify_api_key)):
    try:
        sanitized_code = validate_and_sanitize_prompt(code)
        if language == "python":
            parser = PythonParser(sanitized_code)
            elements = parser.parse()
            return {"success": True, "count": len(elements)}
        raise HTTPException(status_code=400, detail="Unsupported")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
