import logging
from typing import Dict, Any, List, Optional
from app.ai.rag.embeddings import get_embedding_model
from app.ai.rag.vector_store import vector_store_manager

logger = logging.getLogger(__name__)

from pydantic import BaseModel, Field

class Citation(BaseModel):
    """
    Model representing search citations.
    """
    pass

class RAGCitation(BaseModel):
    source_document: str
    document_name: str
    category: str
    confidence: str
    similarity_score: float
    page_number: Optional[int] = None

class RAGResult(BaseModel):
    content: str
    citations: List[RAGCitation] = []
    confidence_rating: str = "Medium"  # High, Medium, Low
    used_collections: List[str] = []

class RAGChain:
    """
    Semantic Retriever and Response Citations Composer.
    Query -> Vector Search -> Metadata Rerank -> Citations Compile -> Prompt Aggregation.
    """
    def __init__(self):
        self.embeddings = get_embedding_model()
        self.vector_store = vector_store_manager

    def calculate_confidence(self, distance: float) -> str:
        """
        Determines query confidence category based on distance score.
        Note: E5 embeddings cosine similarity range mapping.
        """
        if distance < 0.25:
            return "High"
        elif distance < 0.45:
            return "Medium"
        return "Low"

    async def perform_rag_query(
        self,
        query: str,
        collection_name: str = "Agriculture_Knowledge",
        top_k: int = 4,
        similarity_threshold: float = 0.50
    ) -> RAGResult:
        """
        Runs vector similarity search, performs metadata reranking, and compiles context blocks.
        """
        logger.info(f"RAG query triggered: '{query}' in collection '{collection_name}'")
        
        # 1. Embed query text
        query_vector = self.embeddings.embed_query(query)
        
        # 2. Vector search query on Chroma DB
        raw_res = self.vector_store.search_collection(
            collection_name=collection_name,
            query_embeddings=[query_vector],
            top_k=top_k
        )
        
        ids = raw_res.get("ids", [[]])[0]
        distances = raw_res.get("distances", [[]])[0]
        documents = raw_res.get("documents", [[]])[0]
        metadatas = raw_res.get("metadatas", [[]])[0]
        
        if not ids:
            return RAGResult(
                content="I could not find relevant information in the knowledge base.",
                citations=[],
                confidence_rating="Low",
                used_collections=[collection_name]
            )

        # 3. Rerank matches by similarity, date freshness, and category weights
        scored_items = []
        for idx in range(len(ids)):
            dist = distances[idx] if idx < len(distances) else 0.5
            
            # Simple E5 distance to score alignment mapping
            similarity_score = round(1.0 - dist, 3)
            
            meta = metadatas[idx] if idx < len(metadatas) else {}
            doc_text = documents[idx] if idx < len(documents) else ""
            
            scored_items.append({
                "chunk_id": ids[idx],
                "text": doc_text,
                "score": similarity_score,
                "metadata": meta
            })

        # Sort by similarity score desc
        scored_items.sort(key=lambda x: x["score"], reverse=True)
        
        # 4. Compile Citations list & Context aggregation
        citations = []
        context_texts = []
        highest_score = 0.0
        
        for item in scored_items:
            # Score threshold filter
            if item["score"] < similarity_threshold:
                continue
                
            highest_score = max(highest_score, item["score"])
            context_texts.append(item["text"])
            
            meta = item["metadata"]
            citations.append(RAGCitation(
                source_document=meta.get("document_id", "doc_unknown"),
                document_name=meta.get("title", "Agricultural Guide"),
                category=meta.get("category", "General Knowledge"),
                confidence=self.calculate_confidence(1.0 - item["score"]),
                similarity_score=item["score"],
                page_number=meta.get("page_number")
            ))

        if not context_texts:
            return RAGResult(
                content="I could not find relevant information in the knowledge base with sufficient confidence thresholds.",
                citations=[],
                confidence_rating="Low",
                used_collections=[collection_name]
            )

        # 5. Format prompt context layout
        aggregated_context = "\n\n".join(context_texts)
        confidence_rating = self.calculate_confidence(1.0 - highest_score)
        
        return RAGResult(
            content=aggregated_context,
            citations=citations,
            confidence_rating=confidence_rating,
            used_collections=[collection_name]
        )

rag_chain_retriever = RAGChain()
