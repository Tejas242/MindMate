from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.chat import ChatSession, CounsellorAssignment
from app.models.user import User
from app.core.config import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)


class CrisisEscalationService:
    
    def __init__(self, db: Session):
        self.db = db
    
    async def handle_crisis_session(self, session_id: int, risk_assessment_data: Dict) -> Dict:
        """Handle crisis-level session escalation"""
        
        session = self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            return {"error": "Session not found"}
        
        # Mark session as crisis
        session.crisis_flagged = True
        session.counsellor_notified = False
        
        # Get available counsellors
        available_counsellors = self.get_available_counsellors()
        
        result = {
            "session_id": session_id,
            "crisis_flagged": True,
            "actions_taken": []
        }
        
        # Auto-assign to available counsellor
        if available_counsellors:
            counsellor = available_counsellors[0]  # Simple assignment to first available
            
            assignment = CounsellorAssignment(
                student_id=session.user_id,
                counsellor_id=counsellor.id,
                session_id=session_id,
                priority="crisis",
                status="pending",
                notes=f"Auto-assigned due to crisis detection. Risk factors: {risk_assessment_data.get('risk_factors', {})}"
            )
            
            self.db.add(assignment)
            session.counsellor_notified = True
            
            result["actions_taken"].append({
                "action": "auto_assigned_counsellor",
                "counsellor": {
                    "id": counsellor.id,
                    "name": counsellor.full_name or counsellor.username,
                    "email": counsellor.email
                }
            })
            
            # Send notification to counsellor
            await self.notify_counsellor_crisis(counsellor, session, risk_assessment_data)
            result["actions_taken"].append("counsellor_notified")
        
        else:
            # No counsellors available - log for manual follow-up
            logger.critical(f"CRISIS SESSION {session_id} - No counsellors available for immediate assignment!")
            result["actions_taken"].append("logged_for_manual_followup")
        
        # Log crisis event
        logger.warning(f"Crisis session detected: {session_id}, User: {session.user_id}, Risk: {risk_assessment_data.get('overall_risk_score', 0)}")
        
        self.db.commit()
        
        return result
    
    def get_available_counsellors(self) -> List[User]:
        """Get list of available counsellors for crisis assignment"""
        
        # Get all active counsellors
        counsellors = self.db.query(User).filter(
            User.role.in_(["counsellor", "admin"]),
            User.is_active == True
        ).all()
        
        # TODO: Add logic to check counsellor availability/workload
        # For now, return all counsellors
        return counsellors
    
    async def notify_counsellor_crisis(self, counsellor: User, session: ChatSession, risk_data: Dict):
        """Send crisis notification to counsellor"""
        
        try:
            # In a real implementation, you would send actual email/SMS/push notification
            # For demo, we'll just log the notification
            
            notification_message = f"""
            CRISIS ALERT - Immediate Attention Required
            
            Student: {session.user.username} (ID: {session.user_id})
            Session: {session.id}
            Risk Score: {risk_data.get('overall_risk_score', 0):.2f}
            Risk Level: {risk_data.get('risk_level', 'unknown')}
            
            Detected Risk Factors:
            {self._format_risk_factors(risk_data.get('risk_factors', {}))}
            
            Please contact the student immediately or coordinate with campus crisis services.
            
            Crisis Resources:
            - Campus Crisis Line: [CAMPUS_CRISIS_NUMBER]
            - National Suicide Prevention Lifeline: 988
            - Crisis Text Line: Text HOME to 741741
            """
            
            logger.warning(f"CRISIS NOTIFICATION sent to {counsellor.email}: {notification_message}")
            
            # TODO: Implement actual notification delivery
            # - Email via SMTP
            # - SMS via Twilio
            # - Push notification via FCM
            # - Slack/Teams integration for institutional alerts
            
        except Exception as e:
            logger.error(f"Failed to send crisis notification to {counsellor.email}: {e}")
    
    def _format_risk_factors(self, risk_factors: Dict) -> str:
        """Format risk factors for notification"""
        if not risk_factors:
            return "None specified"
        
        formatted = []
        for factor, details in risk_factors.items():
            if isinstance(details, list):
                formatted.append(f"- {factor}: {', '.join(details)}")
            else:
                formatted.append(f"- {factor}: {details}")
        
        return "\n".join(formatted)
    
    def get_crisis_response_resources(self) -> Dict:
        """Get crisis response resources and hotlines"""
        
        return {
            "immediate_help": [
                {
                    "name": "National Suicide Prevention Lifeline",
                    "number": "988",
                    "available": "24/7",
                    "method": "call_or_text"
                },
                {
                    "name": "Crisis Text Line",
                    "number": "741741",
                    "text": "HOME",
                    "available": "24/7",
                    "method": "text"
                },
                {
                    "name": "Emergency Services",
                    "number": "911",
                    "available": "24/7",
                    "method": "call"
                }
            ],
            "online_resources": [
                {
                    "name": "SAMHSA National Helpline",
                    "url": "https://www.samhsa.gov/find-help/national-helpline",
                    "description": "Treatment referral and information service"
                },
                {
                    "name": "Crisis Text Line",
                    "url": "https://www.crisistextline.org/",
                    "description": "Free, 24/7 support via text message"
                }
            ],
            "campus_resources": [
                {
                    "name": "Campus Counseling Center",
                    "description": "Contact your campus counseling services",
                    "note": "Available during business hours"
                },
                {
                    "name": "Campus Security",
                    "description": "For immediate campus emergencies",
                    "note": "Available 24/7"
                }
            ]
        }
    
    def escalate_high_risk_session(self, session_id: int) -> Dict:
        """Escalate high-risk (non-crisis) session for counsellor review"""
        
        session = self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            return {"error": "Session not found"}
        
        # Add to counsellor review queue
        existing_assignment = self.db.query(CounsellorAssignment).filter(
            CounsellorAssignment.session_id == session_id,
            CounsellorAssignment.status != "resolved"
        ).first()
        
        if existing_assignment:
            return {"message": "Session already assigned for review"}
        
        # Create assignment for review (not urgent like crisis)
        assignment = CounsellorAssignment(
            student_id=session.user_id,
            counsellor_id=None,  # Will be assigned by counsellors
            session_id=session_id,
            priority="high",
            status="pending",
            notes="High-risk session flagged for counsellor review"
        )
        
        self.db.add(assignment)
        self.db.commit()
        
        logger.info(f"High-risk session {session_id} added to counsellor review queue")
        
        return {
            "session_id": session_id,
            "action": "added_to_review_queue",
            "priority": "high"
        }