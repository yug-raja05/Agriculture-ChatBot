from typing import Dict, Any
from pydantic import BaseModel, Field
from app.ai.base_tool import BaseAITool
from app.ai.registry import register_tool
from app.ai.ml_framework.registry import ml_model_registry
from app.ai.ml_framework.monitoring import model_monitoring_service

class YieldPredictorParams(BaseModel):
    crop_name: str = Field(..., description="Target crop.")
    area_hectares: float = Field(..., description="Size of the cultivated land.")

class YieldPredictorTool(BaseAITool):
    @property
    def name(self) -> str:
        return "yield_predictor"

    @property
    def description(self) -> str:
        return "Predicts crop harvest yield weights based on soil and acreage parameters."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return YieldPredictorParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        # 1. Fetch dynamic active model from Registry
        model = ml_model_registry.GetActiveModel("yield")
        if not model:
            return {"error": "No active yield prediction model found.", "status": "failed"}

        # 2. Execute prediction
        pred = model.predict(params)
        
        # 3. Log metrics to monitoring logs
        await model_monitoring_service.log_prediction(
            category="yield",
            model_name=model.name,
            input_data=params,
            output_data=pred,
            inference_time_ms=model.inference_latency_ms,
            success=True
        )

        # Scale mock prediction by acres
        pred_value = round(pred.get("expected_yield_metric_tons", 4.2) * params.get("area_hectares", 1.0) / 10.0, 2)

        return {
            "expected_yield_metric_tons": pred_value,
            "active_model_used": model.name,
            "model_version": model.version,
            "status": "success"
        }

register_tool(YieldPredictorTool())
