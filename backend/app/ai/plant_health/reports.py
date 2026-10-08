import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ReportGenerationService:
    """
    Report Generation Service.
    Builds downloadable PDF and text summaries for farmer treatments.
    """
    def __init__(self):
        pass

    def generate_pdf_report(self, diagnosis_results: Dict[str, Any], output_path: str) -> str:
        """
        Generates simulated PDF treatment file.
        """
        logger.info(f"Generating PDF treatment report: {output_path}...")
        
        # Create staging folders if missing
        dir_name = os.path.dirname(output_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
            
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("=========================================\n")
            f.write("      AgriGenius AI - Plant Health Report\n")
            f.write("=========================================\n")
            f.write(f"Disease Detected: {diagnosis_results.get('disease_name', 'Tomato Late Blight')}\n")
            f.write(f"Confidence score: {diagnosis_results.get('confidence', 0.94) * 100}%\n")
            f.write(f"Severity level: {diagnosis_results.get('severity', 'Medium')}\n")
            f.write(f"Symptoms description: {diagnosis_results.get('symptoms', 'None')}\n")
            f.write("-----------------------------------------\n")
            f.write("Recommended Treatments:\n")
            treatment = diagnosis_results.get("treatment", {})
            if isinstance(treatment, dict):
                f.write(f" - Organic: {treatment.get('organic', 'None')}\n")
                f.write(f" - Chemical: {treatment.get('chemical', 'None')}\n")
                f.write(f" - Prevention: {treatment.get('prevention', 'None')}\n")
            else:
                f.write(f" - Advice: {treatment}\n")
            f.write("=========================================\n")
            
        return output_path

report_generation_service = ReportGenerationService()
