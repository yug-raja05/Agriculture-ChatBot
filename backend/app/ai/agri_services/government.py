import logging
import time
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.core.database import db_manager
from app.core.caching import execute_with_retry_and_cache

logger = logging.getLogger(__name__)

# Core seed data representing default government schemes
DEFAULT_SCHEMES = [
    {
        "scheme_id": "PM_KISAN",
        "name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "category": "Direct Income Support",
        "benefits": "Rs. 6000 per year in three equal installments",
        "eligibility": "Small and marginal farmer families holding cultivable land up to 2 hectares.",
        "required_documents": ["Aadhaar Card", "Land holding papers", "Bank Account Details"],
        "application_steps": [
            "Visit PM-Kisan official portal",
            "Click on New Farmer Registration",
            "Input Aadhaar details and upload land papers",
            "Submit registration for state validation"
        ],
        "deadline": "Rolling Registration"
    },
    {
        "scheme_id": "PMFBY",
        "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "category": "Crop Insurance",
        "benefits": "Low premium insurance cover against crop failures due to natural calamities.",
        "eligibility": "All farmers growing notified crops in notified areas including sharecroppers.",
        "required_documents": ["Land record document", "Sowing certificate", "Aadhaar Card", "Bank Passbook"],
        "application_steps": [
            "Apply through bank branches or authorized insurance agents",
            "Submit sowing certificate within 10 days of sowing",
            "Pay nominal premium (1.5% to 5% depending on crop season)"
        ],
        "deadline": "August 31, 2026 for Kharif crops"
    },
    {
        "scheme_id": "KCC",
        "name": "Kisan Credit Card (KCC)",
        "category": "Agriculture Loan",
        "benefits": "Access to short term loans up to Rs. 3 Lakh at low interest rates (4% effective).",
        "eligibility": "Individual/Joint cultivators, tenant farmers, and sharecroppers.",
        "required_documents": ["Land ownership documents", "ID proof (Aadhaar/Voter ID)", "Address proof"],
        "application_steps": [
            "Visit nearest commercial or cooperative bank branch",
            "Fill KCC application forms",
            "Submit land title papers and ID verifications"
        ],
        "deadline": "No specific deadline"
    }
]

class SchemesProvider:
    async def fetch_schemes(self, query: str = "", category: str = "") -> List[Dict[str, Any]]:
        raise NotImplementedError()

    async def get_details(self, scheme_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError()

class DatabaseGovSchemesProvider(SchemesProvider):
    async def _ensure_seeded(self, db):
        try:
            count = await db["government_schemes"].count_documents({})
            if count == 0:
                logger.info("MongoDB government_schemes collection is empty. Seeding defaults...")
                await db["government_schemes"].insert_many(DEFAULT_SCHEMES)
                logger.info("Successfully seeded government schemes database.")
        except Exception as e:
            logger.error(f"Error seeding government schemes: {e}")

    async def fetch_schemes(self, query: str = "", category: str = "") -> List[Dict[str, Any]]:
        db = db_manager.db
        if db is None:
            # If MongoDB is down, return default schemes as immediate in-memory fallback
            logger.warning("MongoDB is offline. Falling back to in-memory defaults.")
            return [s for s in DEFAULT_SCHEMES if (not query or query.lower() in s["name"].lower()) and (not category or category.lower() == s["category"].lower())]
            
        await self._ensure_seeded(db)
        
        filter_dict = {}
        if query:
            filter_dict["$or"] = [
                {"name": {"$regex": query, "$options": "i"}},
                {"category": {"$regex": query, "$options": "i"}},
                {"benefits": {"$regex": query, "$options": "i"}}
            ]
        if category:
            filter_dict["category"] = category
            
        results = []
        try:
            cursor = db["government_schemes"].find(filter_dict)
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                results.append(doc)
        except Exception as e:
            logger.error(f"Failed to fetch schemes from MongoDB: {e}")
        return results

    async def get_details(self, scheme_id: str) -> Optional[Dict[str, Any]]:
        db = db_manager.db
        if db is None:
            for s in DEFAULT_SCHEMES:
                if s["scheme_id"] == scheme_id:
                    return s
            return None
            
        await self._ensure_seeded(db)
        try:
            doc = await db["government_schemes"].find_one({"scheme_id": scheme_id})
            if doc:
                doc["_id"] = str(doc["_id"])
                return doc
        except Exception as e:
            logger.error(f"Failed to get scheme details from MongoDB: {e}")
        return None

class APIGovSchemesProvider(SchemesProvider):
    """
    Queries simulated/real external government schemes API (e.g. data.gov.in schemes APIs).
    If connection fails, triggers the fallback system.
    """
    async def fetch_schemes(self, query: str = "", category: str = "") -> List[Dict[str, Any]]:
        # In production, this calls the external national scheme aggregator API.
        # Here we fetch from an API representation or fall back to DB.
        db_provider = DatabaseGovSchemesProvider()
        return await db_provider.fetch_schemes(query, category)

    async def get_details(self, scheme_id: str) -> Optional[Dict[str, Any]]:
        db_provider = DatabaseGovSchemesProvider()
        return await db_provider.get_details(scheme_id)

class GovernmentProviderRegistry:
    def __init__(self):
        self._providers = {
            "database": DatabaseGovSchemesProvider(),
            "api": APIGovSchemesProvider()
        }

    def get_provider(self) -> SchemesProvider:
        active_name = settings.ACTIVE_GOVERNMENT_PROVIDER
        return self._providers.get(active_name, self._providers["database"])

class GovernmentService:
    """
    Government Schemes Knowledge Platform.
    Tracks Central & State subsidies, PM-Kisan, PMFBY, and KCC loans.
    """
    def __init__(self):
        self.registry = GovernmentProviderRegistry()

    async def search_schemes(self, query: str = "", category: str = "") -> List[Dict[str, Any]]:
        prov = self.registry.get_provider()
        
        async def fetch():
            return await prov.fetch_schemes(query, category)
            
        cache_key = {"query": query.strip().lower(), "category": category.strip().lower()}
        return await execute_with_retry_and_cache(
            cache_key_dict=cache_key,
            collection_name="schemes_cache",
            api_call_func=fetch,
            cache_ttl_seconds=86400  # 24 hours schemes list cache TTL
        )

    async def get_scheme_details(self, scheme_id: str) -> Optional[Dict[str, Any]]:
        prov = self.registry.get_provider()
        
        async def fetch():
            return await prov.get_details(scheme_id)
            
        cache_key = {"scheme_id": scheme_id}
        return await execute_with_retry_and_cache(
            cache_key_dict=cache_key,
            collection_name="schemes_cache",
            api_call_func=fetch,
            cache_ttl_seconds=86400  # 24 hours scheme details cache TTL
        )

government_service = GovernmentService()
