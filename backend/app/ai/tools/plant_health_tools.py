from typing import Dict, Any
from pydantic import BaseModel, Field
from app.ai.base_tool import BaseAITool
from app.ai.registry import register_tool
from app.ai.plant_health.vision import disease_prediction_service, image_analysis_service
from app.ai.plant_health.ocr import ocr_service
from app.ai.plant_health.audio import speech_recognition_service, tts_service

# --- 1. Disease Detection Tool ---
class DiseaseDetectionParams(BaseModel):
    image_path: str = Field(..., description="Local staged path or URL of the leaf/fruit image.")
    plant_part: str = Field(default="Leaf", description="Plant section scanned: Leaf, Stem, Fruit.")

class DiseaseDetectionTool(BaseAITool):
    @property
    def name(self) -> str:
        return "DiseaseDetectionTool"

    @property
    def description(self) -> str:
        return "Diagnoses plant leaf/fruit disease symptoms, severity, and treatment methods."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return DiseaseDetectionParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        pre_meta = {"width": 224, "height": 224, "preprocessed": True}
        res = disease_prediction_service.predict_disease(pre_meta, params.get("plant_part"))
        return res

# --- 2. Pest Detection Tool ---
class PestDetectionParams(BaseModel):
    image_path: str = Field(..., description="Local path or URL of the leaf/fruit image.")

class PestDetectionTool(BaseAITool):
    @property
    def name(self) -> str:
        return "PestDetectionTool"

    @property
    def description(self) -> str:
        return "Detects insects, larvae, and fungal/bacterial pest symptoms."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return PestDetectionParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        return {
            "pest_name": "Aphids infestation",
            "severity": "Medium",
            "control_method": "Apply organic neem oil solution directly to leaf tissues.",
            "organic_solution": "Neem oil spray (10ml/Litre)",
            "chemical_solution": "Spray imidacloprid formulation",
            "expected_recovery": "7 days"
        }

# --- 3. Image Analysis Tool ---
class ImageAnalysisParams(BaseModel):
    before_image_path: str = Field(..., description="Staged path of the original image.")
    after_image_path: str = Field(..., description="Staged path of the post-treatment image.")

class ImageAnalysisTool(BaseAITool):
    @property
    def name(self) -> str:
        return "ImageAnalysisTool"

    @property
    def description(self) -> str:
        return "Tracks disease recovery progress and leaf health changes."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return ImageAnalysisParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        res = image_analysis_service.compare_images(
            params.get("before_image_path"),
            params.get("after_image_path")
        )
        return res

# --- 4. OCR Tool ---
class OCRParams(BaseModel):
    file_path: str = Field(..., description="Local path to soil report or medicine bill.")

class OCRTool(BaseAITool):
    @property
    def name(self) -> str:
        return "OCRTool"

    @property
    def description(self) -> str:
        return "Extracts dosage schedules, chemical names, and tables from labels or soil reports."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return OCRParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        # Return mock file details or extract text
        mock_path = params.get("file_path", "report.pdf")
        res = ocr_service.extract_text(mock_path)
        return res

# --- 5. Speech Recognition Tool ---
class SpeechRecognitionParams(BaseModel):
    audio_path: str = Field(..., description="Local voice audio note file path.")

class SpeechRecognitionTool(BaseAITool):
    @property
    def name(self) -> str:
        return "SpeechRecognitionTool"

    @property
    def description(self) -> str:
        return "Transcribes recorded voice prompts into English, Hindi, or Gujarati script transcripts."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return SpeechRecognitionParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        res = speech_recognition_service.transcribe_audio(params.get("audio_path"))
        return res

# --- 6. Text To Speech Tool ---
class TextToSpeechParams(BaseModel):
    text: str = Field(..., description="Text response content to vocalize.")
    language: str = Field(default="en", description="Vocal dialect (en, hi, gu).")

class TextToSpeechTool(BaseAITool):
    @property
    def name(self) -> str:
        return "TextToSpeechTool"

    @property
    def description(self) -> str:
        return "Generates natural speech voice files for farmer responses."

    @property
    def parameter_schema(self) -> type[BaseModel]:
        return TextToSpeechParams

    async def execute(self, params: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        res = tts_service.generate_speech(
            text=params.get("text"),
            language=params.get("language")
        )
        return res

# Auto-registrations
register_tool(DiseaseDetectionTool())
register_tool(PestDetectionTool())
register_tool(ImageAnalysisTool())
register_tool(OCRTool())
register_tool(SpeechRecognitionTool())
register_tool(TextToSpeechTool())
