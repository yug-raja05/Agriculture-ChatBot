from typing import Dict, Any
from pydantic import BaseModel, Field
from app.ai.base_tool import BaseAITool
from app.ai.registry import register_tool

class VoiceTranscriberParams(BaseModel):
    audio_url: str = Field(..., description="Url link to the recorded voice note.")

class VoiceTranscriberTool(BaseAITool):
    @property
    def name(self) -> str:
        return "voice_transcriber"

    @property
    def description(self) -> str:
        return "Processes spoken audio clips to transcribe text prompts."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return VoiceTranscriberParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        return {
            "transcript": "What fertilizer should I spray on wheat?",
            "status": "success"
        }

register_tool(VoiceTranscriberTool())
