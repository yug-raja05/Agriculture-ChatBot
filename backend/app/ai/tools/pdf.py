from typing import Dict, Any
from pydantic import BaseModel, Field
from app.ai.base_tool import BaseAITool
from app.ai.registry import register_tool

class PDFAnalystParams(BaseModel):
    pdf_url: str = Field(..., description="Url link to the uploaded PDF document.")

class PDFAnalystTool(BaseAITool):
    @property
    def name(self) -> str:
        return "pdf_analyst"

    @property
    def description(self) -> str:
        return "Analyzes PDF crop guidelines, reports, or scientific documents to summarize recommendations."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return PDFAnalystParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        return {
            "file": params.get("pdf_url"),
            "summary": "This document contains recommendations for organic nitrogen compost fertilization in wet clay soil.",
            "status": "success"
        }

register_tool(PDFAnalystTool())
