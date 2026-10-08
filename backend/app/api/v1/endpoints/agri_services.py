import time
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.api.deps import get_db, get_current_user
from app.models.user import UserDB
from app.ai.agri_services.weather import weather_service
from app.ai.agri_services.market import market_service
from app.ai.agri_services.government import government_service
from app.ai.agri_services.notifications import notification_service
from app.ai.agri_services.reminders import reminder_service
from app.ai.agri_services.location import location_service
from app.ai.agri_services.analytics import analytics_service
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()

# Schema definitions
class CurrentWeatherRequest(BaseModel):
    latitude: float = Field(..., description="GPS latitude coordinate.")
    longitude: float = Field(..., description="GPS longitude coordinate.")

class ForecastWeatherRequest(BaseModel):
    latitude: float = Field(..., description="GPS latitude coordinate.")
    longitude: float = Field(..., description="GPS longitude coordinate.")

class WeatherByLocationRequest(BaseModel):
    location: str = Field(..., description="Location name (e.g. city, state).")

class WeatherByCoordinatesRequest(BaseModel):
    latitude: float = Field(..., description="GPS latitude coordinate.")
    longitude: float = Field(..., description="GPS longitude coordinate.")

class MarketPricesRequest(BaseModel):
    crop_name: str = Field(..., description="Target crop (e.g. Wheat).")
    location: str = Field(default="Gujarat", description="State or market location.")

class MarketBatchPricesRequest(BaseModel):
    crops: List[str] = Field(default=["Wheat", "Maize", "Soybeans"], description="List of target crops.")
    location: str = Field(default="Gujarat", description="State or market location.")

class MarketMandisRequest(BaseModel):
    crop_name: Optional[str] = Field(default=None, description="Optional target crop filter.")
    location: Optional[str] = Field(default=None, description="Optional location or state filter.")
    limit: int = Field(default=50, description="Max records to return.")

class GovernmentSearchRequest(BaseModel):
    query: str = Field(default="", description="Search keywords (e.g. PM-Kisan).")
    category: str = Field(default="", description="Category filter.")

class NotificationSendRequest(BaseModel):
    recipient: str = Field(..., description="Email or phone number.")
    category: str = Field(..., description="Category: Weather, Disease, Market, Reminder, System.")
    title: str = Field(..., description="Notification header.")
    body: str = Field(..., description="Message body.")

class ReminderCreateRequest(BaseModel):
    category: str = Field(..., description="Reminder type: Sowing, Harvest, Irrigation, Fertilizer.")
    title: str = Field(..., description="Reminder description.")
    target_timestamp: float = Field(..., description="Execution epoch timestamp.")
    is_recurring: bool = Field(default=False, description="Recurring alert.")
    interval_days: int = Field(default=0, description="Interval in days.")

class CropRecommendRequest(BaseModel):
    nitrogen: float = Field(default=50.0)
    phosphorus: float = Field(default=35.0)
    potassium: float = Field(default=110.0)
    ph: float = Field(default=6.5)
    moisture: float = Field(default=35.0)
    soil_type: str = Field(default="Loamy")
    season: str = Field(default="Kharif")
    location: str = Field(default="Gujarat")

# Background Tasks Helpers
def bg_refresh_weather_cache(lat: float, lon: float):
    # Simulate caching weather parameters in background
    pass

def bg_update_market_prices(crop: str, location: str):
    # Simulate updating market metrics in background
    pass


# --- Weather routes ---

