"""Pydantic schemas for API validation"""
from pydantic import BaseModel
from typing import Optional, List


class GenerateDocsRequest(BaseModel):
    code: str
    language: str = "python"
    model: Optional[str] = None
    project_name: Optional[str] = "Project"


class GenerateDocsResponse(BaseModel):
    success: bool
    documentation: str
    elements_count: int
    model_used: str


class HealthCheckResponse(BaseModel):
    status: str
    version: str
    ollama_connected: bool
