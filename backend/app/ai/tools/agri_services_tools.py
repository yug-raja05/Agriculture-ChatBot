from typing import Dict, Any
from pydantic import BaseModel, Field
from app.ai.base_tool import BaseAITool
from app.ai.registry import register_tool
from app.ai.agri_services.weather import weather_service
from app.ai.agri_services.market import market_service
from app.ai.agri_services.government import government_service
from app.ai.agri_services.notifications import notification_service
from app.ai.agri_services.reminders import reminder_service
from app.ai.agri_services.location import location_service

# --- 1. Weather Tool ---
class WeatherParams(BaseModel):
    latitude: float = Field(..., description="GPS latitude coordinate.")
    longitude: float = Field(..., description="GPS longitude coordinate.")

class WeatherTool(BaseAITool):
    @property
    def name(self) -> str:
        return "WeatherTool"

    @property
    def description(self) -> str:
        return "Fetches real-time weather conditions, forecasts, and irrigation/spraying recommendations."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return WeatherParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        res = weather_service.get_current_weather(params.get("latitude"), params.get("longitude"))
        return res

# --- 2. Market Tool ---
class MarketParams(BaseModel):
    crop_name: str = Field(..., description="Name of the crop.")
    location: str = Field(default="Gujarat", description="State or mandi district.")

class MarketTool(BaseAITool):
    @property
    def name(self) -> str:
        return "MarketTool"

    @property
    def description(self) -> str:
        return "Retrieves modal crop prices, mandi trends, and best selling time suggestions."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return MarketParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        res = market_service.get_current_prices(params.get("crop_name"), params.get("location"))
        return res

# --- 3. Government Scheme Tool ---
class GovParams(BaseModel):
    query: str = Field(default="", description="Search query keyword.")
    category: str = Field(default="", description="Subsidies or direct income support filter.")

class GovernmentSchemeTool(BaseAITool):
    @property
    def name(self) -> str:
        return "GovernmentSchemeTool"

    @property
    def description(self) -> str:
        return "Queries government loans, PM-Kisan registration steps, and crop insurance PMFBY deadlines."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return GovParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        res = government_service.search_schemes(params.get("query"), params.get("category"))
        return res

# --- 4. Notification Tool ---
class NotifyParams(BaseModel):
    recipient: str = Field(..., description="Email address or SMS phone number.")
    category: str = Field(..., description="Type of alert: Emergency, Weather, Reminder.")
    title: str = Field(..., description="Title of the message.")
    body: str = Field(..., description="Notification body content.")

class NotificationTool(BaseAITool):
    @property
    def name(self) -> str:
        return "NotificationTool"

    @property
    def description(self) -> str:
        return "Sends emergency weather alerts or disease advisories via SMS or Email."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return NotifyParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        res = await notification_service.send_notification(
            user_id=user_id,
            recipient=params.get("recipient"),
            category=params.get("category"),
            title=params.get("title"),
            body=params.get("body")
        )
        return res

# --- 5. Reminder Tool ---
class ReminderParams(BaseModel):
    category: str = Field(..., description="Reminder type: Sowing, Harvest, Irrigation.")
    title: str = Field(..., description="Reminder description.")
    target_timestamp: float = Field(..., description="Execution target epoch timestamp.")

class ReminderTool(BaseAITool):
    @property
    def name(self) -> str:
        return "ReminderTool"

    @property
    def description(self) -> str:
        return "Schedules custom alerts or warnings for farming actions (e.g. crop watering)."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return ReminderParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        res = await reminder_service.create_reminder(
            user_id=user_id,
            category=params.get("category"),
            title=params.get("title"),
            target_timestamp=params.get("target_timestamp")
        )
        return res

# --- 6. Location Tool ---
class LocationParams(BaseModel):
    latitude: float = Field(..., description="GPS latitude coordinate.")
    longitude: float = Field(..., description="GPS longitude coordinate.")

class LocationTool(BaseAITool):
    @property
    def name(self) -> str:
        return "LocationTool"

    @property
    def description(self) -> str:
        return "Locates nearest wholesale mandis, soil testing centers, and fertilizer shops."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return LocationParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        res = location_service.get_nearest_facilities(params.get("latitude"), params.get("longitude"))
        return res

# Auto-registrations
register_tool(WeatherTool())
register_tool(MarketTool())
register_tool(GovernmentSchemeTool())
register_tool(NotificationTool())
register_tool(ReminderTool())
register_tool(LocationTool())
