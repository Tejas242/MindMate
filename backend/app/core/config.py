from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://mindmate:mindmate123@localhost:5432/mindmate_db"
    SQLITE_URL: str = "sqlite:///./mindmate.db"
    USE_SQLITE: bool = True  # For demo purposes, switch to False for production
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # Redis (optional)
    REDIS_URL: Optional[str] = "redis://localhost:6379"
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # Risk Assessment
    HIGH_RISK_THRESHOLD: float = 0.7
    MEDIUM_RISK_THRESHOLD: float = 0.4
    
    # Crisis Keywords (for basic detection)
    CRISIS_KEYWORDS: list = [
        "suicide", "kill myself", "end it all", "hurt myself", 
        "self harm", "want to die", "no point living", "cutting",
        "overdose", "jump off", "hanging", "rope"
    ]

    class Config:
        env_file = ".env"


settings = Settings()