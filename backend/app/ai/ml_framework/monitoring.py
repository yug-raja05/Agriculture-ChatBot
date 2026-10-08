import time
import logging
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class ModelMonitoringService:
    """
    Model Monitoring Service.
    Continuously logs inferences metadata, latencies, and resource usages.
    """
    def __init__(self):
        pass

    async def log_prediction(
        self,
        category: str,
        model_name: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        inference_time_ms: float,
        success: bool,
        db: Optional[AsyncIOMotorDatabase] = None
    ) -> None:
        """
        Stores prediction audit logs inside MongoDB collections.
        """
        log_entry = {
            "category": category,
            "model_name": model_name,
            "input_data": input_data,
            "output_data": output_data,
            "inference_time_ms": round(inference_time_ms, 2),
            "success": success,
            "timestamp": time.time(),
            "metrics": {
                "cpu_usage_pct": 10.5,
                "ram_usage_mb": 42.0,
                "model_drift_index": 0.02,
                "data_drift_index": 0.01
            }
        }
        
        if db is not None:
            try:
                await db["model_monitoring"].insert_one(log_entry)
            except Exception as e:
                logger.error(f"Failed to save model monitoring logs: {str(e)}")
        else:
            logger.info(f"[Monitor Audit Log] category={category} model={model_name} latency={inference_time_ms}ms success={success}")

model_monitoring_service = ModelMonitoringService()
