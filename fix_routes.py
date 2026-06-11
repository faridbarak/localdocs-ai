import sys
content = """from fastapi import APIRouter, HTTPException
from localdocs.api.schemas import GenerateDocsRequest
from localdocs.llm.ollama_client import OllamaClient
from localdocs.parsers.python_parser import PythonParser
from localdocs.parsers.javascript_parser import JavaScriptParser
from localdocs.generators.markdown_generator import MarkdownGenerator
from localdocs.utils.config import settings

router = APIRouter()
ollama_client = OllamaClient()

@router.get("/")
async def root():
    return {"message": "LocalDocs AI", "version": settings.app_version, "docs": "/docs"}

@router.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "version": settings.app_version, "ollama_connected": ollama_client.check_connection()}

@router.get("/api/v1/models")
async def list_models():
    return {"models": ollama_client.list_models(), "default": settings.ollama_default_model}

@router.post("/api/v1/generate-docs")
async def generate_docs(request: GenerateDocsRequest):
    parser = PythonParser(request.code) if request.language.lower() in ["python", "py"] else JavaScriptParser(request.code)
    elements = parser.parse()
    ai_docs = ollama_client.generate_docs(request.code, request.model, request.language)
    markdown = MarkdownGenerator.generate(elements, request.project_name)
    markdown += "\
\
## AI-Generated Documentation\
\
" + ai_docs
    return {"success": True, "documentation": markdown, "elements_count": len(elements)}

@router.post("/api/v1/parse-code")
async def parse_code(code: str, language: str = "python"):
    parser = PythonParser(code) if language.lower() in ["python", "py"] else JavaScriptParser(code)
    elements = parser.parse()
    return {"success": True, "count": len(elements)}
"""
open("src/localdocs/api/routes.py", "w").write(content)
print("Done!")

