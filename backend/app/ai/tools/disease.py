from typing import Dict, Any
from pydantic import BaseModel, Field
from app.ai.base_tool import BaseAITool
from app.ai.registry import register_tool
from app.ai.plant_health.vision import disease_prediction_service

class DiseaseDetectorParams(BaseModel):
    image_url: str = Field(..., description="Url of the uploaded leaf or plant image.")
    plant_part: str = Field(default="Leaf", description="Plant section scanned: Leaf, Stem, Fruit.")

class DiseaseDetectorTool(BaseAITool):
    @property
    def name(self) -> str:
        return "plant_disease_detector"

    @property
    def description(self) -> str:
        return "Analyzes plant images to diagnose diseases and recommend treatment regimens."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return DiseaseDetectorParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        image_url = params.get("image_url")
        plant_part = params.get("plant_part", "Leaf")
        
        # Invoke computer vision prediction service dynamically
        pre_meta = {"width": 224, "height": 224, "preprocessed": True, "image_url": image_url}
        pred = disease_prediction_service.predict_disease(pre_meta, plant_part)
        
        return {
            "image_url": image_url,
            "diagnosis": pred.get("disease_name"),
            "confidence": pred.get("confidence"),
            "severity": pred.get("severity"),
            "treatment": [
                pred.get("treatment", {}).get("organic", ""),
                pred.get("treatment", {}).get("chemical", ""),
                pred.get("treatment", {}).get("prevention", "")
            ],
            "status": "success"
        }

# Automatic registration
register_tool(DiseaseDetectorTool())
