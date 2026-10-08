import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=========================================")
print("AgriGenius AI RAG - Ingestion & Retrieval Verification Check")
print("=========================================")

async def test_rag_pipeline():
    try:
        # Load and connect DB Manager
        from app.core.database import db_manager
        db_manager.connect()
        db = db_manager.db
        
        print("1. Loading Embedding Model Service...")
        from app.ai.rag.embeddings import get_embedding_model
        embed = get_embedding_model()
        vec = embed.embed_query("Organic wheat composting")
        print(f"   [OK] Embedded query dimensions: {len(vec)}")

        print("2. Loading Vector Store Manager...")
        from app.ai.rag.vector_store import vector_store_manager
        hc = vector_store_manager.check_health()
        print(f"   [OK] Chroma DB Health Check status: {hc.get('status')}")

        print("3. Loading Document Loader & Splitter...")
        from app.ai.rag.document_loader import DocumentLoader
        loader = DocumentLoader(chunk_size=50, overlap=5)
        # Create a mock text file
        temp_path = "temp_doc.txt"
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write("Wheat requires moderate watering and rich nitrogen compost soil configurations to achieve bumper crop yield sizes.")
            
        chunks = loader.process_document(
            file_path=temp_path,
            file_type="txt",
            doc_id="test_doc_1",
            base_metadata={"category": "Crop Guide", "title": "Wheat Care Guide"}
        )
        print(f"   [OK] Total split document chunks count: {len(chunks)}")
        print(f"   [OK] Chunk metadata preview: {chunks[0].metadata}")
        
        # Clean temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        print("4. Testing Semantic Retriever (RAG Chain query)...")
        from app.ai.rag.rag_chain import rag_chain_retriever
        res = await rag_chain_retriever.perform_rag_query(
            query="compost requirements for wheat",
            collection_name="Agriculture_Knowledge",
            top_k=2
        )
        print(f"   [OK] RAG query result rating: {res.confidence_rating}")
        
        print("\n[SUCCESS] AI RAG pipeline passes test compiles perfectly!")
        print("=========================================")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] RAG verification failed: {str(e)}")
        print("=========================================")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_rag_pipeline())
