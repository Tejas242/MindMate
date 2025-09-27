from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_counsellor_user, get_admin_user
from app.models.user import User
from app.models.chat import ChatSession, CounsellorAssignment
from app.schemas.chat import ChatSessionResponse, RiskAssessmentResponse
from app.services.risk_service import RiskAssessmentService
from pydantic import BaseModel

router = APIRouter(prefix="/counsellor", tags=["counsellor"])


class HighRiskSessionResponse(BaseModel):
    session: ChatSessionResponse
    user_info: Dict
    latest_assessment: RiskAssessmentResponse
    messages_count: int
    assigned_counsellor: Optional[str] = None


class CounsellorAssignmentCreate(BaseModel):
    student_id: int
    session_id: int
    priority: str = "medium"
    notes: Optional[str] = None


class CounsellorAssignmentResponse(BaseModel):
    id: int
    student_id: int
    counsellor_id: int
    session_id: int
    assigned_at: datetime
    status: str
    priority: str
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.get("/dashboard/high-risk", response_model=List[HighRiskSessionResponse])
async def get_high_risk_sessions(
    current_user: User = Depends(get_counsellor_user),
    db: Session = Depends(get_db),
    assigned_only: bool = False
):
    """Get high-risk sessions for counsellor dashboard"""
    
    risk_service = RiskAssessmentService(db)
    
    if assigned_only:
        # Get only sessions assigned to this counsellor
        high_risk_data = risk_service.get_high_risk_sessions(current_user.id)
    else:
        # Get all high-risk sessions (for admins or general viewing)
        high_risk_data = risk_service.get_high_risk_sessions()
    
    response_data = []
    for item in high_risk_data:
        session = item["session"]
        user = item["user"]
        assessment = item["latest_assessment"]
        
        # Get assigned counsellor if any
        assignment = db.query(CounsellorAssignment).filter(
            CounsellorAssignment.session_id == session.id,
            CounsellorAssignment.status != "resolved"
        ).first()
        
        assigned_counsellor = None
        if assignment:
            counsellor = db.query(User).filter(User.id == assignment.counsellor_id).first()
            if counsellor:
                assigned_counsellor = counsellor.full_name or counsellor.username
        
        response_data.append(HighRiskSessionResponse(
            session=session,
            user_info={
                "id": user.id,
                "username": user.username,
                "campus": user.campus,
                "year_of_study": user.year_of_study,
                "student_id": user.student_id
            },
            latest_assessment=assessment,
            messages_count=item["messages_count"],
            assigned_counsellor=assigned_counsellor
        ))
    
    return response_data


@router.get("/dashboard/assignments", response_model=List[CounsellorAssignmentResponse])
async def get_my_assignments(
    current_user: User = Depends(get_counsellor_user),
    db: Session = Depends(get_db),
    status_filter: Optional[str] = None
):
    """Get assignments for the current counsellor"""
    
    query = db.query(CounsellorAssignment).filter(
        CounsellorAssignment.counsellor_id == current_user.id
    )
    
    if status_filter:
        query = query.filter(CounsellorAssignment.status == status_filter)
    
    assignments = query.order_by(CounsellorAssignment.assigned_at.desc()).all()
    
    return assignments


