import time
import logging
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field
from app.ai.nlp.normalizer import TextNormalizer
from app.ai.nlp.tokenizer import MultilingualTokenizer
from app.ai.nlp.intent import IntentDetector
from app.ai.nlp.entities import EntityExtractor, NLPContextEntities
from app.ai.nlp.enricher import ContextEnricher

logger = logging.getLogger(__name__)

class NLPResult(BaseModel):
    language: str
    intents: List[Dict[str, Any]]
    entities: NLPContextEntities
    normalized_text: str
    tokens: List[str]
    confidence_score: float = 0.95
    confidence_rating: str = "High"  # High, Medium, Low
    suggested_tool: str = "general_chat"
    recommended_prompt_template: str = "general"
    processing_time_ms: float = 0.0

class NLPPipeline:
    """
    Unified NLP Pipeline.
    Clean -> Tokenize -> Detect Language -> Detect Intents -> Extract Entities -> Enrich Context.
    """
    def __init__(self):
        self.normalizer = TextNormalizer()
        self.tokenizer = MultilingualTokenizer()
        self.intent_detector = IntentDetector()
        self.entity_extractor = EntityExtractor()
        self.enricher = ContextEnricher()

    def _detect_language(self, text: str) -> str:
        # Check devanagari and gujarati scripts
        if any(ord(c) >= 2304 and ord(c) <= 2431 for c in text):
            return "hi"
        if any(ord(c) >= 2688 and ord(c) <= 2815 for c in text):
            return "gu"
        return "en"

    def _map_tool_and_template(self, primary_intent: str) -> tuple[str, str]:
        mapping = {
            "Weather Query": ("weather_advisor", "weather"),
            "Disease Detection": ("plant_disease_detector", "disease_detection"),
            "Crop Recommendation": ("crop_recommender", "crop_recommendation"),
            "Market Price": ("market_price_assistant", "market"),
            "Government Scheme": ("government_schemes_advisor", "government"),
            "Fertilizer Recommendation": ("fertilizer_advisor", "explanation"),
            "Soil Analysis": ("fertilizer_advisor", "explanation"),
            "Yield Prediction": ("yield_predictor", "yield"),
            "Knowledge Base Search": ("knowledge_base_tool", "doc_analysis")
        }
        return mapping.get(primary_intent, ("general_chat", "general"))

    async def process_query(
        self,
        text: str,
        user_id: str,
        profile: Dict[str, Any],
        db: AsyncIOMotorDatabase
    ) -> NLPResult:
        start_time = time.time()
        
        # 1. Normalize
        normalized = self.normalizer.process(text)
        
        # 2. Tokenize
        tokens = self.tokenizer.tokenize(normalized)
        
        # 3. Detect language
        lang = self._detect_language(normalized)
        
        # 4. Intent Classification
        intents = self.intent_detector.detect_intents(normalized)
        primary = intents[0]["intent"] if intents else "General Question"
        
        # 5. Extract Entities
        entities = self.entity_extractor.extract_entities(normalized)
        
        # 6. Context Enrichment
        enriched_entities = self.enricher.enrich_context(entities, profile)
        
        # 7. Map execution metadata
        tool, template = self._map_tool_and_template(primary)
        
        duration_ms = (time.time() - start_time) * 1000
        
        result = NLPResult(
            language=lang,
            intents=intents,
            entities=enriched_entities,
            normalized_text=normalized,
            tokens=tokens,
            suggested_tool=tool,
            recommended_prompt_template=template,
            processing_time_ms=round(duration_ms, 2)
        )

        # Log results to MongoDB collections nlp_logs & history tables
        try:
            await db["nlp_logs"].insert_one({
                "original_message": text,
                "normalized_message": normalized,
                "language": lang,
                "primary_intent": primary,
                "confidence": result.confidence_score,
                "processing_time_ms": result.processing_time_ms,
                "created_at": time.time()
            })
            await db["intent_history"].insert_one({
                "user_id": user_id,
                "intents": [i["intent"] for i in intents],
                "created_at": time.time()
            })
            await db["entity_history"].insert_one({
                "user_id": user_id,
                "entities": enriched_entities.model_dump(),
                "created_at": time.time()
            })
            await db["language_history"].insert_one({
                "user_id": user_id,
                "language": lang,
                "created_at": time.time()
            })
        except Exception as e:
            logger.error(f"Error logging NLP metrics: {str(e)}")

        return result

nlp_pipeline = NLPPipeline()
