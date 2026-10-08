from typing import Dict, Any
from pydantic import BaseModel, Field
from app.ai.base_tool import BaseAITool
from app.ai.registry import register_tool
from app.ai.ml_framework.registry import ml_model_registry
from app.ai.ml_framework.monitoring import model_monitoring_service

class CropRecommenderParams(BaseModel):
    nitrogen: float = Field(..., description="Soil nitrogen content (mg/kg).")
    phosphorus: float = Field(..., description="Soil phosphorus content (mg/kg).")
    potassium: float = Field(..., description="Soil potassium content (mg/kg).")
    ph: float = Field(..., description="Soil pH value.")
    moisture: float = Field(..., description="Soil moisture percentage.")

class CropRecommenderTool(BaseAITool):
    @property
    def name(self) -> str:
        return "crop_recommender"

    @property
    def description(self) -> str:
        return "Recommends optimal crop options based on chemical and physical soil profiles."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return CropRecommenderParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        # 1. Fetch dynamic active model from Registry
        model = ml_model_registry.GetActiveModel("crop")
        if not model:
            return {"error": "No active crop recommendation model found.", "status": "failed"}

        # 2. Execute prediction
        pred = model.predict(params)
        
        # 3. Log metrics to monitoring logs
        await model_monitoring_service.log_prediction(
            category="crop",
            model_name=model.name,
            input_data=params,
            output_data=pred,
            inference_time_ms=model.inference_latency_ms,
            success=True
        )

        return {
            "recommended_crops": [
                {"crop": pred.get("crop_recommendation", "Wheat"), "confidence": pred.get("confidence", 0.90), "days_to_harvest": 110}
            ],
            "active_model_used": model.name,
            "model_version": model.version,
            "status": "success"
        }

register_tool(CropRecommenderTool())
