from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class PredictionType(str, Enum):
    CROP_RECOMMENDATION = "crop_recommendation"
    DISEASE_DETECTION = "disease_detection"
    YIELD_PREDICTION = "yield_prediction"
    SOIL_ANALYSIS = "soil_analysis"

class PredictionRecordDB(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    prediction_type: PredictionType
    input_data: Dict[str, Any]
    output_result: Dict[str, Any]
    confidence_score: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
