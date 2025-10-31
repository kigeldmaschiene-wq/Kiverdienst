import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://kiverdienst:password@localhost:5432/kiverdienst_v2")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    
    # AI Services
    ollama_url: str = os.getenv("OLLAMA_URL", "http://135.181.129.240:11434")
    ollama_model_large: str = os.getenv("OLLAMA_MODEL_LARGE", "llama3.1:70b")
    ollama_model_fast: str = os.getenv("OLLAMA_MODEL_FAST", "llama3.1:8b-instruct-q8_0")
    
    runway_api_key: Optional[str] = os.getenv("RUNWAY_API_KEY")
    
    # Azure TTS
    azure_tts_key: Optional[str] = os.getenv("AZURE_TTS_KEY")
    azure_tts_region: str = os.getenv("AZURE_TTS_REGION", "westeurope")
    
    # Email
    sendgrid_api_key: Optional[str] = os.getenv("SENDGRID_API_KEY")
    
    # Proxies
    brightdata_username: Optional[str] = os.getenv("BRIGHTDATA_USERNAME")
    brightdata_password: Optional[str] = os.getenv("BRIGHTDATA_PASSWORD")
    
    class Config:
        env_file = ".env"

settings = Settings()
