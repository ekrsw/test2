from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum


class UserRole(str, Enum):
    GENERAL = "一般ユーザー"
    SV = "SV"
    ADMIN = "管理者"


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole
    group_id: Optional[UUID] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    group_id: Optional[UUID] = None


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    role: UserRole
    group_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"