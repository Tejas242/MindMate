from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user, get_counsellor_user
from app.models.user import User
from app.services.risk_service import RiskAssessmentService, InterventionService
from app.schemas.chat import RiskAssessmentResponse, InterventionResponse

router = APIRouter(prefix="/risk", tags=["risk assessment"])


class RiskAssessmentRequest(BaseModel):
    message: str
    context: List[str] = []


class RiskAssessmentResult(BaseModel):
    overall_risk_score: float
    risk_level: str
    depression_score: float
    anxiety_score: float
    suicide_risk_score: float
    self_harm_score: float
    risk_factors: Dict
    explanation: str
    confidence_level: float


@router.post("/assess", response_model=RiskAssessmentResult)
async def assess_message_risk(
    request: RiskAssessmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assess risk level of a message (for testing/development)"""
    
    risk_service = RiskAssessmentService(db)
    
    # Use AI service directly for assessment without storing
    from app.services.ai_service import ai_service
    risk_data = ai_service.assess_message_risk(request.message, request.context)
    
    return RiskAssessmentResult(**risk_data)


@router.get("/interventions/{risk_level}", response_model=List[InterventionResponse])
async def get_interventions_by_risk(
    risk_level: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get interventions appropriate for a specific risk level"""
    
    valid_levels = ["low", "medium", "high", "crisis"]
    if risk_level not in valid_levels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid risk level. Must be one of: {valid_levels}"
        )
    
    intervention_service = InterventionService(db)
    interventions = intervention_service.get_interventions_for_risk_level(risk_level)
    
    return interventions


@router.get("/user/{user_id}/trend")
async def get_user_risk_trend(
    user_id: int,
    current_user: User = Depends(get_counsellor_user),
    db: Session = Depends(get_db),
    limit: int = 10
):
    """Get risk trend for a specific user (counsellor access only)"""
    
    # Verify target user exists
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    risk_service = RiskAssessmentService(db)
    trend_data = risk_service.get_user_risk_trend(user_id, limit)
    
    return {
        "user": {
            "id": target_user.id,
            "username": target_user.username,
            "full_name": target_user.full_name
        },
        "trend": trend_data
    }


@router.get("/crisis-keywords")
async def get_crisis_keywords(
    current_user: User = Depends(get_counsellor_user)
):
    """Get list of crisis keywords used for detection"""
    
    from app.core.config import settings
    return {
        "keywords": settings.CRISIS_KEYWORDS,
        "note": "These keywords trigger crisis-level risk assessment"
    }


@router.post("/init-interventions")
async def initialize_default_interventions(
    current_user: User = Depends(get_counsellor_user),
    db: Session = Depends(get_db)
):
    """Initialize default interventions in the database"""
    
    intervention_service = InterventionService(db)
    intervention_service.create_default_interventions()
    
    return {"message": "Default interventions initialized successfully"}