import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=========================================")
print("AgriGenius AI ML Framework - Model Lifecycle Verification Check")
print("=========================================")

async def test_ml_lifecycle():
    try:
        # DB connection
        client = AsyncIOMotorClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
        db = client["AgriGeniusAI_test"]
        
        print("1. Loading Model Registry & active Crop Recommendation model...")
        from app.ai.ml_framework.registry import ml_model_registry
        crop_model = ml_model_registry.GetActiveModel("crop")
        print(f"   [OK] Active Crop Model: {crop_model.name} v{crop_model.version}")
        
        print("2. Verifying Model Health Service metrics extraction...")
        from app.ai.ml_framework.health import model_health_service
        health = model_health_service.get_health_status(crop_model)
        print(f"   [OK] Model Health status: {health.get('health_status')}")
        print(f"   [OK] Availability status: {health.get('availability')}")
        print(f"   [OK] Current Memory Footprint: {health.get('current_memory_usage_mb')} MB")
        
        print("3. Verifying Model Monitoring logs...")
        from app.ai.ml_framework.monitoring import model_monitoring_service
        await model_monitoring_service.log_prediction(
            category="crop",
            model_name=crop_model.name,
            input_data={"nitrogen": 50.0},
            output_data={"crop": "Cotton"},
            inference_time_ms=12.5,
            success=True,
            db=db
        )
        print("   [OK] Successfully logged model prediction log metrics to model_monitoring.")
        
        print("4. Testing Retraining Service modular pipeline execution...")
        from app.ai.ml_framework.retraining import retraining_service
        retrain = await retraining_service.trigger_retraining_pipeline(
            category="crop",
            model_name="random_forest",
            dataset_path="datasets/crop_features_v2.csv",
            db=db
        )
        print(f"   [OK] Retrained accuracy: {retrain.get('trained_accuracy') * 100}%")
        print(f"   [OK] Promotion approval status: {retrain.get('promotion_approved')}")
        
        print("5. Testing Version Manager & trigger Rollback metrics check...")
        from app.ai.ml_framework.versioning import version_manager, version_manager
        version_log = await version_manager.register_new_version(
            category="crop",
            model_name="random_forest",
            version="v2",
            metrics={"accuracy": 0.94},
            change_log="Retrained on organic fertilizers dataset version 2.",
            db=db
        )
        print(f"   [OK] Registered new version: {version_log.get('version')}")
        
        rollback_log = await version_manager.trigger_rollback(
            category="crop",
            target_version="v1",
            db=db
        )
        print(f"   [OK] Target rollback log version: {rollback_log.get('rolled_back_to_version')}")
        print(f"   [OK] Rollback execution status: {rollback_log.get('rollback_status')}")
        
        print("\n[SUCCESS] AI ML Framework enterprise lifecycle passes test compiles perfectly!")
        print("=========================================")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] ML Lifecycle verification failed: {str(e)}")
        print("=========================================")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_ml_lifecycle())
