from typing import Dict, Any
from pydantic import BaseModel, Field
from app.ai.base_tool import BaseAITool
from app.ai.registry import register_tool
from app.ai.ml_framework.registry import ml_model_registry
from app.ai.ml_framework.monitoring import model_monitoring_service

class FertilizerParams(BaseModel):
    crop_name: str = Field(..., description="Target crop.")
    soil_type: str = Field(default="Loamy", description="Farm soil texture class.")

class FertilizerTool(BaseAITool):
    @property
    def name(self) -> str:
        return "fertilizer_advisor"

    @property
    def description(self) -> str:
        return "Calculates fertilizer ratio requirements based on crop and soil parameters."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return FertilizerParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        # 1. Fetch dynamic active model from Registry
        model = ml_model_registry.GetActiveModel("fertilizer")
        if not model:
            return {"error": "No active fertilizer recommendation model found.", "status": "failed"}

        # 2. Execute prediction
        pred = model.predict(params)
        
        # 3. Log metrics to monitoring logs
        await model_monitoring_service.log_prediction(
            category="fertilizer",
            model_name=model.name,
            input_data=params,
            output_data=pred,
            inference_time_ms=model.inference_latency_ms,
            success=True
        )

        return {
            "recommended_fertilizer": pred.get("recommended_fertilizer", "NPK 19-19-19"),
            "dosage": pred.get("dosage", "50kg per Hectare"),
            "active_model_used": model.name,
            "model_version": model.version,
            "status": "success"
        }

register_tool(FertilizerTool())