@router.post("/weather/current")
async def get_current_weather(
    req: CurrentWeatherRequest,
    bg_tasks: BackgroundTasks,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    bg_tasks.add_task(bg_refresh_weather_cache, req.latitude, req.longitude)
    
    res = await weather_service.get_current_weather(req.latitude, req.longitude)
    # Log weather query in history
    try:
        await db["weather_history"].insert_one({
            "user_id": current_user.id,
            "latitude": req.latitude,
            "longitude": req.longitude,
            "temp": res.get("temperature"),
            "timestamp": time.time()
        })
    except Exception:
        pass
    return res

@router.post("/weather/forecast")
async def get_weather_forecast(
    req: ForecastWeatherRequest,
    current_user: UserDB = Depends(get_current_user)
):
    res = await weather_service.get_forecast(req.latitude, req.longitude)
    return res

@router.get("/weather/current")
async def get_current_weather_get(
    location: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    current_user: UserDB = Depends(get_current_user)
):
    try:
        if location:
            return await weather_service.get_current_weather(location)
        elif latitude is not None and longitude is not None:
            return await weather_service.get_current_weather(latitude, longitude)
        else:
            raise HTTPException(status_code=400, detail="Missing location or coordinates query parameters.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/weather/forecast")
async def get_weather_forecast_get(
    location: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    current_user: UserDB = Depends(get_current_user)
):
    try:
        if location:
            return await weather_service.get_forecast(location)
        elif latitude is not None and longitude is not None:
            return await weather_service.get_forecast(latitude, longitude)
        else:
            raise HTTPException(status_code=400, detail="Missing location or coordinates query parameters.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/weather/by-location")
async def post_weather_by_location(
    req: WeatherByLocationRequest,
    current_user: UserDB = Depends(get_current_user)
):
    try:
        return await weather_service.get_current_weather(req.location)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/weather/by-coordinates")
async def post_weather_by_coordinates(
    req: WeatherByCoordinatesRequest,
    current_user: UserDB = Depends(get_current_user)
):
    try:
        return await weather_service.get_current_weather(req.latitude, req.longitude)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Market routes ---

@router.post("/market/prices")
async def get_market_prices(
    req: MarketPricesRequest,
    bg_tasks: BackgroundTasks,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    bg_tasks.add_task(bg_update_market_prices, req.crop_name, req.location)
    
    res = await market_service.get_current_prices(req.crop_name, req.location)
    # Log to MongoDB market_history collection
    try:
        await db["market_history"].insert_one({
            "user_id": current_user.id,
            "crop": req.crop_name,
            "modal_price": res.get("modal_price_per_quintal"),
            "timestamp": time.time()
        })
    except Exception:
        pass
    return res

@router.post("/market/batch-prices")
async def get_market_batch_prices(
    req: MarketBatchPricesRequest,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Returns market price quotes for multiple crops in a single efficient call.
    """
    results = []
    for crop in req.crops:
        try:
            res = await market_service.get_current_prices(crop, req.location)
            results.append(res)
        except Exception:
            pass
    return results

@router.get("/market/history")
async def get_market_price_history(
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    history = []
    try:
        cursor = db["market_history"].find().sort("timestamp", -1).limit(10)
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            history.append(doc)
    except Exception:
        pass
    return history

@router.post("/market/mandis")
async def get_live_mandis_post(
    req: MarketMandisRequest,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Returns live Mandi market records from the Government API or national mandi registry.
    """
    return await market_service.get_live_mandis(req.crop_name, req.location, req.limit)

@router.get("/market/mandis")
async def get_live_mandis_get(
    crop_name: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 50,
    current_user: UserDB = Depends(get_current_user)
):
    """
    GET method for fetching live Mandi market records.
    """
    return await market_service.get_live_mandis(crop_name, location, limit)


# --- Government routes ---

@router.post("/government/search")
async def search_government_schemes(
    req: GovernmentSearchRequest,
    current_user: UserDB = Depends(get_current_user)
):
    res = await government_service.search_schemes(req.query, req.category)
    return res


# --- Notification routes ---

@router.post("/notifications/send")
async def send_notification(
    req: NotificationSendRequest,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    res = await notification_service.send_notification(
        user_id=current_user.id,
        recipient=req.recipient,
        category=req.category,
        title=req.title,
        body=req.body,
        db=db
    )
    return res

@router.get("/notifications")
async def list_user_notifications(
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    notifications = []
    try:
        cursor = db["notifications"].find({"user_id": current_user.id}).sort("timestamp", -1)
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            notifications.append(doc)
    except Exception:
        pass
    return notifications


# --- Reminder routes ---

@router.post("/reminders/create")
async def create_reminder(
    req: ReminderCreateRequest,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    res = await reminder_service.create_reminder(
        user_id=current_user.id,
        category=req.category,
        title=req.title,
        target_timestamp=req.target_timestamp,
        is_recurring=req.is_recurring,
        recurrence_interval_days=req.interval_days,
        db=db
    )
    return res

@router.get("/reminders")
async def get_active_reminders(
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    res = await reminder_service.get_active_reminders(current_user.id, db)
    return res


# --- Crop Recommendation AI route ---

@router.post("/crop/recommend")
async def recommend_crops(
    req: CropRecommendRequest,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Live AI & Gemini crop recommendation based on location, climate, and soil chemistry.
    """
    import re
    import json
    from app.ai.agent_executor import get_state_crop_recommendations
    from app.ai.llm import get_llm

    # 1. Try Google Gemini API for real-time generative recommendations
    llm = get_llm()
    prompt = f"""You are AgriGenius AI, a leading Indian agronomist and agricultural scientist.
Recommend the top 3 best matching and most profitable crops for a farm in {req.location}, India with the following soil and climate specifications:
- Location: {req.location}
- Soil Type: {req.soil_type}
- Season: {req.season}
- Nitrogen (N): {req.nitrogen} mg/kg
- Phosphorus (P): {req.phosphorus} mg/kg
- Potassium (K): {req.potassium} mg/kg
- pH: {req.ph}
- Moisture: {req.moisture}%

Return your recommendation as a JSON object with this exact structure:
{{
  "crops": [
    {{"name": "Crop Name", "confidence": 0.95, "score": "Optimal Fit", "harvest": "110-120 days", "reason": "Specific agronomic reason for this crop in {req.location}"}},
    {{"name": "Crop Name 2", "confidence": 0.88, "score": "High Fit", "harvest": "90-100 days", "reason": "Specific agronomic reason"}},
    {{"name": "Crop Name 3", "confidence": 0.79, "score": "Moderate Fit", "harvest": "120-130 days", "reason": "Specific agronomic reason"}}
  ],
  "healthScore": "Excellent",
  "advice": "Actionable fertilizer and crop care advice for {req.location}."
}}
"""
    try:
        raw_res = llm._call(prompt)
        json_match = re.search(r"\{[\s\S]*\}", raw_res)
        if json_match:
            parsed = json.loads(json_match.group(0))
            if "crops" in parsed and len(parsed["crops"]) > 0:
                return parsed
    except Exception as e:
        logger.warning(f"Gemini crop recommendation parsing failed ({e}). Using regional model.")

    # 2. Regional Agronomic Model fallback
    rec = get_state_crop_recommendations(req.location, req.nitrogen, req.phosphorus, req.potassium, req.ph, req.soil_type)
    crops_formatted = []
    for c in rec.get("crops", []):
        crops_formatted.append({
            "name": c["name"],
            "confidence": round(c.get("compatibility", 90) / 100, 2),
            "score": "Optimal Fit" if c.get("compatibility", 90) >= 92 else "High Fit",
            "harvest": c.get("maturity_days", "110-130 days"),
            "reason": c.get("reason", "")
        })
    return {
        "crops": crops_formatted,
        "healthScore": "Optimal",
        "advice": f"Soil NPK profile and pH in {req.location} are well-suited for {rec.get('crops', [{}])[0].get('name', 'these crops')}."
    }
