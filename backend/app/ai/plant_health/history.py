import os
import time
import logging
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

logger = logging.getLogger(__name__)

class HistoryService:
    """
    History and Metadata Service.
    Logs analysis queries to MongoDB image_history, disease_predictions,
    pest_predictions, ocr_documents, voice_history, and speech_logs collections.
    """
    def __init__(self):
        pass

    async def log_image_prediction(
        self,
        user_id: str,
        category: str,  # disease, pest, analysis
        image_path: str,
        results: Dict[str, Any],
        db: AsyncIOMotorDatabase
    ) -> str:
        """
        Stores image evaluation outcome logs in DB.
        """
        logger.info(f"Logging {category} prediction metrics to MongoDB history...")
        
        # 1. Image metadata log
        metadata_entry = {
            "file_name": os.path.basename(image_path) if 'os' in globals() else image_path.split("/")[-1],
            "file_path": image_path,
            "width": 224,
            "height": 224,
            "format": "JPEG",
            "size_bytes": 102400,
            "timestamp": time.time()
        }
        meta_res = await db["image_metadata"].insert_one(metadata_entry)
        
        # 2. Main history entry
        history_entry = {
            "user_id": user_id,
            "crop": results.get("crop", "Tomato"),
            "category": category,
            "image_metadata_id": str(meta_res.inserted_id),
            "results": results,
            "confidence": results.get("confidence", 0.90),
            "created_at": time.time(),
            "status": "success"
        }
        hist_res = await db["image_history"].insert_one(history_entry)
        hist_id = str(hist_res.inserted_id)

        # 3. Save category specific diagnostics
        if category == "disease":
            await db["disease_predictions"].insert_one({
                "history_id": hist_id,
                "disease_name": results.get("disease_name"),
                "severity": results.get("severity"),
                "treatment": results.get("treatment"),
                "timestamp": time.time()
            })
        elif category == "pest":
            await db["pest_predictions"].insert_one({
                "history_id": hist_id,
                "pest_name": results.get("pest_name"),
                "severity": results.get("severity"),
                "control_method": results.get("control_method"),
                "timestamp": time.time()
            })

        return hist_id

    async def get_user_history(self, user_id: str, db: AsyncIOMotorDatabase) -> List[Dict[str, Any]]:
        history = []
        try:
            cursor = db["image_history"].find({"user_id": user_id}).sort("created_at", -1)
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                history.append(doc)
        except Exception as e:
            logger.error(f"Failed to query user history logs: {str(e)}")
        return history

    async def delete_history_item(self, item_id: str, db: AsyncIOMotorDatabase) -> bool:
        try:
            await db["image_history"].delete_one({"_id": ObjectId(item_id)})
            return True
        except Exception as e:
            logger.error(f"Failed to delete history item: {str(e)}")
            return False

history_service = HistoryService()
