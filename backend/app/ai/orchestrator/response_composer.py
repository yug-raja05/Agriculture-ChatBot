from datetime import datetime, timezone
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

class SummaryRecord(BaseModel):
    user_id: str
    chat_id: str
    summary_text: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ResponseComposer:
    """
    Response Composer & Summarizer Service.
    Assembles final markdown texts and logs chat summaries in MongoDB.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    def compose_final_response(
        self,
        query: str,
        tool_results: List[Dict[str, Any]],
        duration_seconds: float
    ) -> Dict[str, Any]:
        """
        Gathers raw tool outputs and constructs a polished, structured markdown result.
        """
        markdown_body = f"### Agricultural Advisor Report\n\n"
        recommendations = []
        warnings = []
        actions = []
        used_tools = []

        for log in tool_results:
            name = log.get("tool_name")
            output = log.get("output", {}).get("result", {})
            used_tools.append(name)
            
            if name == "weather_advisor":
                markdown_body += (
                    f"#### Weather Conditions\n"
                    f"- Current temperature: {output.get('temperature_celsius')}°C with {output.get('humidity_percentage')}% humidity.\n"
                    f"- Rainfall Probability: {output.get('rainfall_probability') * 100}%.\n\n"
                )
                if output.get("warning"):
                    warnings.append(output.get("warning"))
            elif name == "plant_disease_detector":
                markdown_body += (
                    f"#### Diagnostic Scan Result\n"
                    f"- **Diagnosis**: {output.get('diagnosis')} (Confidence: {int(output.get('confidence', 0.95) * 100)}%)\n\n"
                )
                for treat in output.get("treatment", []):
                    recommendations.append(treat)
                actions.append("Analyze leaf image")
            elif name == "market_price_assistant":
                markdown_body += (
                    f"#### Market Quotes\n"
                    f"- Average wholesale price: ${output.get('average_price')} per quintal (Trend: {output.get('trend')})\n\n"
                )
                actions.append("Check Market Prices")

        # Warnings box
        if warnings:
            markdown_body += "#### ⚠️ Advisory Alerts\n"
            for warn in warnings:
                markdown_body += f"> [!WARNING]\n> {warn}\n\n"

        # Recommendations box
        if recommendations:
            markdown_body += "#### 🌱 Recommended Actions\n"
            for rec in recommendations:
                markdown_body += f"- {rec}\n"
            markdown_body += "\n"

        # Next Steps
        markdown_body += "#### Next Steps\n- Regularly monitor soil moisture.\n- Schedule alerts for chemical spraying in the dashboard."

        return {
            "content": markdown_body,
            "metadata": {
                "confidence_score": 0.92,
                "used_tools": used_tools,
                "execution_time_seconds": round(duration_seconds, 3),
                "suggested_actions": actions,
                "suggested_questions": ["Recommend fertilizer dosage?", "Check weather forecast?"]
            }
        }

    async def generate_and_save_summary(self, user_id: str, chat_id: str, chat_history: List[Dict[str, Any]]) -> str:
        """
        Creates a short summarization transcript and saves it in MongoDB.
        """
        text_concat = " ".join([m.get("content", "") for m in chat_history])
        # Simple compression logic
        words = text_concat.split(" ")
        summary_words = words[:30]
        summary_text = " ".join(summary_words) + "..." if len(words) > 30 else text_concat
        
        record = SummaryRecord(
            user_id=user_id,
            chat_id=chat_id,
            summary_text=summary_text
        )
        await self.db["conversation_summary"].replace_one(
            {"chat_id": chat_id},
            record.model_dump(),
            upsert=True
        )
        return summary_text
