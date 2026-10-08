from typing import Dict, Any, List
from app.ai.orchestrator.session_manager import SessionContext
from app.ai.orchestrator.memory_manager import ConversationMemory

class ContextBuilder:
    """
    Context Builder Service.
    Assembles profile values, session properties, and chat summaries to feed the LLM.
    """
    def __init__(self):
        pass

    def build_optimized_context(
        self,
        current_query: str,
        history: List[Dict[str, Any]],
        session: SessionContext,
        memory: ConversationMemory,
        chat_summary: str = ""
    ) -> Dict[str, Any]:
        """
        Gathers session active parameters and merges them into a clean prompt context map.
        """
        # Compress history if it exceeds limits
        limited_history = history[-10:] if len(history) > 10 else history

        soil = memory.soil_profile
        npk_summary = (
            f"N: {soil.get('nitrogen', 'N/A')}, "
            f"P: {soil.get('phosphorus', 'N/A')}, "
            f"K: {soil.get('potassium', 'N/A')}, "
            f"pH: {soil.get('ph', 'N/A')}"
        )

        return {
            "current_query": current_query,
            "language": session.current_language,
            "location": session.current_location,
            "season": session.current_season,
            "soil_NPK": npk_summary,
            "crops_history": ", ".join(memory.crop_history) if memory.crop_history else "None recorded",
            "recent_diseases": ", ".join(memory.previous_diseases) if memory.previous_diseases else "None recorded",
            "chat_summary": chat_summary or "No summary available",
            "history_messages_count": len(limited_history),
            "active_tool": session.current_active_tool or "None"
        }
