from typing import Dict, Any
from pydantic import BaseModel, Field
from app.ai.base_tool import BaseAITool
from app.ai.registry import register_tool

class TranslationParams(BaseModel):
    text: str = Field(..., description="Agricultural text to translate.")
    target_lang: str = Field(..., description="Target language (Hindi, English, Gujarati).")

class TranslationTool(BaseAITool):
    @property
    def name(self) -> str:
        return "translation_tool"

    @property
    def description(self) -> str:
        return "Translates agricultural terms or advisory text into farmer's preferred language."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return TranslationParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        return {
            "translated_text": f"[{params.get('target_lang')}] {params.get('text')}",
            "status": "success"
        }

register_tool(TranslationTool())
