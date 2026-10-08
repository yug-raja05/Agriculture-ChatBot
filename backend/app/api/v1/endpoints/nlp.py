from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.api.deps import get_db, get_current_user
from app.models.user import UserDB
from app.ai.nlp.pipeline import nlp_pipeline, NLPResult
from app.ai.nlp.normalizer import TextNormalizer
from app.ai.nlp.intent import IntentDetector
from app.ai.nlp.entities import EntityExtractor, NLPContextEntities

router = APIRouter()

from pydantic import BaseModel, Field

# Schema for text inputs
class TextQuery(BaseModel):
    text: str = Field(..., max_length=500, description="Farmer text prompt to evaluate.")

# 1. Analyze text (runs the complete pipeline)
@router.post("/analyze", response_model=NLPResult)
async def analyze_text(
    query: TextQuery,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    profile = await db["profiles"].find_one({"user_id": current_user.id})
    res = await nlp_pipeline.process_query(
        text=query.text,
        user_id=current_user.id,
        profile=profile or {},
        db=db
    )
    return res

# 2. Detect intent endpoint
@router.post("/intents")
async def detect_intent(
    query: TextQuery
):
    normalizer = TextNormalizer()
    normalized = normalizer.process(query.text)
    detector = IntentDetector()
    intents = detector.detect_intents(normalized)
    return {"original": query.text, "intents": intents}

# 3. Extract entities endpoint
@router.post("/entities", response_model=NLPContextEntities)
async def extract_entities(
    query: TextQuery
):
    normalizer = TextNormalizer()
    normalized = normalizer.process(query.text)
    extractor = EntityExtractor()
    entities = extractor.extract_entities(normalized)
    return entities

# 4. Detect language endpoint
@router.post("/languages")
async def detect_language(
    query: TextQuery
):
    # Detect language using characters script check
    text = query.text
    if any(ord(c) >= 2304 and ord(c) <= 2431 for c in text):
        lang = "hi"
    elif any(ord(c) >= 2688 and ord(c) <= 2815 for c in text):
        lang = "gu"
    else:
        lang = "en"
    return {"text": query.text, "language": lang}
