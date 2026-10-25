from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from .common import Email

from ..models.user import UserRole


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: Email
    password: str = Field(min_length=8, max_length=128)
    phone: Optional[str] = Field(default=None, max_length=32)


class UserLogin(BaseModel):
    email: Email
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    phone: Optional[str] = Field(default=None, max_length=32)


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    id: int
    name: str
    email: Email
    role: UserRole
    phone: Optional[str] = None
    is_active: bool
    department_id: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class AdminRoleUpdate(BaseModel):
    role: UserRole
    department_id: Optional[int] = None
    is_active: Optional[bool] = None
