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

class GroqLLM(LLM):
    """
    Groq Real-Time Agent LLM integration using the official Groq Python SDK.
    """
    model_config = {"protected_namespaces": ()}
    api_key: str = ""
    model_name: str = "llama-3.3-70b-versatile"
    temperature: float = 0.7

    @property
    def _llm_type(self) -> str:
        return "groq"

    def get_explicit_groq_key(self) -> str:
        for key_candidate in [
            self.api_key,
            getattr(settings, "GROQ_API_KEY", ""),
            os.getenv("GROQ_API_KEY", "")
        ]:
            if key_candidate and key_candidate.strip():
                return key_candidate.strip()
        return ""

    def get_effective_model(self) -> str:
        model = (
            self.model_name or 
            getattr(settings, "GROQ_MODEL", "") or 
            os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        )
        return model

    def _generate_with_groq_sdk(self, prompt: str) -> str:
        groq_key = self.get_explicit_groq_key()
        
        if groq_key:
            model = self.get_effective_model()
            try:
                from groq import Groq
                client = Groq(api_key=groq_key)
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are AgriGenius AI, an agricultural expert. Answer ONLY what the user asks. Keep responses concise and directly relevant. Do NOT add extra unrelated information."},
                        {"role": "user", "content": prompt}
                    ],
                    model=model,
                    temperature=self.temperature,
                    max_tokens=2048
                )
                content = chat_completion.choices[0].message.content
                if content:
                    logger.info(f"Successfully generated response from Groq SDK ({model}).")
                    return content.strip()
            except Exception as e:
                logger.error(f"Groq SDK call failed for {model}: {e}")
                # Try fallback model
                try:
                    from groq import Groq
                    client = Groq(api_key=groq_key)
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "You are AgriGenius AI, an intelligent real-time agricultural assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        model="llama-3.1-8b-instant",
                        temperature=self.temperature,
                        max_tokens=2048
                    )
                    content = chat_completion.choices[0].message.content
                    if content:
                        logger.info("Successfully generated response from Groq SDK (llama-3.1-8b-instant fallback).")
                        return content.strip()
                except Exception as e2:
                    logger.error(f"Groq SDK fallback also failed: {e2}")
        else:
            logger.warning("No valid Groq API key found.")

        # Try Hugging Face Inference Router API fallback
        hf_token = self._get_hf_token()
        if hf_token:
            hf_output = _try_huggingface_router(prompt, hf_token)
            if hf_output:
                return hf_output

        return ""

    def _get_hf_token(self) -> str:
        for token_candidate in [
            getattr(settings, "HF_TOKEN", ""),
            getattr(settings, "HUGGINGFACE_API_KEY", ""),
            os.getenv("HF_TOKEN", ""),
            os.getenv("HUGGINGFACE_API_KEY", "")
        ]:
            if token_candidate and (token_candidate.strip().startswith("AQ.") or token_candidate.strip().startswith("hf_")):
                return token_candidate.strip()
        return ""

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        return self._generate_with_groq_sdk(prompt)

    async def astream_tokens(self, prompt: str, queue: asyncio.Queue) -> str:
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
        self._langchain_llm = GroqLLM()
        return self._langchain_llm

    def reset_model(self):
        self._langchain_llm = None

llm_loader = ModelLoader()

def get_llm() -> LLM:
        return llm_loader.load_model()
