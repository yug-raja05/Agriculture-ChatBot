import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from app.ai.base_tool import BaseAITool
from app.ai.registry import register_tool
from app.ai.agri_services.weather import weather_service
from app.core.database import db_manager

logger = logging.getLogger(__name__)

class WeatherAdvisorParams(BaseModel):
    location: Optional[str] = Field(default=None, description="City or region name mentioned by user (e.g. Ahmedabad).")
    latitude: Optional[float] = Field(default=None, description="GPS latitude coordinate.")
    longitude: Optional[float] = Field(default=None, description="GPS longitude coordinate.")

class WeatherAdvisorTool(BaseAITool):
    @property
    def name(self) -> str:
        return "weather_advisor"

    @property
    def description(self) -> str:
        return "Fetches real-time weather conditions, forecasts, and irrigation/spraying recommendations using city name or coordinates."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return WeatherAdvisorParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        loc = params.get("location")
        lat = params.get("latitude")
        lon = params.get("longitude")
        
        # Load user profile for fallback coordinates or locations
        db = db_manager.db
        profile = None
        if db is not None and user_id:
            try:
                profile = await db["profiles"].find_one({"user_id": user_id})
            except Exception as e:
                logger.error(f"Error fetching user profile in weather tool: {e}")

        # Location lookup priority resolving:
        # 1. Location argument (city) from parameter
        # 2. Farm saved location from profile
        # 3. GPS Coordinates parameter
        # 4. GPS Coordinates from profile
        
        resolved_city = None
        resolved_lat = None
        resolved_lon = None
        
        if loc and str(loc).strip() != "":
            resolved_city = str(loc).strip()
            logger.info(f"[Weather Tool] Priority 1 Match: City name '{resolved_city}'")
        elif profile and profile.get("location") and str(profile.get("location")).strip() not in ["", "Unknown Location"]:
            resolved_city = str(profile.get("location")).strip()
            logger.info(f"[Weather Tool] Priority 2 Match: Profile location '{resolved_city}'")
        elif lat is not None and lon is not None:
            resolved_lat = float(lat)
            resolved_lon = float(lon)
            logger.info(f"[Weather Tool] Priority 3 Match: Coords {resolved_lat}, {resolved_lon}")
        elif profile and profile.get("latitude") is not None and profile.get("longitude") is not None:
            resolved_lat = float(profile.get("latitude"))
            resolved_lon = float(profile.get("longitude"))
            logger.info(f"[Weather Tool] Priority 4 Match: Profile coords {resolved_lat}, {resolved_lon}")
        else:
            resolved_city = "Bangalore"
            logger.info(f"[Weather Tool] Priority 5 Fallback: Default city '{resolved_city}'")

        # Execute query dynamically
        try:
            if resolved_city:
                logger.info(f"[Weather Tool] Invoking weather_service for city: '{resolved_city}'")
                weather_res = await weather_service.get_current_weather(resolved_city)
            elif resolved_lat is not None and resolved_lon is not None:
                logger.info(f"[Weather Tool] Invoking weather_service for coordinates: {resolved_lat}, {resolved_lon}")
                weather_res = await weather_service.get_current_weather(resolved_lat, resolved_lon)
            else:
                weather_res = await weather_service.get_current_weather("Bangalore")

            weather_res["status"] = "success"
            return weather_res

        except Exception as e:
            logger.error(f"[Weather Tool] Service execution failed: {e}")
            return {
                "error": f"Failed to retrieve weather reports dynamically: {str(e)}",
                "status": "failed"
            }

# Automatic registry injection
register_tool(WeatherAdvisorTool())
