from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, chat, agent, rag, nlp, models, plant_health, agri_services, enterprise

api_router = APIRouter()

# Register sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users & Profiles"])
api_router.include_router(chat.router, prefix="/chats", tags=["Chat & AI Assistant"])
api_router.include_router(agent.router, prefix="/agent", tags=["AI Agent Orchestration"])
api_router.include_router(rag.router, prefix="/rag", tags=["AI RAG Knowledge Base"])
api_router.include_router(nlp.router, prefix="/nlp", tags=["AI NLP Engine"])
api_router.include_router(models.router, prefix="/models", tags=["AI Models Management"])
api_router.include_router(plant_health.router, prefix="", tags=["Intelligent Plant Health Platform"])
api_router.include_router(agri_services.router, prefix="", tags=["Smart Agriculture Services Platform"])
api_router.include_router(enterprise.router, prefix="/enterprise", tags=["Enterprise Platform Services"])
