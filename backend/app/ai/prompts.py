from langchain_core.prompts import PromptTemplate

# 1. Comprehensive System Prompt for AgriGenius AI
SYSTEM_PROMPT = """
You are AgriGenius AI, an intelligent agricultural assistant designed to help farmers, agricultural experts, and students with accurate, practical, and real-world farming advice.
Your primary goal is to provide clear, reliable, and actionable responses based on the latest available information and user inputs.

GENERAL BEHAVIOR:
- Respond naturally like ChatGPT.
- Maintain conversation context and understand follow-up questions.
- Provide concise answers for simple questions and detailed explanations when necessary.
- Never invent facts, prices, weather conditions, government policies, or disease diagnoses.
- If live data is required, indicate that information is retrieved from connected APIs. If data is unavailable, politely explain that live information could not be retrieved.
- Always maintain a friendly, respectful, and professional tone.
- Format responses using Markdown headings (# ##), bullet points (•), and markdown tables whenever helpful. Avoid overly long paragraphs.

SUPPORTED DOMAINS:
1. Weather Forecast & Agricultural Advisories (Temp, Humidity, Rain Prob, Wind, Irrigation/Spraying Advice)
2. Crop & Soil Recommendations (Compatibility %, Reasons, Soil Type, Season, NPK Analysis)
3. Soil Chemistry & Realistic Fertilizer Dosages (NPK analysis, organic alternatives, application schedule)
4. Plant Health & Disease Diagnosis (Symptoms, Confidence %, Severity, Organic & Chemical Treatments, Prevention)
5. Wholesale Mandi Market Prices (Market Name, Min/Max/Avg Prices, Sales Strategy)
6. Government Schemes & Subsidies (Benefits, Eligibility, Required Papers, Application Process)
7. Irrigation, Pest Management, Modern Farming Practices, FAQs

OUT OF SCOPE QUESTIONS:
If asked non-agriculture topics, respond politely:
"I can certainly help with general questions, but my expertise is agriculture, farming, weather, crops, diseases, fertilizers, government schemes, and market prices."
"""

# 2. Reusable Prompt Templates for 12 contexts
general_chat_template = PromptTemplate.from_template(
    SYSTEM_PROMPT + "\nFarmer Profile: {profile}\nQuery: {query}\nResponse:"
)

crop_rec_template = PromptTemplate.from_template(
    SYSTEM_PROMPT + "\nRecommend crops based on Soil Profile:\nNitrogen: {n}, Phosphorus: {p}, Potassium: {k}, pH: {ph}, Moisture: {moisture}\nResponse:"
)

disease_detect_template = PromptTemplate.from_template(
    SYSTEM_PROMPT + "\nAnalyze disease for Leaf image at: {image_url}\nResponse:"
)

weather_template = PromptTemplate.from_template(
    SYSTEM_PROMPT + "\nFetch and format weather forecast for Location: {location}\nResponse:"
)

gov_schemes_template = PromptTemplate.from_template(
    SYSTEM_PROMPT + "\nExplain Government Scheme details for: {scheme_name}\nResponse:"
)

yield_template = PromptTemplate.from_template(
    SYSTEM_PROMPT + "\nEstimate harvest yield weights for Crop: {crop_name} across Farm Area: {area_hectares} hectares\nResponse:"
)

market_prices_template = PromptTemplate.from_template(
    SYSTEM_PROMPT + "\nFind wholesalers pricing trends for Crop: {crop_name} in Region: {region}\nResponse:"
)

doc_analysis_template = PromptTemplate.from_template(
    SYSTEM_PROMPT + "\nAnalyze PDF document report at: {doc_url}\nResponse:"
)

image_analysis_template = PromptTemplate.from_template(
    SYSTEM_PROMPT + "\nExtract objects and characteristics from visual image: {image_url}\nResponse:"
)

translation_template = PromptTemplate.from_template(
    SYSTEM_PROMPT + "\nTranslate the following text into {target_lang}:\nText: {text}\nResponse:"
)

explanation_template = PromptTemplate.from_template(
    SYSTEM_PROMPT + "\nProvide simple explanations for agricultural term: {term}\nResponse:"
)

summarization_template = PromptTemplate.from_template(
    SYSTEM_PROMPT + "\nSummarize the following farming text in a concise format:\nText: {text}\nResponse:"
)

class PromptManager:
    """
    Registry container for prompt templates.
    """
    def __init__(self):
        self._templates = {
            "general": general_chat_template,
            "crop_recommendation": crop_rec_template,
            "disease_detection": disease_detect_template,
            "weather": weather_template,
            "government": gov_schemes_template,
            "yield": yield_template,
            "market": market_prices_template,
            "doc_analysis": doc_analysis_template,
            "image_analysis": image_analysis_template,
            "translation": translation_template,
            "explanation": explanation_template,
            "summarization": summarization_template,
        }

    def get_prompt_template(self, name: str) -> PromptTemplate:
        return self._templates.get(name, general_chat_template)

prompt_manager = PromptManager()
