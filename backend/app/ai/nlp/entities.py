import re
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class NLPContextEntities(BaseModel):
    crop: Optional[str] = None
    disease: Optional[str] = None
    pest: Optional[str] = None
    insect: Optional[str] = None
    fertilizer: Optional[str] = None
    soil_type: Optional[str] = None
    season: Optional[str] = None
    location: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    weather: Optional[str] = None
    temperature: Optional[str] = None
    rainfall: Optional[str] = None
    humidity: Optional[str] = None
    wind: Optional[str] = None
    market: Optional[str] = None
    gov_scheme: Optional[str] = None
    farmer_name: Optional[str] = None
    farm_name: Optional[str] = None
    farm_size: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    chemical: Optional[str] = None
    organic_product: Optional[str] = None
    medicine: Optional[str] = None
    equipment: Optional[str] = None
    language: Optional[str] = None
    document_type: Optional[str] = None
    image_type: Optional[str] = None

class EntityExtractor:
    """
    Hybrid Entity Extractor combining pattern rule matchers, custom dictionaries, and spaCy NER placeholders.
    """
    def __init__(self):
        # Custom keyword directories
        self.crops = ["wheat", "cotton", "rice", "maize", "soybeans", "tomatoes", "potato"]
        self.diseases = ["blight", "spots", "rot", "mildew", "rust"]
        self.fertilizers = ["npk", "urea", "compost", "phosphate", "manure"]
        self.soils = ["clay", "sandy", "loamy", "black soil", "alluvial"]
        self.chemicals = ["copper fungicide", "glyphosate", "malathion", "pesticide"]
        self.states = ["gujarat", "punjab", "haryana", "maharashtra", "uttar pradesh"]

    def extract_entities(self, text: str) -> NLPContextEntities:
        lower_text = text.lower()
        ent = NLPContextEntities()

        # 1. Rules-based regex extractions
        for c in self.crops:
            if c in lower_text:
                ent.crop = c.capitalize()
                break

        for d in self.diseases:
            if d in lower_text:
                ent.disease = d.capitalize()
                break

        for f in self.fertilizers:
            if f in lower_text:
                ent.fertilizer = f.upper()
                break

        for s in self.soils:
            if s in lower_text:
                ent.soil_type = s.capitalize()
                break

        for chem in self.chemicals:
            if chem in lower_text:
                ent.chemical = chem.capitalize()
                break

        for st in self.states:
            if st in lower_text:
                ent.state = st.capitalize()
                break

        # 2. Extract standard patterns
        size_match = re.search(r"(\d+(\.\d+)?)\s*(acres|hectares|bighas)", lower_text)
        if size_match:
            ent.farm_size = size_match.group(0)

        temp_match = re.search(r"(\d+)\s*(c|f|degrees|celsius)", lower_text)
        if temp_match:
            ent.temperature = temp_match.group(0)

        # 3. Handle standard date patterns
        date_match = re.search(r"(tomorrow|yesterday|today|\d{1,2}/\d{1,2}/\d{4})", lower_text)
        if date_match:
            ent.date = date_match.group(0)

        # 4. Extract Location/City Entities dynamically
        # Look for preposition indicators like "in Ahmedabad", "at Rajkot"
        loc_match = re.search(r"\b(?:in|at|near|for|of)\s+([a-zA-Z]+(?:[\s-][a-zA-Z]+)*)\b", lower_text)
        if loc_match:
            # Filter out standard non-city keywords
            extracted_candidate = loc_match.group(1).strip().title()
            if extracted_candidate.lower() not in ["degrees", "celsius", "fahrenheit", "compost", "manure"]:
                ent.location = extracted_candidate

        # Common known cities fallback list
        known_cities = ["ahmedabad", "surat", "rajkot", "bangalore", "mumbai", "delhi", "ludhiana", "amritsar", "gandhinagar", "anand"]
        for city in known_cities:
            if city in lower_text:
                ent.location = city.capitalize()
                break

        return ent
