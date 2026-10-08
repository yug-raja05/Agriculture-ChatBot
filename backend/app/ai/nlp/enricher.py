from typing import Dict, Any
from app.ai.nlp.entities import NLPContextEntities

class ContextEnricher:
    """
    Context Enrichment Service.
    Merges NLP parsed entities with conversation context memory.
    """
    def __init__(self):
        pass

    def enrich_context(
        self,
        entities: NLPContextEntities,
        profile: Dict[str, Any]
    ) -> NLPContextEntities:
        """
        Populates missing query parameters using historical profile details.
        """
        # Create a copy of entities to modify
        enriched = entities.model_copy()

        # If query crop is empty, enrich from profile primary crops
        if not enriched.crop and profile and profile.get("primary_crops"):
            primary = profile.get("primary_crops")
            enriched.crop = primary[0] if isinstance(primary, list) else primary

        # Enrich location
        if not enriched.location and profile and profile.get("location"):
            enriched.location = profile.get("location")

        # Enrich farm size
        if not enriched.farm_size and profile and profile.get("farm_size_hectares"):
            enriched.farm_size = f"{profile.get('farm_size_hectares')} hectares"

        # Enrich soil parameters
        if not enriched.soil_type and profile and profile.get("soil_profile", {}).get("texture"):
            enriched.soil_type = profile.get("soil_profile").get("texture")

        return enriched
