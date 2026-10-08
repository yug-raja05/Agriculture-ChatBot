import time
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.api.deps import get_db, get_current_user
from app.models.user import UserDB
from app.ai.orchestrator.session_manager import SessionManager, SessionContext
from app.ai.orchestrator.memory_manager import MemoryManager, ConversationMemory
from app.ai.orchestrator.context_builder import ContextBuilder
from app.ai.orchestrator.intent_analyzer import IntentAnalyzer
from app.ai.orchestrator.planner import Planner
from app.ai.orchestrator.tool_router import ToolRouter
from app.ai.orchestrator.response_composer import ResponseComposer

router = APIRouter()

# 1. Sessions APIs
@router.post("/sessions", response_model=SessionContext, status_code=status.HTTP_201_CREATED)
async def create_agent_session(
    location: str = "Gujarat",
    lang: str = "en",
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    manager = SessionManager(db)
    session = await manager.create_session(user_id=current_user.id, location=location, lang=lang)
    return session

@router.get("/sessions/{session_id}", response_model=SessionContext)
async def resume_agent_session(
    session_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    manager = SessionManager(db)
    session = await manager.get_session(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Active agent session not found.")
    return session

@router.delete("/sessions/{session_id}")
async def delete_agent_session(
    session_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    manager = SessionManager(db)
    session = await manager.get_session(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Active agent session not found.")
    
    success = await manager.terminate_session(session_id)
    return {"terminated": success}

# 2. Memory APIs
@router.get("/memory/{user_id}", response_model=ConversationMemory)
async def get_conversation_memory(
    user_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    manager = MemoryManager(db)
    memory = await manager.get_memory(user_id)
    return memory

@router.put("/memory/{user_id}")
async def update_conversation_memory(
    user_id: str,
    updates: Dict[str, Any],
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    manager = MemoryManager(db)
    success = await manager.update_memory(user_id, updates)
    return {"updated": success}

# 3. Context APIs
@router.get("/context/{session_id}")
async def get_active_context(
    session_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    sm = SessionManager(db)
    session = await sm.get_session(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found.")
        
    mm = MemoryManager(db)
    memory = await mm.get_memory(current_user.id)
    
    cb = ContextBuilder()
    context = cb.build_optimized_context(
        current_query="",
        history=[],
        session=session,
        memory=memory
    )
    return context

# 4. Summary APIs
@router.get("/summary/{chat_id}")
async def get_conversation_summary(
    chat_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    doc = await db["conversation_summary"].find_one({"chat_id": chat_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Summary not found.")
    return {"chat_id": chat_id, "summary_text": doc.get("summary_text")}

# 5. Tools Registry APIs
@router.post("/tools")
async def register_tool_metadata(
    tool_name: str,
    description: str,
    input_schema: Dict[str, Any],
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    router = ToolRouter(db)
    await router.register_tool_metadata(tool_name, description, input_schema)
    return {"registered": True, "tool_name": tool_name}

@router.get("/tools/status")
async def get_tools_status(
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    cursor = db["tool_registry"].find({})
    tools = []
    async for doc in cursor:
        tools.append({
            "name": doc.get("name"),
            "description": doc.get("description"),
            "health_status": doc.get("health_status", "healthy")
        })
    return tools

@router.get("/tools/metrics")
async def get_tools_metrics(
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    cursor = db["tool_logs"].find({}).sort("timestamp", -1).limit(50)
    logs = []
    async for doc in cursor:
        logs.append({
            "tool_name": doc.get("tool_name"),
            "execution_time_seconds": doc.get("execution_time_seconds"),
            "status": doc.get("status"),
            "timestamp": doc.get("timestamp")
        })
    return logs
