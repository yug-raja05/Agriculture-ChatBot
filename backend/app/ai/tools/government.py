from typing import Dict, Any
from pydantic import BaseModel, Field
from app.ai.base_tool import BaseAITool
from app.ai.registry import register_tool
from app.ai.agri_services.government import government_service

class GovSchemesParams(BaseModel):
    scheme_name: str = Field(..., description="Name of the government scheme or subsidy program.")
    state: str = Field(default="Gujarat", description="State location of the farm.")

class GovSchemesTool(BaseAITool):
    @property
    def name(self) -> str:
        return "government_schemes_advisor"

    @property
    def description(self) -> str:
        return "Fetches details, eligibility guidelines, and benefit summaries for agricultural subsidies."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return GovSchemesParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        scheme_query = params.get("scheme_name", "")
        state = params.get("state", "Gujarat")
        
        # Invoke our dynamic GovernmentService
        schemes = await government_service.search_schemes(query=scheme_query, category="")
        
        if schemes:
            s = schemes[0]
            return {
                "scheme": s.get("name"),
                "benefits": s.get("benefits"),
                "eligibility": s.get("eligibility"),
                "required_documents": s.get("required_documents", []),
                "application_steps": s.get("application_steps", []),
                "deadline": s.get("deadline"),
                "provider": s.get("provider", "Database"),
                "status": "active"
            }
        else:
            return {
                "scheme": scheme_query,
                "error": "No matching government agricultural scheme found.",
                "status": "inactive"
            }

# Automatic registration
register_tool(GovSchemesTool())
