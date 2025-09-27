from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from app.core.database import get_db
from app.core.security import get_current_user, get_student_user
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage, RiskAssessment
from app.schemas.chat import (
    ChatMessageCreate, 
    ChatMessageResponse, 
    ChatSessionResponse, 
    ChatResponse,
    RiskAssessmentResponse,
    InterventionResponse
)
from app.services.ai_service import ai_service
from app.services.risk_service import RiskAssessmentService, InterventionService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    current_user: User = Depends(get_student_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session for the student"""
    
    session_token = str(uuid.uuid4())
    
    chat_session = ChatSession(
        user_id=current_user.id,
        session_token=session_token,
        is_active=True
    )
    
    db.add(chat_session)
    db.commit()
    db.refresh(chat_session)
    
    return chat_session


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_user_sessions(
    current_user: User = Depends(get_student_user),
    db: Session = Depends(get_db),
    limit: int = 10
):
    """Get chat sessions for the current user"""
    
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id,
        ChatSession.is_active == True
    ).order_by(ChatSession.created_at.desc()).limit(limit).all()
    
    return sessions


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_session_messages(
    session_id: int,
    current_user: User = Depends(get_student_user),
    db: Session = Depends(get_db)
):
    """Get messages for a specific session"""
    
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.timestamp.asc()).all()
    
    return messages


@router.post("/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_message(
    session_id: int,
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_student_user),
    db: Session = Depends(get_db)
):
    """Send a message in a chat session and get AI response"""
    
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id,
        ChatSession.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or inactive"
        )
    
    try:
        # Save user message
        user_message = ChatMessage(
            session_id=session_id,
            sender="user",
            content=message_data.content
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)
        
        # Get conversation history for context
        previous_messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.timestamp.desc()).limit(10).all()
        
        conversation_history = []
        for msg in reversed(previous_messages[1:]):  # Exclude the current message
            role = "user" if msg.sender == "user" else "assistant"
            conversation_history.append({"role": role, "content": msg.content})
        
        # Generate AI response
        ai_response = await ai_service.generate_response(
            message_data.content, 
            conversation_history
        )
        
        # Apply safety filtering
        filtered_response, was_filtered = ai_service.filter_response_safety(ai_response)
        
        # Save AI response
        ai_message = ChatMessage(
            session_id=session_id,
            sender="assistant",
            content=filtered_response,
            safety_filtered=was_filtered,
            original_content=ai_response if was_filtered else None,
            model_used="gpt-3.5-turbo"
        )
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)
        
        # Perform risk assessment
        risk_service = RiskAssessmentService(db)
        risk_assessment = await risk_service.assess_message_risk(
            message_data.content,
            session_id,
            user_message.id,
            [msg.content for msg in previous_messages if msg.sender == "user"]
        )
        
        # Get appropriate interventions
        intervention_service = InterventionService(db)
        interventions = intervention_service.get_interventions_for_risk_level(
            risk_assessment.risk_level
        )
        
        # Prepare response
        response = ChatResponse(
            message=ai_message,
            risk_assessment=risk_assessment,
            interventions=interventions,
            crisis_alert=(risk_assessment.risk_level == "crisis")
        )
        
        # Handle crisis situations
        if risk_assessment.risk_level == "crisis":
            from app.services.crisis_service import CrisisEscalationService
            crisis_service = CrisisEscalationService(db)
            
            crisis_result = await crisis_service.handle_crisis_session(
                session_id,
                {
                    "overall_risk_score": risk_assessment.overall_risk_score,
                    "risk_level": risk_assessment.risk_level,
                    "risk_factors": risk_assessment.risk_factors
                }
            )
            
            logger.warning(f"Crisis escalation triggered for session {session_id}: {crisis_result}")
            
        elif risk_assessment.risk_level == "high":
            # Escalate high-risk sessions for counsellor review
            from app.services.crisis_service import CrisisEscalationService
            crisis_service = CrisisEscalationService(db)
            
            escalation_result = crisis_service.escalate_high_risk_session(session_id)
            logger.info(f"High-risk session escalated: {escalation_result}")
        
        return response
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing message"
        )


@router.get("/sessions/{session_id}/risk-history", response_model=List[RiskAssessmentResponse])
async def get_session_risk_history(
    session_id: int,
    current_user: User = Depends(get_student_user),
    db: Session = Depends(get_db)
):
    """Get risk assessment history for a session"""
    
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    risk_service = RiskAssessmentService(db)
    risk_history = risk_service.get_session_risk_history(session_id)
    
    return risk_history


@router.get("/interventions", response_model=List[InterventionResponse])
async def get_interventions(
    risk_level: str = "low",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available interventions for a risk level"""
    
    intervention_service = InterventionService(db)
    interventions = intervention_service.get_interventions_for_risk_level(risk_level)
    
    return interventions


@router.get("/crisis-resources")
async def get_crisis_resources(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get crisis response resources and hotlines"""
    
    from app.services.crisis_service import CrisisEscalationService
    crisis_service = CrisisEscalationService(db)
    resources = crisis_service.get_crisis_response_resources()
    
    return resources