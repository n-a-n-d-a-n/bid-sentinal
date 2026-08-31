"""Auth schemas — login, token, register."""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.schemas.common import UserRole


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user_id: str
    username: str
    role: UserRole
    full_name: str


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_.-]+$")
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.VIEWER
    department: Optional[str] = None
    designation: Optional[str] = None
    employee_id: Optional[str] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    username: str
    full_name: str
    role: str
    department: Optional[str] = None
    designation: Optional[str] = None
    employee_id: Optional[str] = None
    is_active: bool
    is_verified: bool
    last_login: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    department: Optional[str] = None
    designation: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
