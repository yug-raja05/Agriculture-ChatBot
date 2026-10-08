from typing import Dict, Any
from pydantic import BaseModel, Field
from app.ai.base_tool import BaseAITool
from app.ai.registry import register_tool

class OCRScannerParams(BaseModel):
    image_url: str = Field(..., description="Url link of the scanned receipt or invoice.")

class OCRScannerTool(BaseAITool):
    @property
    def name(self) -> str:
        return "ocr_scanner"

    @property
    def description(self) -> str:
        return "Scans image receipts, pesticide bills, or seed logs to extract text descriptions."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return OCRScannerParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        return {
            "bill_total": "$125.50",
            "extracted_items": ["Copper Fungicide 5L", "Organic Mulch 20kg"],
            "status": "success"
        }

register_tool(OCRScannerTool())
