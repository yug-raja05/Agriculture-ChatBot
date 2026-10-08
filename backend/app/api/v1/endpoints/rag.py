import os
import uuid
import shutil
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field
from app.api.deps import get_db, get_current_user
from app.models.user import UserDB
from app.ai.rag.embeddings import get_embedding_model
from app.ai.rag.vector_store import vector_store_manager
from app.ai.rag.document_loader import DocumentLoader
from app.ai.rag.rag_chain import rag_chain_retriever

router = APIRouter()

# Staging uploads directory
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class EmbeddingJobRecord(BaseModel):
    job_id: str
    user_id: str
    file_name: str
    status: str = "pending"  # pending, processing, completed, failed
    progress: float = 0.0
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DocumentMetadataSchema(BaseModel):
    document_id: str
    title: str
    category: str
    language: str
    author: str
    tags: List[str] = []
    file_type: str
    chunk_count: int
    version: int = 1
    upload_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Background processing task
async def process_document_background(
    job_id: str,
    file_path: str,
    file_type: str,
    doc_id: str,
    meta_dict: Dict[str, Any],
    db_name: str,
    db: AsyncIOMotorDatabase
):
    """
    Asynchronous RAG document extraction, split parsing, and embedding vectorization.
    """
    try:
        # Update status to processing
        await db["embedding_jobs"].update_one(
            {"job_id": job_id},
            {"$set": {"status": "processing", "progress": 0.25}}
        )

        loader = DocumentLoader(chunk_size=300, overlap=30)
        chunks = loader.process_document(file_path, file_type, doc_id, meta_dict)
        
        await db["embedding_jobs"].update_one(
            {"job_id": job_id},
            {"$set": {"progress": 0.50}}
        )

        # Generate vectors
        embeddings_model = get_embedding_model()
        chunk_texts = [c.text for c in chunks]
        embeddings = embeddings_model.embed_documents(chunk_texts)
        
        await db["embedding_jobs"].update_one(
            {"job_id": job_id},
            {"$set": {"progress": 0.75}}
        )

        # Save to Chroma Vector DB
        col_name = "crop_guides" if meta_dict.get("category") == "Crop Guide" else "Agriculture_Knowledge"
        ids = [c.chunk_id for c in chunks]
        metadatas = [c.metadata for c in chunks]
        
        vector_store_manager.add_vectors(
            collection_name=col_name,
            ids=ids,
            embeddings=embeddings,
            documents=chunk_texts,
            metadatas=metadatas
        )

        # Save metadata to MongoDB
        await db["documents"].insert_one({
            "_id": doc_id,
            "title": meta_dict.get("title"),
            "file_type": file_type,
            "path": file_path,
            "uploaded_by": meta_dict.get("author"),
            "created_at": datetime.now(timezone.utc)
        })
        
        doc_metadata = DocumentMetadataSchema(
            document_id=doc_id,
            title=meta_dict.get("title"),
            category=meta_dict.get("category", "General Knowledge"),
            language=meta_dict.get("language", "en"),
            author=meta_dict.get("author", "System"),
            tags=meta_dict.get("tags", []),
            file_type=file_type,
            chunk_count=len(chunks)
        )
        await db["document_metadata"].insert_one(doc_metadata.model_dump())

        # Complete job
        await db["embedding_jobs"].update_one(
            {"job_id": job_id},
            {"$set": {"status": "completed", "progress": 1.0}}
        )
    except Exception as e:
        # Log failure
        await db["embedding_jobs"].update_one(
            {"job_id": job_id},
            {"$set": {"status": "failed", "error_message": str(e)}}
        )
        await db["knowledge_base_logs"].insert_one({
            "event": "ingestion_failure",
            "document_id": doc_id,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc)
        })

