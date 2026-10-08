import os
import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class OCRService:
    """
    OCR Document Service.
    Extracts text parameters from soil reports, medicine labels, bills, and parses dosage schedules.
    """
    def __init__(self):
        pass

    def extract_text(self, file_path: str) -> Dict[str, Any]:
        """
        Parses text parameters and returns structured values dynamically based on file contents.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Target OCR document path {file_path} not found.")

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in [".pdf", ".png", ".jpg", ".jpeg", ".txt", ".md", ".json"]:
            raise ValueError(f"Unsupported file format for OCR parsing: {ext}")

        logger.info(f"Extracting OCR text from document: {file_path}...")
        
        # Read the file content as text if it's text-based
        raw_text = ""
        if ext in [".txt", ".md", ".json"]:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    raw_text = f.read()
            except Exception as e:
                logger.error(f"Failed to read file as text: {e}")
                raw_text = ""
        else:
            # For PDF or images, if we don't have binary OCR tools installed,
            # we check if there's a matching text-based sidecar file, or raise a clean error
            sidecar_txt = file_path + ".txt"
            if os.path.exists(sidecar_txt):
                try:
                    with open(sidecar_txt, "r", encoding="utf-8") as f:
                        raw_text = f.read()
                except Exception:
                    raw_text = ""
            else:
                # If it's a binary file and no OCR tools are installed, we raise an exception
                # rather than returning fake mock data.
                raise RuntimeError(
                    f"OCR binary engines (Tesseract/EasyOCR) are not installed, "
                    f"and no text sidecar was found for: {os.path.basename(file_path)}"
                )

        # Clean/sanitize text
        clean_text = " ".join(raw_text.split())
        
        # Run dynamic regex scanners
        numbers = [float(n) for n in re.findall(r"\b\d+\.?\d*\b", clean_text)]
        
        # Look for crop names
        all_crops = ["wheat", "cotton", "paddy", "rice", "potato", "onion", "soyabean", "tomato", "citrus", "grapes"]
        detected_crops = [crop.capitalize() for crop in all_crops if crop in clean_text.lower()]
        
        # Scan for potential medicine/chemical names
        chemical_keywords = ["fungicide", "pesticide", "oxychloride", "neem", "mancozeb", "chlorothalonil", "nitrogen", "phosphorus", "potassium", "npk"]
        detected_chemicals = []
        for word in clean_text.split():
            clean_word = re.sub(r"[^\w\-%]", "", word).lower()
            if any(k in clean_word for k in chemical_keywords) and len(clean_word) > 3:
                detected_chemicals.append(clean_word.capitalize())
        # Deduplicate
        detected_chemicals = list(set(detected_chemicals))

        # Check document type
        lower_text = clean_text.lower()
        if "soil" in lower_text or "ph" in lower_text or "NPK" in clean_text:
            doc_type = "Soil Report"
        elif "label" in lower_text or "dosage" in lower_text or "fungicide" in lower_text or "pesticide" in lower_text:
            doc_type = "Medicine Label"
        else:
            doc_type = "Invoice / Text Document"

        # Search for dosage patterns
        dosage_match = re.search(r"(\d+\.?\d*\s*(g|ml|kg|litres?|per)\s*\/?\s*\w*)", clean_text, re.IGNORECASE)
        dosage = dosage_match.group(1) if dosage_match else ""

        # Dates extraction
        dates = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", clean_text)

        summary = f"Extracted {doc_type}. Found {len(detected_crops)} crop references and {len(detected_chemicals)} chemicals/compounds."
        if dosage:
            summary += f" Recommended dosage identified: {dosage}."

        return {
            "document_type": doc_type,
            "extracted_text": clean_text[:1000],  # truncate if extremely long
            "medicines": detected_chemicals,
            "dosage": dosage,
            "crop_names": detected_crops,
            "numbers": numbers[:10],
            "dates": dates,
            "summary": summary
        }

ocr_service = OCRService()
