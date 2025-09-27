from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.STUDENT


class UserCreate(UserBase):
    password: str
    # Student fields
    student_id: Optional[str] = None
    campus: Optional[str] = None
    year_of_study: Optional[int] = None
    # Counsellor fields
    license_number: Optional[str] = None
    specialization: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    student_id: Optional[str] = None
    campus: Optional[str] = None
    year_of_study: Optional[int] = None
    license_number: Optional[str] = None
    specialization: Optional[str] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenRefresh(BaseModel):
    refresh_token: str