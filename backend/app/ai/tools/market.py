from typing import Dict, Any
from pydantic import BaseModel, Field
from app.ai.base_tool import BaseAITool
from app.ai.registry import register_tool
from app.ai.agri_services.market import market_service

class MarketPriceParams(BaseModel):
    crop_name: str = Field(..., description="Name of the crop to get price updates.")
    region: str = Field(default="Gujarat", description="Target region or market.")

class MarketPriceTool(BaseAITool):
    @property
    def name(self) -> str:
        return "market_price_assistant"

    @property
    def description(self) -> str:
        return "Fetches wholesale market prices, trends, and demand metrics for specific crops."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return MarketPriceParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        crop = params.get("crop_name", "Wheat")
        location = params.get("region", "Gujarat")
        
        # Invoke our dynamic MarketService
        market_res = await market_service.get_current_prices(crop, location)
        
        modal_p = market_res.get("modal_price_per_quintal", 2500.0)
        return {
            "crop": market_res.get("crop"),
            "region": market_res.get("location"),
            "modal_price_per_quintal": modal_p,
            "average_wholesale_price_inr_quintal": modal_p,
            "average_wholesale_price_usd_ton": modal_p,
            "unit": "/quintal",
            "currency": "₹",
            "weekly_trend": "upward" if "up" in market_res.get("best_selling_time", "").lower() else "stable",
            "demand_index": "High",
            "recommended_sales_strategy": market_res.get("best_selling_time"),
            "historical_trends": market_res.get("historical_trends", []),
            "provider": market_res.get("provider"),
            "status": "success"
        }

# Automatic registration
register_tool(MarketPriceTool())
