import asyncio
from typing import Any, Dict, List, Optional
from langchain_core.callbacks import AsyncCallbackHandler

class StreamingCallbackHandler(AsyncCallbackHandler):
    """
    LangChain Async Callback Handler that pushes newly generated tokens
    into an asyncio Queue to be read by the FastAPI streaming stream generator.
    """
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue
        self.done = asyncio.Event()

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """
        Pushes the generated token to the queue.
        """
        if token:
            await self.queue.put(token)

    async def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """
        Signals completion.
        """
        self.done.set()

    async def on_llm_error(self, error: BaseException, **kwargs: Any) -> None:
        """
        Signals failure.
        """
        await self.queue.put(f"[ERROR] Generation failed: {str(error)}")
        self.done.set()
