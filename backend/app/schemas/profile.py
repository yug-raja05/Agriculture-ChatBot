from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.profile import SoilMetrics

class ProfileCreate(BaseModel):
    fullname: str
    phone: Optional[str] = None
    location: Optional[str] = None
    farm_size_hectares: Optional[float] = None
    primary_crops: List[str] = []
    soil_profile: Optional[SoilMetrics] = None

class ProfileUpdate(BaseModel):
    fullname: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    farm_size_hectares: Optional[float] = None
    primary_crops: Optional[List[str]] = None
    soil_profile: Optional[SoilMetrics] = None

class ProfileResponse(BaseModel):
    id: str
    user_id: str
    fullname: str
    phone: Optional[str] = None
    location: Optional[str] = None
    farm_size_hectares: Optional[float] = None
    primary_crops: List[str]
    soil_profile: Optional[SoilMetrics] = None

    class Config:
        from_attributes = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "profile_1",
                "user_id": "user_1",
                "fullname": "John Doe",
                "phone": "+1234567890",
                "location": "Central Valley, California",
                "farm_size_hectares": 12.5,
                "primary_crops": ["Almonds", "Grapes"],
                "soil_profile": {
                    "nitrogen": 45.2,
                    "phosphorus": 22.1,
                    "potassium": 120.5,
                    "ph": 6.8,
                    "moisture": 40.0
                }
            }
        }
