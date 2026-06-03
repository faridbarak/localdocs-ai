"""Application configuration settings using Pydantic"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    app_name: str = "LocalDocs AI"
    app_version: str = "0.1.0"
    log_level: str = "INFO"
    
    # LLM / Ollama Settings
    ollama_base_url: str = "http://localhost:11434"
    default_model: str = "llama3"
    
    # Storage Settings
    storage_dir: str = "./data"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instantiate a global settings object
settings = Settings()
