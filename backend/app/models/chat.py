from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class MessageSender(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class MessageAttachment(BaseModel):
    file_type: str  # "image", "audio", "pdf", "csv"
    url: str
    ocr_text: Optional[str] = None  # If scanned/OCR'd

class ToolCallLog(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    output: Dict[str, Any]
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MessageDB(BaseModel):
    id: str = Field(alias="_id")
    chat_id: str
    sender: MessageSender
    content: str
    attachments: List[MessageAttachment] = []
    tool_calls: List[ToolCallLog] = []  # Tracks internal tool usages (crop rec, weather call, etc)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatDB(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    title: str = "New Farming Discussion"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
