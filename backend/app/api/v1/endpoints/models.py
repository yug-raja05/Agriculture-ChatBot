import time
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.api.deps import get_db, get_current_user
from app.models.user import UserDB
from app.ai.ml_framework.registry import ml_model_registry
from app.ai.ml_framework.health import model_health_service
from app.ai.ml_framework.retraining import retraining_service
from app.ai.ml_framework.versioning import version_manager
from pydantic import BaseModel, Field

router = APIRouter()

# Schema definitions
class BenchmarkRequest(BaseModel):
    category: str = Field(..., description="Target model category: crop, fertilizer, yield, soil.")
    model_name: str = Field(..., description="Target model name: random_forest, xgboost, catboost, lightgbm.")

class RetrainRequest(BaseModel):
    category: str = Field(..., description="Target model category: crop, fertilizer, yield, soil.")
    model_name: str = Field(..., description="Target model name.")
    dataset_path: str = Field(..., description="Path to the training dataset.")

class RollbackRequest(BaseModel):
    category: str = Field(..., description="Target model category: crop, fertilizer, yield, soil.")
    target_version: str = Field(..., description="Target model version (e.g. v1).")

class NewVersionRequest(BaseModel):
    category: str = Field(..., description="Target model category.")
    model_name: str = Field(..., description="Target model name.")
    version: str = Field(..., description="New version identifier.")
    change_log: str = Field(..., description="What was updated in this version.")

# 1. List catalog models
@router.get("")
async def list_registered_models(
    current_user: UserDB = Depends(get_current_user)
):
    catalog = ml_model_registry.list_catalog()
    return catalog

# 2. Get active models
@router.get("/active")
async def get_active_models(
    current_user: UserDB = Depends(get_current_user)
):
    categories = ["crop", "fertilizer", "yield", "soil"]
    actives = {}
    for cat in categories:
        model = ml_model_registry.GetActiveModel(cat)
        actives[cat] = {
            "model_name": model.name if model else "None",
            "version": model.version if model else "None"
        }
    return actives

# 3. Activate a model
@router.put("/{category}/{model_name}/activate")
async def activate_model(
    category: str,
    model_name: str,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if category not in ["crop", "fertilizer", "yield", "soil"]:
        raise HTTPException(status_code=400, detail="Invalid model category.")
        
    success = ml_model_registry.SetActiveModel(category, model_name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not registered in {category}.")

    # Log configuration changes to MongoDB ml_model_configurations collection
    try:
        await db["ml_model_configurations"].insert_one({
            "category": category,
            "activated_model": model_name,
            "modified_by": current_user.id,
            "timestamp": time.time()
        })
    except Exception:
        pass

    return {"activated": True, "category": category, "model_name": model_name}

# 4. Compare models within a category
@router.get("/compare/{category}")
async def compare_category_models(
    category: str,
    current_user: UserDB = Depends(get_current_user)
):
    if category not in ["crop", "fertilizer", "yield", "soil"]:
        raise HTTPException(status_code=400, detail="Invalid model category.")
        
    comparisons = ml_model_registry.CompareModels(category)
    return comparisons

# 5. Benchmark a model
@router.post("/benchmark")
async def benchmark_model(
    req: BenchmarkRequest,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    category = req.category
    model_name = req.model_name
    
    bench_results = ml_model_registry.BenchmarkModel(category, model_name)
    if "error" in bench_results:
        raise HTTPException(status_code=404, detail=bench_results["error"])

    # Log metrics to MongoDB ml_model_metrics / benchmark_reports collections
    try:
        await db["ml_model_metrics"].insert_one({
            "category": category,
            "model_name": model_name,
            "avg_latency_seconds": bench_results.get("avg_latency_seconds"),
            "benchmark_runs": bench_results.get("benchmark_runs_count"),
            "tested_by": current_user.id,
            "timestamp": time.time()
        })
        await db["benchmark_reports"].insert_one({
            "category": category,
            "model_name": model_name,
            "metrics": bench_results,
            "timestamp": time.time()
        })
    except Exception:
        pass

    return bench_results

# 6. Model Health Endpoint
@router.get("/health/{category}/{model_name}")
async def get_model_health(
    category: str,
    model_name: str,
    current_user: UserDB = Depends(get_current_user)
):
    model = ml_model_registry.GetModel(category, model_name)
    if not model:
        raise HTTPException(status_code=404, detail="Model not registered.")
    health = model_health_service.get_health_status(model)
    return health

# 7. Model Retraining Endpoint
@router.post("/retrain")
async def retrain_model(
    req: RetrainRequest,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    retrain_res = await retraining_service.trigger_retraining_pipeline(
        category=req.category,
        model_name=req.model_name,
        dataset_path=req.dataset_path,
        db=db
    )
    return retrain_res

# 8. Model Rollback Endpoint
@router.post("/rollback")
async def rollback_model(
    req: RollbackRequest,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    rollback_res = await version_manager.trigger_rollback(
        category=req.category,
        target_version=req.target_version,
        db=db
    )
    return rollback_res

# 9. Register New Version Endpoint
@router.post("/versions")
async def register_version(
    req: NewVersionRequest,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    res = await version_manager.register_new_version(
        category=req.category,
        model_name=req.model_name,
        version=req.version,
        metrics={"accuracy": 0.90},
        change_log=req.change_log,
        db=db
    )
    return res

# 10. Monitoring Stats Endpoint
@router.get("/monitoring/stats")
async def get_monitoring_stats(
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    # Retrieve metrics from model_monitoring collection
    stats = []
    try:
        cursor = db["model_monitoring"].find().sort("timestamp", -1).limit(10)
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            stats.append(doc)
    except Exception:
        pass
    return stats
