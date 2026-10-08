import os
import time
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.api.deps import get_db, get_current_user
from app.models.user import UserDB
from app.ai.plant_health.vision import image_manager, disease_prediction_service, image_analysis_service
from app.ai.plant_health.ocr import ocr_service
from app.ai.plant_health.audio import speech_recognition_service, tts_service
from app.ai.plant_health.history import history_service
from app.ai.plant_health.reports import report_generation_service
from pydantic import BaseModel, Field

router = APIRouter()

# Schema definitions
class CompareRequest(BaseModel):
    before_image_path: str = Field(..., description="Staged path of the original scan.")
    after_image_path: str = Field(..., description="Staged path of the follow-up scan.")

class SpeechSpeakRequest(BaseModel):
    text: str = Field(..., description="Response text to synthesize.")
    language: str = Field(default="en", description="Vocal dialect (en, hi, gu).")
    speed: float = Field(default=1.0, description="Rate speed of the voice.")

# --- Image endpoints ---

@router.post("/image/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    # Stage file upload locally in temp folder
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)
    
    with open(temp_path, "wb") as f:
        f.write(await file.read())
        
    try:
        # Preprocess
        pre = image_manager.preprocess_image(temp_path)
        # Mock analysis prediction details
        analysis_res = {
            "crop": "Tomato",
            "leaf_health_index": "Fair",
            "symptoms_identified": ["spots", "chlorosis"],
            "recommendation": "Spray nitrogenous fertilizers and organic composts.",
            "confidence": 0.89
        }
        hist_id = await history_service.log_image_prediction(
            user_id=current_user.id,
            category="analysis",
            image_path=temp_path,
            results=analysis_res,
            db=db
        )
        analysis_res["history_id"] = hist_id
        return analysis_res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/image/disease")
async def detect_disease(
    file: UploadFile = File(...),
    plant_part: str = Form(default="Leaf"),
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)
    
    with open(temp_path, "wb") as f:
        f.write(await file.read())
        
    try:
        pre = image_manager.preprocess_image(temp_path)
        pred = disease_prediction_service.predict_disease(pre, plant_part)
        
        hist_id = await history_service.log_image_prediction(
            user_id=current_user.id,
            category="disease",
            image_path=temp_path,
            results=pred,
            db=db
        )
        pred["history_id"] = hist_id
        return pred
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/image/pest")
async def detect_pest(
    file: UploadFile = File(...),
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)
    
    with open(temp_path, "wb") as f:
        f.write(await file.read())
        
    try:
        pre = image_manager.preprocess_image(temp_path)
        pest_res = {
            "crop": "Cotton",
            "pest_name": "Aphids infestation",
            "severity": "High",
            "confidence": 0.91,
            "control_method": "Spray organic neem oil extract combined with insecticidal soap.",
            "organic_solution": "Neem oil spray (10ml per Litre).",
            "chemical_solution": "Apply imidacloprid insecticide dosage.",
            "expected_recovery": "7-10 days"
        }
        hist_id = await history_service.log_image_prediction(
            user_id=current_user.id,
            category="pest",
            image_path=temp_path,
            results=pest_res,
            db=db
        )
        pest_res["history_id"] = hist_id
        return pest_res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.get("/image/history")
async def get_image_history(
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    history = await history_service.get_user_history(current_user.id, db)
    return history

@router.delete("/image/history/{item_id}")
async def delete_image_history_item(
    item_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    success = await history_service.delete_history_item(item_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="History item not found.")
    return {"deleted": True, "id": item_id}


# --- OCR endpoints ---

@router.post("/ocr/extract")
async def extract_ocr_document(
    file: UploadFile = File(...),
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)
    
    with open(temp_path, "wb") as f:
        f.write(await file.read())
        
    try:
        extracted = ocr_service.extract_text(temp_path)
        
        # Log to MongoDB ocr_documents collection
        await db["ocr_documents"].insert_one({
            "user_id": current_user.id,
            "file_name": file.filename,
            "document_type": extracted.get("document_type"),
            "extracted_data": extracted,
            "timestamp": time.time()
        })
        return extracted
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# --- Speech endpoints ---

@router.post("/speech/transcribe")
async def transcribe_audio_file(
    file: UploadFile = File(...),
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)
    
    with open(temp_path, "wb") as f:
        f.write(await file.read())
        
    try:
        transcription = speech_recognition_service.transcribe_audio(temp_path)
        
        # Log to MongoDB speech_logs / voice_history collections
        await db["speech_logs"].insert_one({
            "user_id": current_user.id,
            "file_name": file.filename,
            "transcript": transcription.get("transcript"),
            "language": transcription.get("detected_language"),
            "timestamp": time.time()
        })
        return transcription
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/speech/speak")
async def speak_text_to_audio(
    req: SpeechSpeakRequest,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    audio_meta = tts_service.generate_speech(
        text=req.text,
        language=req.language,
        voice_speed=req.speed
    )
    
    # Log to MongoDB voice_history collection
    await db["voice_history"].insert_one({
        "user_id": current_user.id,
        "text": req.text,
        "audio_url": audio_meta.get("speech_audio_url"),
        "timestamp": time.time()
    })
    return audio_meta
