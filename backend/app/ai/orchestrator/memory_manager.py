from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

class ConversationMemory(BaseModel):
    user_id: str
    user_name: Optional[str] = None
    farm_name: Optional[str] = None
    farm_size_hectares: float = 0.0
    location: str = "Gujarat"
    preferred_language: str = "en"
    preferred_units: str = "metric"
    crop_history: List[str] = []
    previous_diseases: List[str] = []
    soil_profile: Dict[str, Any] = {}
    favorite_crops: List[str] = []
    recent_questions: List[str] = []
    previous_recommendations: List[str] = []
    uploaded_reports: List[Dict[str, Any]] = []
    weather_history: List[Dict[str, Any]] = []
    market_interests: List[str] = []
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MemoryManager:
    """
    Memory Manager Service.
    Updates short/long term context properties in MongoDB `conversation_memory`.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_memory(self, user_id: str) -> ConversationMemory:
        doc = await self.db["conversation_memory"].find_one({"user_id": user_id})
        if not doc:
            memory = ConversationMemory(user_id=user_id)
            await self.db["conversation_memory"].insert_one(memory.model_dump())
            return memory
        return ConversationMemory(**doc)

    async def update_memory(self, user_id: str, updates: Dict[str, Any]) -> bool:
        updates["updated_at"] = datetime.now(timezone.utc)
        res = await self.db["conversation_memory"].update_one(
            {"user_id": user_id},
            {"$set": updates},
            upsert=True
        )
        return res.modified_count > 0 or res.upserted_id is not None

    async def append_crop_history(self, user_id: str, crop: str) -> None:
        await self.db["conversation_memory"].update_one(
            {"user_id": user_id},
            {
                "$addToSet": {"crop_history": crop, "favorite_crops": crop},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            },
            upsert=True
        )

    async def append_disease_history(self, user_id: str, disease: str) -> None:
        await self.db["conversation_memory"].update_one(
            {"user_id": user_id},
            {
                "$addToSet": {"previous_diseases": disease},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            },
            upsert=True
        )
