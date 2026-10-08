from typing import Dict, Any
from pydantic import BaseModel, Field
from app.ai.base_tool import BaseAITool
from app.ai.registry import register_tool

class NotifParams(BaseModel):
    alert_title: str = Field(..., description="Alert description.")
    scheduled_time: str = Field(..., description="Target time string.")

class NotifTool(BaseAITool):
    @property
    def name(self) -> str:
        return "notification_scheduler"

    @property
    def description(self) -> str:
        return "Schedules custom alerts or warnings for farming actions (e.g. fertilizer spraying schedules)."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return NotifParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        return {
            "notification_id": "notif_123",
            "scheduled": True,
            "status": "success"
        }

register_tool(NotifTool())
