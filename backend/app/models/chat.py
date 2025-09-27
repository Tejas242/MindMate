from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRISIS = "crisis"


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String, unique=True, index=True, nullable=False)  # For anonymization
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Risk assessment
    current_risk_level = Column(String, default=RiskLevel.LOW)
    risk_score = Column(Float, default=0.0)
    risk_factors = Column(JSON, nullable=True)  # Store detected risk factors
    
    # Crisis handling
    crisis_flagged = Column(Boolean, default=False)
    counsellor_notified = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    sender = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # AI metadata
    tokens_used = Column(Integer, nullable=True)
    response_time = Column(Float, nullable=True)
    model_used = Column(String, nullable=True)
    
    # Safety filtering
    safety_filtered = Column(Boolean, default=False)
    original_content = Column(Text, nullable=True)  # If content was filtered
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    message_id = Column(Integer, ForeignKey("chat_messages.id"), nullable=True)
    
    # Assessment scores
    overall_risk_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    
    # Specific assessment scores (PHQ-2/9, GAD-7 inspired)
    depression_score = Column(Float, default=0.0)
    anxiety_score = Column(Float, default=0.0)
    suicide_risk_score = Column(Float, default=0.0)
    self_harm_score = Column(Float, default=0.0)
    
    # Detected indicators
    risk_factors = Column(JSON, nullable=True)
    protective_factors = Column(JSON, nullable=True)
    crisis_keywords_detected = Column(JSON, nullable=True)
    
    # AI explanation
    explanation = Column(Text, nullable=True)
    confidence_level = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("ChatSession", back_populates="risk_assessments")


class Intervention(Base):
    __tablename__ = "interventions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # 'cbt', 'breathing', 'journaling', etc.
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)  # The actual intervention content/prompt
    
    # Targeting
    min_risk_level = Column(String, default=RiskLevel.LOW)
    max_risk_level = Column(String, default=RiskLevel.HIGH)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CounsellorAssignment(Base):
    __tablename__ = "counsellor_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    counsellor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="pending")  # pending, contacted, resolved
    priority = Column(String, default="medium")  # low, medium, high, crisis
    
    notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    student = relationship("User", foreign_keys=[student_id])
    counsellor = relationship("User", foreign_keys=[counsellor_id])
    session = relationship("ChatSession")


# Add relationships to User model
from app.models.user import User
User.chat_sessions = relationship("ChatSession", back_populates="user")