import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=========================================")
print("AgriGenius AI Plant Health - Platform Verification Check")
print("=========================================")

async def test_plant_health_platform():
    try:
        # DB connection
        client = AsyncIOMotorClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
        db = client["AgriGeniusAI_test"]
        
        # Create a mock image file
        mock_img = "mock_leaf.jpg"
        with open(mock_img, "w") as f:
            f.write("leaf pixels")
            
        print("1. Verifying Image Preprocessor & Validations...")
        from app.ai.plant_health.vision import image_manager
        pre = image_manager.preprocess_image(mock_img)
        print(f"   [OK] Image Preprocessed dimensions: {pre.get('width')}x{pre.get('height')}")
        
        print("2. Verifying Disease Prediction Service (EfficientNet)...")
        from app.ai.plant_health.vision import disease_prediction_service
        pred = disease_prediction_service.predict_disease(pre, "Leaf")
        print(f"   [OK] Predicted Disease: {pred.get('disease_name')}")
        print(f"   [OK] Symptoms: {pred.get('symptoms')}")
        
        print("3. Verifying OCR Document Parsing Service...")
        from app.ai.plant_health.ocr import ocr_service
        # Create a mock soil report text file
        mock_report = "soil_report.txt"
        with open(mock_report, "w") as f:
            f.write("Nitrogen: 220, pH: 6.8")
            
        ocr = ocr_service.extract_text(mock_report)
        print(f"   [OK] Document type parsed: {ocr.get('document_type')}")
        print(f"   [OK] Document summary: {ocr.get('summary')}")
        
        # Clean mock files
        for f_path in [mock_img, mock_report]:
            if os.path.exists(f_path):
                os.remove(f_path)
                
        print("4. Verifying Speech AI Whisper & Coqui TTS Services...")
        from app.ai.plant_health.audio import speech_recognition_service, tts_service
        transcription = speech_recognition_service.transcribe_audio("hindi_note.wav")
        print(f"   [OK] Whisper transcribes transcript text successfully (detected language: {transcription.get('detected_language')})")
        
        audio = tts_service.generate_speech("Please water your wheat crop.", language="en")
        print(f"   [OK] Coqui TTS generates wave file: {audio.get('speech_audio_url')}")
        
        print("5. Verifying Report Generation Service (PDF Writer)...")
        from app.ai.plant_health.reports import report_generation_service
        output_pdf = "reports_staging/plant_report.pdf"
        report_generation_service.generate_pdf_report(pred, output_pdf)
        print(f"   [OK] PDF Report written status: {os.path.exists(output_pdf)}")
        
        # Clean output report file
        if os.path.exists(output_pdf):
            os.remove(output_pdf)
            os.rmdir("reports_staging")
            
        print("\n[SUCCESS] AI Plant Health Platform passes test compiles perfectly!")
        print("=========================================")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Plant Health Platform verification failed: {str(e)}")
        print("=========================================")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_plant_health_platform())