@router.post("/assignments", response_model=CounsellorAssignmentResponse)
async def create_assignment(
    assignment_data: CounsellorAssignmentCreate,
    current_user: User = Depends(get_counsellor_user),
    db: Session = Depends(get_db)
):
    """Assign a session to the current counsellor"""
    
    # Verify session exists and is high risk
    session = db.query(ChatSession).filter(ChatSession.id == assignment_data.session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.current_risk_level not in ["high", "crisis"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is not high risk"
        )
    
    # Check if already assigned
    existing = db.query(CounsellorAssignment).filter(
        CounsellorAssignment.session_id == assignment_data.session_id,
        CounsellorAssignment.status != "resolved"
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already assigned"
        )
    
    # Create assignment
    assignment = CounsellorAssignment(
        student_id=assignment_data.student_id,
        counsellor_id=current_user.id,
        session_id=assignment_data.session_id,
        priority=assignment_data.priority,
        notes=assignment_data.notes,
        status="pending"
    )
    
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    return assignment


@router.put("/assignments/{assignment_id}/status")
async def update_assignment_status(
    assignment_id: int,
    status: str,
    notes: Optional[str] = None,
    current_user: User = Depends(get_counsellor_user),
    db: Session = Depends(get_db)
):
    """Update assignment status"""
    
    assignment = db.query(CounsellorAssignment).filter(
        CounsellorAssignment.id == assignment_id,
        CounsellorAssignment.counsellor_id == current_user.id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    valid_statuses = ["pending", "contacted", "resolved"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    assignment.status = status
    if notes:
        assignment.notes = notes
    
    if status == "resolved":
        assignment.resolved_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Assignment status updated successfully"}


@router.get("/students/{student_id}/risk-trend")
async def get_student_risk_trend(
    student_id: int,
    current_user: User = Depends(get_counsellor_user),
    db: Session = Depends(get_db)
):
    """Get risk trend for a specific student"""
    
    # Verify student exists
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    risk_service = RiskAssessmentService(db)
    trend_data = risk_service.get_user_risk_trend(student_id, limit=20)
    
    return {
        "student": {
            "id": student.id,
            "username": student.username,
            "full_name": student.full_name,
            "campus": student.campus
        },
        "risk_trend": trend_data
    }


@router.get("/dashboard/stats")
async def get_counsellor_stats(
    current_user: User = Depends(get_counsellor_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for counsellor"""
    
    # Get assignments in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    assignments = db.query(CounsellorAssignment).filter(
        CounsellorAssignment.counsellor_id == current_user.id,
        CounsellorAssignment.assigned_at >= thirty_days_ago
    ).all()
    
    stats = {
        "total_assignments": len(assignments),
        "pending_assignments": len([a for a in assignments if a.status == "pending"]),
        "resolved_assignments": len([a for a in assignments if a.status == "resolved"]),
        "crisis_assignments": len([a for a in assignments if a.priority == "crisis"]),
        "high_priority_assignments": len([a for a in assignments if a.priority == "high"])
    }
    
    # Get current high-risk sessions count
    high_risk_sessions = db.query(ChatSession).filter(
        ChatSession.current_risk_level.in_(["high", "crisis"]),
        ChatSession.is_active == True
    ).count()
    
    stats["current_high_risk_sessions"] = high_risk_sessions
    
    return stats


# Admin-only endpoints
@router.get("/admin/all-assignments", response_model=List[CounsellorAssignmentResponse])
async def get_all_assignments(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Get all assignments (admin only)"""
    
    assignments = db.query(CounsellorAssignment).order_by(
        CounsellorAssignment.assigned_at.desc()
    ).limit(limit).all()
    
    return assignments


@router.get("/admin/system-stats")
async def get_system_stats(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get system-wide statistics (admin only)"""
    
    # Get counts for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    total_sessions = db.query(ChatSession).filter(
        ChatSession.created_at >= thirty_days_ago
    ).count()
    
    high_risk_sessions = db.query(ChatSession).filter(
        ChatSession.current_risk_level.in_(["high", "crisis"]),
        ChatSession.created_at >= thirty_days_ago
    ).count()
    
    crisis_sessions = db.query(ChatSession).filter(
        ChatSession.current_risk_level == "crisis",
        ChatSession.created_at >= thirty_days_ago
    ).count()
    
    total_users = db.query(User).filter(User.role == "student").count()
    
    return {
        "total_sessions_30d": total_sessions,
        "high_risk_sessions_30d": high_risk_sessions,
        "crisis_sessions_30d": crisis_sessions,
        "total_students": total_users,
        "high_risk_percentage": (high_risk_sessions / total_sessions * 100) if total_sessions > 0 else 0
    }