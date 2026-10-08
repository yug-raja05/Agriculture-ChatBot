from typing import Dict, Any
from pydantic import BaseModel, Field
from app.ai.base_tool import BaseAITool
from app.ai.registry import register_tool
from app.ai.rag.rag_chain import rag_chain_retriever

class KBParams(BaseModel):
    query: str = Field(..., description="Farming search query keyword.")

class KBTool(BaseAITool):
    @property
    def name(self) -> str:
        return "knowledge_base_tool"

    @property
    def description(self) -> str:
        return "Looks up agricultural brochures, research guides, and government schemes databases."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return KBParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        query_text = params.get("query")
        
        # Invoke our RAG chain retriever
        rag_res = await rag_chain_retriever.perform_rag_query(
            query=query_text,
            collection_name="Agriculture_Knowledge",
            top_k=3,
            similarity_threshold=0.30
        )
        
        # Compile structured citations metadata for citations cards
        references_list = []
        for cit in rag_res.citations:
            references_list.append({
                "document_id": cit.source_document,
                "document_name": cit.document_name,
                "category": cit.category,
                "confidence": cit.confidence,
                "similarity_score": cit.similarity_score,
                "page_number": cit.page_number
            })

        return {
            "query": query_text,
            "context_summary": rag_res.content,
            "citations": references_list,
            "confidence_rating": rag_res.confidence_rating,
            "status": "success"
        }

register_tool(KBTool())
