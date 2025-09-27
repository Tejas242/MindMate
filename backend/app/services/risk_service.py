from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.chat import RiskAssessment, ChatSession, Intervention
from app.services.ai_service import ai_service
import uuid


class RiskAssessmentService:
    
    def __init__(self, db: Session):
        self.db = db
    
    async def assess_message_risk(
        self, 
        message: str, 
        session_id: int,
        message_id: Optional[int] = None,
        conversation_history: List[str] = None
    ) -> RiskAssessment:
        """Assess risk for a message and store in database"""
        
        # Get risk assessment from AI service
        risk_data = ai_service.assess_message_risk(message, conversation_history)
        
        # Create risk assessment record
        risk_assessment = RiskAssessment(
            session_id=session_id,
            message_id=message_id,
            overall_risk_score=risk_data["overall_risk_score"],
            risk_level=risk_data["risk_level"],
            depression_score=risk_data["depression_score"],
            anxiety_score=risk_data["anxiety_score"],
            suicide_risk_score=risk_data["suicide_risk_score"],
            self_harm_score=risk_data["self_harm_score"],
            risk_factors=risk_data["risk_factors"],
            explanation=risk_data["explanation"],
            confidence_level=risk_data["confidence_level"]
        )
        
        self.db.add(risk_assessment)
        self.db.commit()
        self.db.refresh(risk_assessment)
        
        # Update session risk level
        session = self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            session.current_risk_level = risk_data["risk_level"]
            session.risk_score = risk_data["overall_risk_score"]
            
            # Flag crisis if detected
            if risk_data["risk_level"] == "crisis":
                session.crisis_flagged = True
            
            self.db.commit()
        
        return risk_assessment
    
    def get_session_risk_history(self, session_id: int) -> List[RiskAssessment]:
        """Get risk assessment history for a session"""
        return self.db.query(RiskAssessment).filter(
            RiskAssessment.session_id == session_id
        ).order_by(RiskAssessment.created_at.desc()).all()
    
    def get_user_risk_trend(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get risk trend for a user across all sessions"""
        sessions = self.db.query(ChatSession).filter(
            ChatSession.user_id == user_id,
            ChatSession.is_active == True
        ).order_by(ChatSession.created_at.desc()).limit(limit).all()
        
        trend_data = []
        for session in sessions:
            latest_assessment = self.db.query(RiskAssessment).filter(
                RiskAssessment.session_id == session.id
            ).order_by(RiskAssessment.created_at.desc()).first()
            
            if latest_assessment:
                trend_data.append({
                    "session_id": session.id,
                    "date": session.created_at,
                    "risk_level": latest_assessment.risk_level,
                    "risk_score": latest_assessment.overall_risk_score,
                    "crisis_flagged": session.crisis_flagged
                })
        
        return trend_data
    
    def get_high_risk_sessions(self, counsellor_id: Optional[int] = None) -> List[Dict]:
        """Get sessions flagged as high risk or crisis"""
        query = self.db.query(ChatSession).filter(
            ChatSession.current_risk_level.in_(["high", "crisis"]),
            ChatSession.is_active == True
        )
        
        # If counsellor specified, filter by assignments
        if counsellor_id:
            from app.models.chat import CounsellorAssignment
            query = query.join(CounsellorAssignment).filter(
                CounsellorAssignment.counsellor_id == counsellor_id
            )
        
        sessions = query.order_by(ChatSession.updated_at.desc()).all()
        
        result = []
        for session in sessions:
            latest_assessment = self.db.query(RiskAssessment).filter(
                RiskAssessment.session_id == session.id
            ).order_by(RiskAssessment.created_at.desc()).first()
            
            result.append({
                "session": session,
                "user": session.user,
                "latest_assessment": latest_assessment,
                "messages_count": len(session.messages)
            })
        
        return result


class InterventionService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_interventions_for_risk_level(self, risk_level: str) -> List[Intervention]:
        """Get appropriate interventions for a risk level"""
        return self.db.query(Intervention).filter(
            Intervention.is_active == True,
            Intervention.min_risk_level <= risk_level,
            Intervention.max_risk_level >= risk_level
        ).all()
    
    def create_default_interventions(self):
        """Create default set of interventions"""
        default_interventions = [
            {
                "name": "5-4-3-2-1 Grounding",
                "category": "breathing",
                "description": "A grounding technique for anxiety",
                "content": "Let's try the 5-4-3-2-1 grounding technique:\n\n5 things you can see around you\n4 things you can touch\n3 things you can hear\n2 things you can smell\n1 thing you can taste\n\nTake your time with each step and focus on the present moment.",
                "min_risk_level": "low",
                "max_risk_level": "high"
            },
            {
                "name": "Box Breathing",
                "category": "breathing",
                "description": "Simple breathing exercise for stress relief",
                "content": "Let's do some box breathing together:\n\n1. Breathe in for 4 counts\n2. Hold for 4 counts\n3. Breathe out for 4 counts\n4. Hold for 4 counts\n\nRepeat this cycle 4-6 times. Focus only on your breathing.",
                "min_risk_level": "low",
                "max_risk_level": "high"
            },
            {
                "name": "Quick Mood Check-in",
                "category": "cbt",
                "description": "Cognitive behavioral technique for self-awareness",
                "content": "Take a moment to check in with yourself:\n\n• What am I feeling right now?\n• What thoughts are going through my mind?\n• What's happening in my body?\n• What do I need right now?\n\nThere are no wrong answers - just observe without judgment.",
                "min_risk_level": "low",
                "max_risk_level": "medium"
            },
            {
                "name": "Thought Challenge",
                "category": "cbt",
                "description": "Challenge negative thought patterns",
                "content": "When we're struggling, our thoughts can become very negative. Let's examine them:\n\n1. What's the specific thought bothering you?\n2. Is this thought helpful or accurate?\n3. What would you tell a friend having this thought?\n4. What's a more balanced way to think about this?\n\nRemember: thoughts are not facts.",
                "min_risk_level": "medium",
                "max_risk_level": "high"
            },
            {
                "name": "Values Reminder",
                "category": "journaling",
                "description": "Connect with personal values and meaning",
                "content": "Sometimes when we're struggling, we lose sight of what matters to us. Take a moment to think about:\n\n• What are 3 things that are important to you?\n• What gives your life meaning?\n• What would your best self do in this situation?\n• What small step could you take today that aligns with your values?\n\nYour worth isn't determined by your struggles.",
                "min_risk_level": "medium",
                "max_risk_level": "high"
            }
        ]
        
        for intervention_data in default_interventions:
            existing = self.db.query(Intervention).filter(
                Intervention.name == intervention_data["name"]
            ).first()
            
            if not existing:
                intervention = Intervention(**intervention_data)
                self.db.add(intervention)
        
        self.db.commit()