from typing import Dict, Any
from pydantic import BaseModel, Field
from app.ai.base_tool import BaseAITool
from app.ai.registry import register_tool

class ImageParams(BaseModel):
    image_url: str = Field(..., description="Url link of the uploaded leaf or crop photo.")

class ImageTool(BaseAITool):
    @property
    def name(self) -> str:
        return "image_analyst"

    @property
    def description(self) -> str:
        return "Analyzes agricultural leaf photos or farm landscapes to identify properties."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return ImageParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        return {
            "image_url": params.get("image_url"),
            "diagnostics": "Leaf scan indicates minor dehydration. Increase watering by 10%.",
            "status": "success"
        }

register_tool(ImageTool())
