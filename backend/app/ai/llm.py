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
                        {"role": "system", "content": "You are AgriGenius AI, a knowledgeable and helpful assistant with deep expertise in agriculture."},
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

class MistralLLM(LLM):
    """
    Mistral AI LLM integration using the OpenAI-compatible Python SDK.
    Mistral exposes an OpenAI-compatible API at https://api.mistral.ai/v1
    """
    model_config = {"protected_namespaces": ()}
    api_key: str = ""
    model_name: str = "mistral-small-latest"
    temperature: float = 0.7

    @property
    def _llm_type(self) -> str:
        return "mistral"

    def get_explicit_api_key(self) -> str:
        for key_candidate in [
            self.api_key,
            getattr(settings, "MISTRAL_API_KEY", ""),
            os.getenv("MISTRAL_API_KEY", "")
        ]:
            if key_candidate and key_candidate.strip():
                return key_candidate.strip()
        return ""

    def get_effective_model(self) -> str:
        model = (
            self.model_name or 
            getattr(settings, "MISTRAL_MODEL", "") or 
            os.getenv("MISTRAL_MODEL", "mistral-small-latest")
        )
        return model

    def _generate_with_mistral(self, prompt: str) -> str:
        api_key = self.get_explicit_api_key()
        
        if api_key:
            model = self.get_effective_model()
            try:
                from openai import OpenAI
                client = OpenAI(
                    base_url="https://api.mistral.ai/v1",
                    api_key=api_key
                )
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are AgriGenius AI, a knowledgeable and helpful assistant. You can answer questions on any topic. You have deep expertise in agriculture, farming, crops, soil, weather, livestock, mandi prices, fertilizers, plant diseases, and government farming schemes. For non-agriculture questions, answer helpfully using your general knowledge. Keep answers concise, well-formatted with Markdown, and relevant."},
                        {"role": "user", "content": prompt}
                    ],
                    model=model,
                    temperature=self.temperature,
                    max_tokens=2048
                )
                content = chat_completion.choices[0].message.content
                if content:
                    logger.info(f"Successfully generated response from Mistral ({model}).")
                    return content.strip()
            except Exception as e:
                logger.error(f"Mistral call failed for {model}: {e}")
                # Try fallback model
                try:
                    from openai import OpenAI
                    client = OpenAI(
                        base_url="https://api.mistral.ai/v1",
                        api_key=api_key
                    )
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "You are AgriGenius AI, an intelligent real-time agricultural assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        model="open-mistral-nemo",
                        temperature=self.temperature,
                        max_tokens=2048
                    )
                    content = chat_completion.choices[0].message.content
                    if content:
                        logger.info("Successfully generated response from Mistral (open-mistral-nemo fallback).")
                        return content.strip()
                except Exception as e2:
                    logger.error(f"Mistral fallback also failed: {e2}")
        else:
            logger.warning("No valid Mistral API key found.")

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
        return self._generate_with_mistral(prompt)

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
        self._langchain_llm = MistralLLM()
        return self._langchain_llm

    def reset_model(self):
        self._langchain_llm = None

llm_loader = ModelLoader()

def get_llm() -> LLM:
        return llm_loader.load_model()