# 1. Document Upload API
@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    bg_tasks: BackgroundTasks,
    title: str,
    category: str = "General Knowledge",
    language: str = "en",
    author: str = "Admin",
    tags: str = "",
    file: UploadFile = File(...),
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Registers a RAG ingestion job, saves files to staging, and schedules vectorization in BackgroundTasks.
    """
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else "txt"
    if file_ext not in ["pdf", "docx", "txt", "md", "markdown", "csv", "json"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: {file_ext}"
        )

    # Prevent large files over 20MB
    # Note: File size check wrapper
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > 20 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 20MB configuration limits."
        )

    doc_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())
    
    # Save file to staging uploads dir
    staged_path = os.path.join(UPLOAD_DIR, f"{doc_id}.{file_ext}")
    with open(staged_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    meta_dict = {
        "title": title,
        "category": category,
        "language": language,
        "author": author,
        "tags": tag_list
    }

    # Insert pending job
    job = EmbeddingJobRecord(
        job_id=job_id,
        user_id=current_user.id,
        file_name=file.filename
    )
    await db["embedding_jobs"].insert_one(job.model_dump())

    # Dispatch Background Task
    bg_tasks.add_task(
        process_document_background,
        job_id,
        staged_path,
        file_ext,
        doc_id,
        meta_dict,
        db.name,
        db
    )

    return {"status": "queued", "job_id": job_id, "document_id": doc_id}

# 2. Document deletion API
@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    doc = await db["documents"].find_one({"_id": doc_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Remove from vector stores
    meta = await db["document_metadata"].find_one({"document_id": doc_id})
    if meta:
        col_name = "crop_guides" if meta.get("category") == "Crop Guide" else "Agriculture_Knowledge"
        chunk_count = meta.get("chunk_count", 0)
        chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(chunk_count)]
        vector_store_manager.delete_vectors(col_name, chunk_ids)

    # Clean file system staging
    if os.path.exists(doc.get("path", "")):
        try:
            os.remove(doc.get("path"))
        except Exception:
            pass

    # Clear MongoDB registries
    await db["documents"].delete_one({"_id": doc_id})
    await db["document_metadata"].delete_one({"document_id": doc_id})

    return {"deleted": True, "document_id": doc_id}

# 3. Search document metadata
@router.get("/search")
async def search_documents_metadata(
    query: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    cursor = db["document_metadata"].find({"title": {"$regex": query, "$options": "i"}}).limit(20)
    results = []
    async for doc in cursor:
        results.append(DocumentMetadataSchema(**doc))
    return results

# 4. Vector Similarity query API
@router.post("/vector-search")
async def perform_vector_similarity_search(
    query: str,
    collection: str = "Agriculture_Knowledge",
    top_k: int = 4,
    similarity_threshold: float = 0.50
):
    res = await rag_chain_retriever.perform_rag_query(
        query=query,
        collection_name=collection,
        top_k=top_k,
        similarity_threshold=similarity_threshold
    )
    return res

# 5. Statistics dashboard values
@router.get("/statistics")
async def knowledge_base_statistics(
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    doc_count = await db["documents"].count_documents({})
    metadata_cursor = db["document_metadata"].find({})
    
    total_chunks = 0
    categories = {}
    async for doc in metadata_cursor:
        total_chunks += doc.get("chunk_count", 0)
        cat = doc.get("category", "General Knowledge")
        categories[cat] = categories.get(cat, 0) + 1

    jobs_count = await db["embedding_jobs"].count_documents({"status": "failed"})

    return {
        "total_documents": doc_count,
        "total_chunks_vectorized": total_chunks,
        "categories_distribution": categories,
        "failed_ingestion_jobs": jobs_count
    }

# 6. Collection health status
@router.get("/collections")
async def collections_status():
    hc = vector_store_manager.check_health()
    cols = vector_store_manager.list_collections()
    
    col_details = []
    for c in cols:
        stats = vector_store_manager.get_collection_stats(c)
        col_details.append(stats)

    return {"health": hc, "collections": col_details}
