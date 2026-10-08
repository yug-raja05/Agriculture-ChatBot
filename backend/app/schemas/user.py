from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    roles: Optional[List[UserRole]] = [UserRole.FARMER]

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str = Field(default="", validation_alias="_id")
    email: EmailStr
    roles: List[UserRole] = [UserRole.FARMER]
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        from_attributes = True
