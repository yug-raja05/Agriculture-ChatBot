import logging
import os
import json
import ssl
import asyncio
import urllib.request
import urllib.error
from typing import Any, List, Mapping, Optional
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks import CallbackManagerForLLMRun
from app.core.config import settings

logger = logging.getLogger(__name__)
# Triggering uvicorn reload for .env update

def _try_huggingface_router(prompt: str, token: str) -> str:
    """
    Hugging Face Router Chat Completions API call using active token.
    """
    if not token or not token.strip():
        return ""
    
    endpoints = [
        ("https://router.huggingface.co/hf-inference/v1/chat/completions", "Qwen/Qwen2.5-7B-Instruct"),
        ("https://router.huggingface.co/hf-inference/v1/chat/completions", "mistralai/Mistral-7B-Instruct-v0.2"),
        ("https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct", None)
    ]
    
    for url, model_id in endpoints:
        try:
            headers = {
                "Authorization": f"Bearer {token.strip()}",
                "Content-Type": "application/json"
            }
            if model_id:
                payload = {
                    "model": model_id,
                    "messages": [
                        {"role": "system", "content": "You are AgriGenius AI, an intelligent real-time agricultural assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 1024,
                    "temperature": 0.7
                }
            else:
                payload = {
                    "inputs": prompt,
                    "parameters": {"max_new_tokens": 512, "temperature": 0.7, "return_full_text": False}
                }
                
            data = json.dumps(payload).encode("utf-8")
            ctx = ssl._create_unverified_context()
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                if isinstance(res_json, dict):
                    choices = res_json.get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content", "")
                        if content:
                            return content
                    gen_text = res_json.get("generated_text", "")
                    if gen_text:
                        return gen_text
                elif isinstance(res_json, list) and len(res_json) > 0:
                    gen_text = res_json[0].get("generated_text", "")
                    if gen_text:
                        return gen_text
        except Exception as e:
            logger.debug(f"HF Inference endpoint {url} failed: {e}")
            
    return ""

class GeminiLLM(LLM):
    """
    Google Gemini & Multi-Provider Real-Time Agent LLM integration.
    Supports official google-generativeai package, Gemini REST API, and Hugging Face API fallback.
    """
    model_config = {"protected_namespaces": ()}
    api_key: str = ""
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.7

    @property
    def _llm_type(self) -> str:
        return "gemini"

    def get_explicit_gemini_key(self) -> str:
        # Check explicit Gemini/Google AI keys first
        for key_candidate in [
            self.api_key,
            getattr(settings, "GEMINI_API_KEY", ""),
            getattr(settings, "GOOGLE_API_KEY", ""),
            getattr(settings, "GOOGLE_MAPS_API_KEY", ""),
            os.getenv("GEMINI_API_KEY", ""),
            os.getenv("GOOGLE_API_KEY", ""),
            os.getenv("GOOGLE_GENERATIVE_AI_API_KEY", ""),
            os.getenv("GOOGLE_MAPS_API_KEY", "")
        ]:
            if key_candidate and key_candidate.strip().startswith("AIzaSy"):
                return key_candidate.strip()
        return ""

    def get_hf_token(self) -> str:
        for token_candidate in [
            getattr(settings, "GEMINI_API_KEY", ""),
            getattr(settings, "HF_TOKEN", ""),
            getattr(settings, "HUGGINGFACE_API_KEY", ""),
            getattr(settings, "CHATBOT_API_KEY", ""),
            os.getenv("GEMINI_API_KEY", ""),
            os.getenv("HF_TOKEN", ""),
            os.getenv("HUGGINGFACE_API_KEY", ""),
            os.getenv("CHATBOT_API_KEY", "")
        ]:
            if token_candidate and (token_candidate.strip().startswith("AQ.") or token_candidate.strip().startswith("hf_")):
                return token_candidate.strip()
        return ""

    def get_effective_model(self) -> str:
        model = (
            self.model_name or 
            getattr(settings, "GEMINI_MODEL", "") or 
            os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        )
        if model.startswith("models/"):
            model = model[7:]
        return model

    def _generate_with_rest(self, prompt: str) -> str:
        gemini_key = self.get_explicit_gemini_key()
        
        if gemini_key:
            candidate_models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-pro"]
            primary = self.get_effective_model()
            if primary and primary in candidate_models:
                candidate_models.remove(primary)
                candidate_models.insert(0, primary)
            elif primary:
                candidate_models.insert(0, primary)

            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": self.temperature,
                    "maxOutputTokens": 2048
                }
            }
            data = json.dumps(payload).encode("utf-8")

            for m_name in candidate_models:
                for api_ver in ["v1beta", "v1"]:
                    url = f"https://generativelanguage.googleapis.com/{api_ver}/models/{m_name}:generateContent?key={gemini_key}"
                    req = urllib.request.Request(
                        url, 
                        data=data, 
                        headers={"Content-Type": "application/json"}, 
                        method="POST"
                    )
                    try:
                        ctx = ssl._create_unverified_context()
                        with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
                            res_json = json.loads(resp.read().decode("utf-8"))
                            candidates = res_json.get("candidates", [])
                            if candidates:
                                parts = candidates[0].get("content", {}).get("parts", [])
                                if parts:
                                    text_res = parts[0].get("text", "")
                                    if text_res and text_res.strip():
                                        logger.info(f"Successfully generated response from Gemini API ({m_name}/{api_ver}).")
                                        return text_res.strip()
                    except Exception as e:
                        logger.debug(f"Gemini REST call failed for {m_name} ({api_ver}): {e}")
        else:
            logger.warning("No valid Gemini API key found, skipping Gemini REST calls.")

        # Try Hugging Face Inference Router API fallback
        hf_token = self.get_hf_token()
        if hf_token:
            hf_output = _try_huggingface_router(prompt, hf_token)
            if hf_output:
                return hf_output

        return ""

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        gemini_key = self.get_explicit_gemini_key()
        if gemini_key:
            # 1. Try google.generativeai SDK if available
            for m_candidate in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-pro"]:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=gemini_key)
                    model = genai.GenerativeModel(m_candidate)
                    response = model.generate_content(prompt)
                    if response and hasattr(response, "text") and response.text:
                        logger.info(f"Gemini SDK generated response with model {m_candidate}.")
                        return response.text
                except Exception as e:
                    logger.debug(f"Gemini SDK failed with model {m_candidate}: {e}")

            # 2. Try direct REST endpoint
            rest_out = self._generate_with_rest(prompt)
            if rest_out:
                return rest_out

        return self._generate_with_rest(prompt)

    async def astream_tokens(self, prompt: str, queue: asyncio.Queue) -> str:
        full_text = ""
        gemini_key = self.get_explicit_gemini_key()
        
        if gemini_key:
            # Try SDK streaming
            for m_candidate in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-pro"]:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=gemini_key)
                    model = genai.GenerativeModel(m_candidate)
                    
                    loop = asyncio.get_running_loop()
                    response_stream = await loop.run_in_executor(
                        None, lambda: model.generate_content(prompt, stream=True)
                    )
                    for chunk in response_stream:
                        if hasattr(chunk, "text") and chunk.text:
                            text_chunk = chunk.text
                            full_text += text_chunk
                            await queue.put(text_chunk)
                            await asyncio.sleep(0.01)
                    if full_text and full_text.strip():
                        return full_text
                except Exception as e:
                    logger.debug(f"Gemini SDK streaming failed with {m_candidate}: {e}")

        # REST / direct call fallback with word-by-word streaming token push
        try:
            full_text = await asyncio.to_thread(self._call, prompt)
            if full_text and full_text.strip():
                words = full_text.split(" ")
                for i, word in enumerate(words):
                    chunk = word if i == 0 else " " + word
                    await queue.put(chunk)
                    await asyncio.sleep(0.01)
                return full_text
        except Exception as e:
            logger.error(f"LLM streaming error: {e}")
        return ""

class MockQwenLLM(LLM):
    model_config = {"protected_namespaces": ()}
    model_name: str = "Mock Qwen 3 8B (Fallback)"
    temperature: float = 0.7

    @property
    def _llm_type(self) -> str:
        return "mock_qwen_8b"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        return "Hello! I am AgriGenius, your agricultural AI advisor. Ask me anything about crop care, leaf diseases, or regional weather forecasts."

class ModelLoader:
    def __init__(self):
        self._langchain_llm = None

    def load_model(self) -> LLM:
        self._langchain_llm = GeminiLLM()
        return self._langchain_llm

    def reset_model(self):
        self._langchain_llm = None

llm_loader = ModelLoader()

def get_llm() -> LLM:
    return llm_loader.load_model()
