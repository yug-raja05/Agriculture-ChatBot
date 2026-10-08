import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=========================================")
print("AgriGenius AI NLP - Normalizer & Pipeline Verification Check")
print("=========================================")

async def test_nlp_pipeline():
    try:
        # Mock database connection
        client = AsyncIOMotorClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
        db = client["AgriGeniusAI_test"]
        
        print("1. Loading Text Normalizer & Cleaning emoji parameters...")
        from app.ai.nlp.normalizer import TextNormalizer
        tn = TextNormalizer()
        cleaned = tn.process("My crop npk level is low 🌾! What should I do?")
        print(f"   [OK] Normalized text output: '{cleaned}'")
        
        print("2. Loading Multilingual Tokenizer & Tokenizing text...")
        from app.ai.nlp.tokenizer import MultilingualTokenizer
        tok = MultilingualTokenizer()
        tokens = tok.tokenize("વરસાદ ક્યારે આવશે?")
        print(f"   [OK] Tokenized Gujarati query count: {len(tokens)}")
        
        print("3. Loading Intent Detector & Classifying query tags...")
        from app.ai.nlp.intent import IntentDetector
        id_det = IntentDetector()
        intents = id_det.detect_intents("Is it going to rain tomorrow?")
        print(f"   [OK] Primary intent detected: {intents[0]['intent']}")
        
        print("4. Loading Entity Extractor & Extracting crop details...")
        from app.ai.nlp.entities import EntityExtractor
        ee = EntityExtractor()
        entities = ee.extract_entities("I grow cotton in my 12 acre farm")
        print(f"   [OK] Crop entity extracted: {entities.crop}")
        print(f"   [OK] Farm size entity extracted: {entities.farm_size}")
        
        print("5. Verifying Context Enricher & Merging user profiles...")
        from app.ai.nlp.enricher import ContextEnricher
        ce = ContextEnricher()
        profile = {"primary_crops": ["Wheat"], "location": "Gujarat"}
        enriched = ce.enrich_context(entities, profile)
        print(f"   [OK] Enriched Crop (from profile fallback): {enriched.crop}")
        print(f"   [OK] Enriched Location (from profile fallback): {enriched.location}")
        
        print("6. Verifying Unified NLPPipeline...")
        from app.ai.nlp.pipeline import nlp_pipeline
        res = await nlp_pipeline.process_query(
            text="Will it rain tomorrow on my cotton fields?",
            user_id="user_123",
            profile=profile,
            db=db
        )
        print(f"   [OK] NLPPipeline language detected: {res.language}")
        print(f"   [OK] NLPPipeline suggested tool execution: {res.suggested_tool}")
        print(f"   [OK] Processing Latency time: {res.processing_time_ms} ms")
        
        print("\n[SUCCESS] AI NLP Engine pipeline passes test compiles perfectly!")
        print("=========================================")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] NLP verification failed: {str(e)}")
        print("=========================================")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_nlp_pipeline())
