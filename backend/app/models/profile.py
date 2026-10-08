from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

class SoilMetrics(BaseModel):
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    ph: Optional[float] = None
    moisture: Optional[float] = None

class FarmerProfileDB(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    fullname: str
    phone: Optional[str] = None
    location: Optional[str] = None  # e.g., "District, State"
    farm_size_hectares: Optional[float] = None
    primary_crops: list[str] = []
    soil_profile: Optional[SoilMetrics] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
