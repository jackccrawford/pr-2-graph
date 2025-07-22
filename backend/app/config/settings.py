"""Configuration management for pr-2-graph."""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Server Settings
    port: int = Field(env="PORT")
    host: str = Field(env="HOST")
    debug: bool = Field(env="DEBUG")
    
    # Ollama Configuration
    ollama_base_url: str = Field(env="OLLAMA_BASE_URL")
    ollama_timeout: int = Field(env="OLLAMA_TIMEOUT")
    
    # Model Configuration
    primary_model: str = Field(env="PRIMARY_MODEL")
    critic_model: str = Field(env="CRITIC_MODEL")
    embeddings_model: str = Field(env="EMBEDDINGS_MODEL")
    fallback_model: str = Field(env="FALLBACK_MODEL")
    formatter_model: str = Field(env="FORMATTER_MODEL")
    
    # Memory Management
    max_memory_gb: float = Field(env="MAX_MEMORY_GB")
    auto_cleanup: bool = Field(env="AUTO_CLEANUP")
    fallback_threshold: float = Field(env="FALLBACK_THRESHOLD")
    
    # Analysis Settings
    enable_critique: bool = Field(env="ENABLE_CRITIQUE")
    enable_embeddings: bool = Field(env="ENABLE_EMBEDDINGS")
    analysis_timeout: int = Field(env="ANALYSIS_TIMEOUT")
    
    # GitHub API (optional)
    github_token: Optional[str] = Field(default=None, env="GITHUB_TOKEN")
    github_api_url: str = Field(env="GITHUB_API_URL")
    
    # Logging
    log_level: str = Field(env="LOG_LEVEL")
    log_format: str = Field(env="LOG_FORMAT")
    
    class Config:
        env_file = [".env.local", ".env"]
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_model_config():
    """Get model configuration dictionary."""
    return {
        "primary": settings.primary_model,
        "critic": settings.critic_model,
        "embeddings": settings.embeddings_model,
        "fallback": settings.fallback_model,
        "formatter": settings.formatter_model,
    }


def get_memory_config():
    """Get memory management configuration."""
    return {
        "max_memory_gb": settings.max_memory_gb,
        "auto_cleanup": settings.auto_cleanup,
        "fallback_threshold": settings.fallback_threshold,
    }


def get_ollama_config():
    """Get Ollama client configuration."""
    return {
        "base_url": settings.ollama_base_url,
        "timeout": settings.ollama_timeout,
    }
