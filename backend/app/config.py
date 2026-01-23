"""
Configuration management using Pydantic settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    gemini_api_key: str
    serper_api_key: str = ""
    
    # Environment
    environment: str = "development"
    log_level: str = "INFO"
    
    # Gemini Configuration
    gemini_model: str = "gemini-2.5-flash-lite"
    gemini_temperature: float = 0.7
    gemini_max_tokens: int = 2048
    
    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Interview Settings
    max_questions_per_interview: int = 15
    min_questions_per_interview: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
