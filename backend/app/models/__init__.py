# Import all models to ensure they're registered with SQLAlchemy
from app.models.user import User
from app.models.chat import (
    ChatSession, 
    ChatMessage, 
    RiskAssessment, 
    Intervention, 
    CounsellorAssignment
)

__all__ = [
    "User",
    "ChatSession", 
    "ChatMessage", 
    "RiskAssessment", 
    "Intervention", 
    "CounsellorAssignment"
]