import time
import logging
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class ReminderService:
    """
    Farming Reminder Engine.
    Configures alerts for watering, fertilizing schedules, and sowing tasks.
    """
    def __init__(self):
        pass

    async def create_reminder(
        self,
        user_id: str,
        category: str,  # Sowing, Harvest, Irrigation, Fertilizer, Pesticide
        title: str,
        target_timestamp: float,
        is_recurring: bool = False,
        recurrence_interval_days: int = 0,
        db: Optional[AsyncIOMotorDatabase] = None
    ) -> Dict[str, Any]:
        """
        Registers a new reminder in MongoDB collection.
        """
        logger.info(f"Creating reminder title='{title}', category={category} for user={user_id}...")
        
        reminder_entry = {
            "user_id": user_id,
            "category": category,
            "title": title,
            "target_timestamp": target_timestamp,
            "is_recurring": is_recurring,
            "recurrence_interval_days": recurrence_interval_days,
            "completed": False,
            "created_at": time.time()
        }

        if db is not None:
            try:
                res = await db["reminders"].insert_one(reminder_entry)
                reminder_entry["_id"] = str(res.inserted_id)
            except Exception as e:
                logger.error(f"Failed to save reminders: {str(e)}")

        return reminder_entry

    async def get_active_reminders(self, user_id: str, db: AsyncIOMotorDatabase) -> List[Dict[str, Any]]:
        reminders = []
        try:
            cursor = db["reminders"].find({"user_id": user_id, "completed": False}).sort("target_timestamp", 1)
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                reminders.append(doc)
        except Exception as e:
            logger.error(f"Failed to fetch reminders: {str(e)}")
        return reminders

reminder_service = ReminderService()
