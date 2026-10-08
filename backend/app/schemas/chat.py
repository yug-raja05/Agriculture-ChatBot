from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.chat import MessageSender, MessageAttachment, ToolCallLog

class ChatCreate(BaseModel):
    title: Optional[str] = "New Farming Discussion"

class ChatResponse(BaseModel):
    id: str = Field(alias="id")
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True

class MessageCreate(BaseModel):
    content: str
    attachments: Optional[List[MessageAttachment]] = []

class MessageResponse(BaseModel):
    id: str = Field(alias="id")
    chat_id: str
    sender: MessageSender
    content: str
    attachments: List[MessageAttachment]
    tool_calls: List[ToolCallLog]
    created_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True
