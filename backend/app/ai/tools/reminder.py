import time
from typing import Dict, Any
from pydantic import BaseModel, Field
from app.ai.base_tool import BaseAITool
from app.ai.registry import register_tool
from app.ai.agri_services.reminders import reminder_service
from app.core.database import db_manager

class ReminderParams(BaseModel):
    task: str = Field(..., description="Action reminder task (e.g. spray insecticide, check moisture).")
    date_str: str = Field(..., description="Target date and time schedule.")
    target_timestamp: float = Field(default=0.0, description="Epoch target timestamp for schedule trigger.")

class ReminderTool(BaseAITool):
    @property
    def name(self) -> str:
        return "reminder_tool"

    @property
    def description(self) -> str:
        return "Configures reminders for crop watering schedules and chemical treatments."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return ReminderParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        task = params.get("task")
        target_ts = params.get("target_timestamp", 0.0)
        if target_ts <= 0.0:
            # Fallback: Schedule 24 hours from now if no valid epoch is provided
            target_ts = time.time() + 86400
            
        # Invoke our dynamic ReminderService saving logs into active MongoDB instance
        db = db_manager.db
        res = await reminder_service.create_reminder(
            user_id=user_id,
            category="Irrigation" if "water" in task.lower() else "Fertilizer",
            title=task,
            target_timestamp=target_ts,
            db=db
        )
        
        return {
            "task": res.get("title"),
            "date": params.get("date_str"),
            "reminder_id": res.get("_id"),
            "reminder_configured": True,
            "status": "success"
        }

# Automatic registration
register_tool(ReminderTool())
