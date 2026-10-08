import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

class SessionContext(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    current_language: str = "en"
    current_location: str = "Gujarat"
    current_crop: Optional[str] = None
    current_season: str = "Kharif"
    last_active_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    session_expiry: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=2))
    recent_files: List[Dict[str, Any]] = []
    current_active_tool: Optional[str] = None
    current_ai_state: str = "idle"
    session_status: str = "active"

class SessionManager:
    """
    Session Manager Service. Saves and restores farmer sessions in MongoDB.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def create_session(self, user_id: str, location: str = "Gujarat", lang: str = "en") -> SessionContext:
        session = SessionContext(
            user_id=user_id,
            current_location=location,
            current_language=lang
        )
        await self.db["sessions"].insert_one(session.model_dump())
        return session

    async def get_session(self, session_id: str) -> Optional[SessionContext]:
        doc = await self.db["sessions"].find_one({"session_id": session_id, "session_status": "active"})
        if not doc:
            return None
        
        # Expiry check
        session = SessionContext(**doc)
        if datetime.now(timezone.utc) > session.session_expiry:
            await self.db["sessions"].update_one(
                {"session_id": session_id},
                {"$set": {"session_status": "expired"}}
            )
            return None
            
        # Update last active time
        await self.db["sessions"].update_one(
            {"session_id": session_id},
            {"$set": {"last_active_time": datetime.now(timezone.utc)}}
        )
        return session

    async def update_session_attributes(self, session_id: str, updates: Dict[str, Any]) -> bool:
        res = await self.db["sessions"].update_one(
            {"session_id": session_id},
            {"$set": updates}
        )
        return res.modified_count > 0

    async def terminate_session(self, session_id: str) -> bool:
        res = await self.db["sessions"].update_one(
            {"session_id": session_id},
            {"$set": {"session_status": "terminated"}}
        )
        return res.modified_count > 0
