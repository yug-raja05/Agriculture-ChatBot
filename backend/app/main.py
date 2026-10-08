import os
import warnings
import logging
from contextlib import asynccontextmanager

# Suppress non-critical third-party warnings & HF hub notices on startup
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Configure HuggingFace authentication token globally to suppress unauthenticated Hub warnings
hf_token = os.getenv("HF_TOKEN")
if hf_token:
    os.environ["HF_TOKEN"] = hf_token
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_token

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.api.middleware.rate_limit import RateLimitMiddleware
from app.api.middleware.security import SecurityHeadersMiddleware
from app.core.config import settings
from app.core.database import db_manager
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging

# Import app.ai to trigger self-registering tool decorators on startup
import app.ai

# Setup logging
setup_logging()
logger = logging.getLogger("app.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages database client lifecycles.
    """
    logger.info("Initializing database connections lifecycle...")
    try:
        db_manager.connect()
        logger.info("Database clients registered successfully.")
    except Exception as e:
        logger.critical(f"Database setup crashed: {str(e)}")
        
    yield
    
    logger.info("Closing database connections lifecycle...")
    db_manager.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise Clean Architecture AI Agriculture platform chatbot to help farmers.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 1. CORS Middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 2. Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware)

# 3. Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# 4. Exception Registry
register_exception_handlers(app)

# 5. Route mounts
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["System Health"])
def health_check():
    """
    Liveness probe checks.
    """
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "database_connected": db_manager.mongo_client is not None,
        "vector_store_connected": db_manager.mongo_client is not None
    }

# Signal Uvicorn reload for state-specific crop recommendations update
