import uuid
import json
import asyncio
import re
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.api.deps import get_db, get_current_user
from app.ai.agent import agent_coordinator
from app.models.user import UserDB
from app.models.chat import ChatDB, MessageDB, MessageSender
from app.schemas.chat import ChatCreate, ChatResponse, MessageCreate, MessageResponse

router = APIRouter()

def generate_chat_title(user_query: str) -> str:
    """
    Generates a concise, Title Case conversation title (4-8 words) based on the user's initial message.
    """
    clean_text = user_query.strip().replace('"', '').replace("'", "").replace("`", "")
    lower = clean_text.lower()

    # 1. Specific Agricultural Intents First
    # Crop Recommendation Intent
    if any(w in lower for w in ["crop", "grow", "plant", "sow", "cultivate", "soil", "npk", "nitrogen", "profit"]):
        loc_match = re.search(r"\b(?:in|at|near|for|of)\s+([a-zA-Z]+)\b", lower)
        if loc_match and loc_match.group(1).lower() not in ["my", "the", "this", "our", "a", "an", "season"]:
            loc = loc_match.group(1).title()
            return f"Crop Recommendation for {loc}"
        return "Crop Recommendation and Soil Advice"

    # Weather Intent
    if any(w in lower for w in ["weather", "rain", "temperature", "temp", "forecast", "climate"]):
        loc_match = re.search(r"\b(?:in|at|near|for|of)\s+([a-zA-Z]+)\b", lower)
        if loc_match and loc_match.group(1).lower() not in ["today", "tomorrow", "my", "the", "this"]:
            loc = loc_match.group(1).title()
            return f"Weather Forecast for {loc}"
        return "Weather Forecast and Field Advisory"

    # Identity & Greeting Queries (Strict Word Boundaries)
    if any(w in lower for w in ["who are you", "who created you", "your identity", "what is your name"]):
        return "AI Advisor Identity & Capabilities"
    if re.search(r"\b(hello|hi|hey|greetings)\b", lower):
        return "Farming AI Assistant Discussion"

    # 4. Disease & Leaf Health Intent
    if any(w in lower for w in ["disease", "spot", "spots", "blight", "fungus", "pest", "leaf", "leaves", "rot", "health"]):
        crop_match = None
        for crop in ["cotton", "paddy", "wheat", "rice", "tomato", "potato", "onion", "maize", "soybean", "sugarcane"]:
            if crop in lower:
                crop_match = crop.title()
                break
        if crop_match:
            return f"{crop_match} Leaf Disease Diagnosis Details"
        return "Plant Leaf Health Disease Diagnosis"

    # 5. Mandi Market Prices Intent
    if any(w in lower for w in ["price", "mandi", "market", "rate", "cost", "sell"]):
        crop_match = None
        for crop in ["wheat", "paddy", "rice", "cotton", "onion", "potato", "soybean", "mustard"]:
            if crop in lower:
                crop_match = crop.title()
                break
        if crop_match:
            return f"Current {crop_match} Mandi Price Details"
        return "Current Crop Wholesale Mandi Prices"

    # 6. Government Schemes Intent
    if any(w in lower for w in ["scheme", "kisan", "pm-kisan", "pmkisan", "pmfby", "kcc", "loan", "subsidy"]):
        scheme_match = None
        for sch in ["pm-kisan", "pmkisan", "pmfby", "kcc"]:
            if sch in lower:
                scheme_match = sch.upper()
                break
        if scheme_match:
            return f"{scheme_match} Government Scheme Details"
        return "Government Kisan Scheme Subsidies Details"

    # 7. Fallback Rule-based Extraction (4-8 words)
    stop_words = {"what", "is", "are", "the", "a", "an", "tell", "me", "about", "which", "should", "i", "how", "can", "to", "my", "please", "help", "do", "you", "know", "give", "want"}
    tokens = [
        w.capitalize() for w in re.sub(r'[^\w\s]', '', clean_text).split()
        if w.lower() not in stop_words
    ]
    if not tokens:
        tokens = [w.capitalize() for w in clean_text.split()]

    fillers = ["General", "Farming", "Discussion", "Topic"]
    for f in fillers:
        if f not in tokens and len(tokens) < 4:
            tokens.append(f)

    return " ".join(tokens[:8])

@router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_in: ChatCreate,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Creates a new chat session (discussion topic) for the user.
    """
    chat_id = str(uuid.uuid4())
    chat_db = ChatDB(
        _id=chat_id,
        user_id=current_user.id,
        title=chat_in.title or "New Farming Discussion"
    )
    await db["chats"].insert_one(chat_db.model_dump(by_alias=True))
    return chat_db

@router.get("", response_model=List[ChatResponse])
async def list_chats(
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Lists all chat sessions belonging to the logged in user.
    """
    cursor = db["chats"].find({"user_id": current_user.id}).sort("updated_at", -1)
    chats = []
    async for doc in cursor:
        chats.append(ChatDB(**doc))
    return chats

@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Deletes a chat session and all associated messages for the logged in user.
    """
    chat = await db["chats"].find_one({"_id": chat_id, "user_id": current_user.id})
    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat room not found or access denied."
        )
    await db["chats"].delete_one({"_id": chat_id, "user_id": current_user.id})
    await db["messages"].delete_many({"chat_id": chat_id})
    return None

@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(
    chat_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Retrieves message history logs for a specific chat session.
    """
    chat = await db["chats"].find_one({"_id": chat_id, "user_id": current_user.id})
    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat room not found or access denied."
        )
        
    cursor = db["messages"].find({"chat_id": chat_id}).sort("created_at", 1)
    messages = []
    async for doc in cursor:
        messages.append(MessageDB(**doc))
    return messages

