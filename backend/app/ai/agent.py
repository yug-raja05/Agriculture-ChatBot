import logging
import asyncio
from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.ai.registry import ai_tool_registry
from app.ai.agent_executor import agent_brain
from app.ai.nlp.pipeline import nlp_pipeline
from app.models.chat import ToolCallLog, MessageAttachment

logger = logging.getLogger(__name__)

class AgriGeniusAgentCoordinator:
    """
    Coordinator bridging FastAPI, the NLP Pipeline, and the LangChain Agent Executor.
    Ensures raw user text is normalized, intents classified, and entities extracted
    before planner/execution steps occur.
    """
    def __init__(self):
        self.registry = ai_tool_registry
        self.agent = agent_brain
        self.nlp = nlp_pipeline

    async def process_chat_query(
        self, 
        user_id: str, 
        chat_id: str, 
        query: str, 
        attachments: List[MessageAttachment],
        db: AsyncIOMotorDatabase,
        queue: Optional[asyncio.Queue] = None
    ) -> Dict[str, Any]:
        """
        Processes query, parses through NLP Pipeline, queries context profile history,
        and invokes the LangChain planner.
        """
        logger.info(f"Agent Coordinator running NLP parser for message in {chat_id}...")

        # 1. Fetch Farmer Profile context memory
        profile = await db["profiles"].find_one({"user_id": user_id})
        farmer_crops = profile.get("primary_crops", []) if profile else []
        farmer_location = profile.get("location", "Unknown Location") if profile else "Unknown Location"
        soil_profile = profile.get("soil_profile", {}) if profile else {}

        # 1b. Check attachments for client location and coordinates
        attached_loc = None
        attached_lat = None
        attached_lon = None
        for att in (attachments or []):
            if isinstance(att, dict) and att.get("file_type") == "location_coords":
                loc_cand = att.get("location")
                if loc_cand and loc_cand not in ["Detecting location...", "Unknown Location", ""]:
                    attached_loc = loc_cand
                if att.get("lat") and att.get("lon"):
                    try:
                        attached_lat = float(att.get("lat"))
                        attached_lon = float(att.get("lon"))
                    except (ValueError, TypeError):
                        pass
                if attached_loc:
                    break
            elif hasattr(att, "file_type") and getattr(att, "file_type", "") == "location_coords":
                loc_cand = getattr(att, "location", None)
                if loc_cand and loc_cand not in ["Detecting location...", "Unknown Location", ""]:
                    attached_loc = loc_cand
                if getattr(att, "lat", None) and getattr(att, "lon", None):
                    try:
                        attached_lat = float(att.lat)
                        attached_lon = float(att.lon)
                    except (ValueError, TypeError):
                        pass
                if attached_loc:
                    break

        if attached_loc and (not farmer_location or farmer_location in ["Unknown Location", "Detecting location..."]):
            farmer_location = attached_loc
            await db["profiles"].update_one(
                {"user_id": user_id},
                {"$set": {"location": attached_loc, "latitude": attached_lat, "longitude": attached_lon}},
                upsert=True
            )
            if profile:
                profile["location"] = attached_loc
                profile["latitude"] = attached_lat
                profile["longitude"] = attached_lon
            else:
                profile = {"user_id": user_id, "location": attached_loc, "latitude": attached_lat, "longitude": attached_lon}

        # 2. Invoke NLP Ingestion pipeline (Raw query text analyzed here)
        nlp_res = await self.nlp.process_query(
            text=query,
            user_id=user_id,
            profile=profile or {},
            db=db
        )

        primary_intent = nlp_res.intents[0]["intent"] if nlp_res.intents else "General Question"
        entities = nlp_res.entities

        # 3. Context updates: Farmer crops learning memory
        if entities and entities.crop:
            await db["profiles"].update_one(
                {"user_id": user_id},
                {"$addToSet": {"primary_crops": entities.crop}}
            )

        # 5. Invoke LangChain Agent loop using query and attachments
        agent_res = await self.agent.execute_agent_loop(
            query=query,
            user_id=user_id,
            attachments=attachments or [],
            chat_history=[],
            profile=profile or {},
            queue=queue
        )

        # 6. Resolve execution log wrappers for matching registry tools
        tool_logs: List[ToolCallLog] = []

        # First check if agent_executor already emitted live verified tool calls
        if agent_res.get("tool_calls"):
            for tc in agent_res["tool_calls"]:
                try:
                    if isinstance(tc, ToolCallLog):
                        tool_logs.append(tc)
                    elif isinstance(tc, dict):
                        tool_logs.append(ToolCallLog(**tc))
                except Exception as log_err:
                    logger.warning(f"Failed to parse agent tool call: {log_err}")

        # Fallback to coordinator tool execution if agent loop did not produce any tool calls
        if not tool_logs:
            tool_name = nlp_res.suggested_tool
            tool_params = {}
            
            if tool_name == "weather_advisor":
                req_loc = entities.location if (entities and entities.location) else None
                user_farm_loc = farmer_location if (farmer_location and farmer_location not in ["Unknown Location", "Detecting location...", "Local Area"]) else None
                effective_loc = req_loc or attached_loc or user_farm_loc or "Surat, Gujarat"
                tool_params = {
                    "location": effective_loc,
                    "latitude": attached_lat,
                    "longitude": attached_lon,
                    "days_forecast": 3
                }
            elif tool_name == "plant_disease_detector":
                tool_params = {"image_url": "uploaded_scan.jpg"}
            elif tool_name == "crop_recommender":
                tool_params = {
                    "nitrogen": soil_profile.get("nitrogen", 50.0),
                    "phosphorus": soil_profile.get("phosphorus", 35.0),
                    "potassium": soil_profile.get("potassium", 110.0),
                    "ph": soil_profile.get("ph", 6.5),
                    "moisture": soil_profile.get("moisture", 35.0)
                }
            elif tool_name == "market_price_assistant":
                tool_params = {"crop_name": entities.crop or "Wheat"}

            if tool_name and tool_name != "general_chat":
                res = await self.registry.execute_tool(tool_name, tool_params, user_id)
                log_entry = ToolCallLog(
                    tool_name=tool_name,
                    parameters=tool_params,
                    output=res
                )
                tool_logs.append(log_entry)

        return {
            "content": agent_res["content"],
            "tool_logs": tool_logs
        }

agent_coordinator = AgriGeniusAgentCoordinator()
