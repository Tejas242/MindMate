from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatMessageCreate(BaseModel):
    content: str


class ChatMessageResponse(BaseModel):
    id: int
    sender: str
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ChatSessionCreate(BaseModel):
    pass  # No fields needed, session created automatically


class ChatSessionResponse(BaseModel):
    id: int
    session_token: str
    created_at: datetime
    current_risk_level: str
    risk_score: float
    crisis_flagged: bool
    
    class Config:
        from_attributes = True


class RiskAssessmentResponse(BaseModel):
    id: int
    overall_risk_score: float
    risk_level: str
    depression_score: float
    anxiety_score: float
    suicide_risk_score: float
    self_harm_score: float
    risk_factors: Optional[Dict[str, Any]] = None
    protective_factors: Optional[Dict[str, Any]] = None
    explanation: Optional[str] = None
    confidence_level: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class InterventionResponse(BaseModel):
    id: int
    name: str
    category: str
    description: Optional[str] = None
    content: str
    
    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    message: ChatMessageResponse
    risk_assessment: Optional[RiskAssessmentResponse] = None
    interventions: List[InterventionResponse] = []
    crisis_alert: bool = False