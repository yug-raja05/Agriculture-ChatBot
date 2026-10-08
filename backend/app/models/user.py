from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr

class UserRole(str, Enum):
    ADMIN = "admin"
    FARMER = "farmer"
    AI_EXPERT = "ai_expert"
    AGRICULTURE_OFFICER = "agriculture_officer"

class UserDB(BaseModel):
    id: str = Field(alias="_id")
    email: EmailStr
    hashed_password: str
    roles: List[UserRole] = [UserRole.FARMER]
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
