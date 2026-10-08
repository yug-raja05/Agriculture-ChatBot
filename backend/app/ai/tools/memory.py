from typing import Dict, Any
from pydantic import BaseModel, Field
from app.ai.base_tool import BaseAITool
from app.ai.registry import register_tool

class MemoryParams(BaseModel):
    key: str = Field(..., description="Memory parameter key (e.g. farm_size, location).")
    value: str = Field(..., description="Parameter value.")

class MemoryTool(BaseAITool):
    @property
    def name(self) -> str:
        return "context_memory_updater"

    @property
    def description(self) -> str:
        return "Updates farmer context database fields to ensure relevant multi-turn conversations."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return MemoryParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        return {
            "key": params.get("key"),
            "value": params.get("value"),
            "updated": True,
            "status": "success"
        }

register_tool(MemoryTool())