@router.post("/{chat_id}/messages", response_model=MessageResponse)
async def send_message(
    chat_id: str,
    msg_in: MessageCreate,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Posts a user message into a chat room, triggers the AI agent coordinator flow,
    and returns the assistant's resolved message with tool logs.
    """
    chat = await db["chats"].find_one({"_id": chat_id, "user_id": current_user.id})
    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat room not found or access denied."
        )

    # Count previous user messages to ensure title is set ONLY once on the first user message
    user_msg_count = await db["messages"].count_documents({"chat_id": chat_id, "sender": {"$in": ["user", "USER"]}})
    if user_msg_count == 0 or chat.get("title") in ["New Farming Discussion", "", None]:
        new_title = generate_chat_title(msg_in.content)
        await db["chats"].update_one(
            {"_id": chat_id},
            {"$set": {"title": new_title, "updated_at": datetime.now(timezone.utc)}}
        )
    else:
        await db["chats"].update_one(
            {"_id": chat_id},
            {"$set": {"updated_at": datetime.now(timezone.utc)}}
        )
        
    # 1. Insert user message record
    user_msg_id = str(uuid.uuid4())
    user_msg = MessageDB(
        _id=user_msg_id,
        chat_id=chat_id,
        sender=MessageSender.USER,
        content=msg_in.content,
        attachments=msg_in.attachments or []
    )
    await db["messages"].insert_one(user_msg.model_dump(by_alias=True))
    
    # 2. Invoke the agent coordinator to process query and execute modular tools
    agent_output = await agent_coordinator.process_chat_query(
        user_id=current_user.id,
        chat_id=chat_id,
        query=msg_in.content,
        attachments=msg_in.attachments or [],
        db=db
    )
    
    # 3. Create and save assistant response record
    assistant_msg_id = str(uuid.uuid4())
    assistant_msg = MessageDB(
        _id=assistant_msg_id,
        chat_id=chat_id,
        sender=MessageSender.ASSISTANT,
        content=agent_output["content"],
        attachments=[],
        tool_calls=agent_output["tool_logs"]
    )
    await db["messages"].insert_one(assistant_msg.model_dump(by_alias=True))
    
    return assistant_msg

@router.post("/{chat_id}/messages/stream")
async def send_message_stream(
    chat_id: str,
    msg_in: MessageCreate,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Server-Sent Events (SSE) streaming API to stream tokens in real-time.
    """
    chat = await db["chats"].find_one({"_id": chat_id, "user_id": current_user.id})
    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat room not found or access denied."
        )

    # Count previous user messages to ensure title is set ONLY once on the first user message
    user_msg_count = await db["messages"].count_documents({"chat_id": chat_id, "sender": {"$in": ["user", "USER"]}})
    updated_title = None
    if user_msg_count == 0 or chat.get("title") in ["New Farming Discussion", "", None]:
        new_title = generate_chat_title(msg_in.content)
        await db["chats"].update_one(
            {"_id": chat_id},
            {"$set": {"title": new_title, "updated_at": datetime.now(timezone.utc)}}
        )
        updated_title = new_title
    else:
        await db["chats"].update_one(
            {"_id": chat_id},
            {"$set": {"updated_at": datetime.now(timezone.utc)}}
        )

    # 1. Insert user message record
    user_msg_id = str(uuid.uuid4())
    user_msg = MessageDB(
        _id=user_msg_id,
        chat_id=chat_id,
        sender=MessageSender.USER,
        content=msg_in.content,
        attachments=msg_in.attachments or []
    )
    await db["messages"].insert_one(user_msg.model_dump(by_alias=True))

    async def event_generator():
        queue = asyncio.Queue()
        
        # 2. Start the query execution task in the background
        task = asyncio.create_task(
            agent_coordinator.process_chat_query(
                user_id=current_user.id,
                chat_id=chat_id,
                query=msg_in.content,
                attachments=msg_in.attachments or [],
                db=db,
                queue=queue
            )
        )

        content = ""
        # 3. Stream generated tokens in real-time as they appear in the queue
        while not task.done() or not queue.empty():
            try:
                token = await asyncio.wait_for(queue.get(), timeout=0.1)
                content += token
                yield f"data: {json.dumps({'token': token})}\n\n"
            except asyncio.TimeoutError:
                continue

        # Wait for the task to complete to get the final metadata (tool call logs)
        agent_output = await task
        tool_logs = agent_output.get("tool_logs", [])

        # 4. Save assistant message record in MongoDB
        assistant_msg_id = str(uuid.uuid4())
        assistant_msg = MessageDB(
            _id=assistant_msg_id,
            chat_id=chat_id,
            sender=MessageSender.ASSISTANT,
            content=content,
            attachments=[],
            tool_calls=tool_logs
        )
        await db["messages"].insert_one(assistant_msg.model_dump(by_alias=True))

        # 5. Yield final completed MessageResponse metadata chunk carrying tool logs and updated title
        response_schema = MessageResponse(
            id=assistant_msg_id,
            chat_id=chat_id,
            sender=MessageSender.ASSISTANT,
            content=content,
            attachments=[],
            tool_calls=tool_logs,
            created_at=assistant_msg.created_at
        )
        payload_data = {'final_payload': response_schema.model_dump(by_alias=True)}
        if updated_title:
            payload_data['chat_title'] = updated_title

        yield f"data: {json.dumps(payload_data, default=str)}\n\n"
        yield "event: close\ndata: \n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
