from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ExtractedEntities(BaseModel):
    crop: Optional[str] = None
    disease: Optional[str] = None
    pest: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    season: Optional[str] = None
    weather: Optional[str] = None
    temperature: Optional[str] = None
    rainfall: Optional[str] = None
    soil_type: Optional[str] = None
    fertilizer: Optional[str] = None
    gov_scheme: Optional[str] = None
    market: Optional[str] = None
    language: Optional[str] = None
    file_type: Optional[str] = None
    image_type: Optional[str] = None

class IntentAnalysisResult(BaseModel):
    primary_intent: str
    secondary_intents: List[str] = []
    confidence_score: float = 1.0
    entities: ExtractedEntities = Field(default_factory=ExtractedEntities)

class IntentAnalyzer:
    """
    Intent Analyzer & Entity Extraction Placeholders Service.
    Parses multi-intent inputs and returns parsed tags.
    """
    def __init__(self):
        pass

    def analyze_intent(self, query: str) -> IntentAnalysisResult:
        """
        Tags query text with categorized intents. Supports multi-intent queries.
        """
        lower_query = query.lower()
        intents = []
        entities = ExtractedEntities()

        # Simple pattern checks
        if "hello" in lower_query or "hi " in lower_query or "hey" in lower_query:
            intents.append("Greeting")
            
        if "weather" in lower_query or "rain" in lower_query or "temp" in lower_query:
            intents.append("Weather Query")
            entities.weather = "forecast"
            
        if "disease" in lower_query or "leaf" in lower_query or "spots" in lower_query or "blight" in lower_query:
            intents.append("Disease Query")
            entities.disease = "leaf spots"
            
        if "crop" in lower_query or "recommend" in lower_query or "grow" in lower_query:
            intents.append("Crop Recommendation")
            for c in ["cotton", "wheat", "maize", "rice", "soybeans"]:
                if c in lower_query:
                    entities.crop = c.capitalize()
                    
        if "price" in lower_query or "market" in lower_query or "cost" in lower_query:
            intents.append("Market Query")
            entities.market = "wholesale"
            
        if "scheme" in lower_query or "kisan" in lower_query or "subsid" in lower_query:
            intents.append("Government Scheme Query")
            entities.gov_scheme = "PM-KISAN"
            
        if "fertilizer" in lower_query or "compost" in lower_query:
            intents.append("Soil Analysis")
            entities.fertilizer = "NPK Compound"

        # Defaults
        if not intents:
            intents.append("General Conversation")

        return IntentAnalysisResult(
            primary_intent=intents[0],
            secondary_intents=intents[1:] if len(intents) > 1 else [],
            confidence_score=0.95,
            entities=entities
        )
