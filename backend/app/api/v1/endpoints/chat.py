from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas import chat as chat_schema
from app.db.models import Chat, Message, User
from app.db.session import get_db
from app.services.ai import ai_service
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[chat_schema.Chat])
def get_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    chats = db.query(Chat).filter(Chat.user_id == current_user.id).offset(skip).limit(limit).all()
    return chats

@router.post("/", response_model=chat_schema.Chat)
def create_chat(
    *,
    db: Session = Depends(get_db),
    chat_in: chat_schema.ChatCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    chat = Chat(
        title=chat_in.title,
        user_id=current_user.id,
        created_at=datetime.utcnow().isoformat()
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

@router.get("/{chat_id}/messages", response_model=List[chat_schema.Message])
def get_messages(
    *,
    db: Session = Depends(get_db),
    chat_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    messages = db.query(Message).filter(Message.chat_id == chat_id).all()
    return messages

@router.post("/{chat_id}/messages", response_model=chat_schema.Message)
async def create_message(
    *,
    db: Session = Depends(get_db),
    chat_id: int,
    message_in: chat_schema.MessageCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
        
    # Save User API Message
    user_msg = Message(
        chat_id=chat_id,
        sender="user",
        content=message_in.content,
        timestamp=datetime.utcnow().isoformat()
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)
    
    # Get conversational context
    history_objs = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.id).all()
    history = [{"role": "user" if m.sender == "user" else "assistant", "content": m.content} for m in history_objs]
    
    # Generate AI Response
    # In a real app we'd inject context from the research report if it exists
    ai_response_content = await ai_service.chat(history, context="You are a helpful research assistant.")
    
    ai_msg = Message(
        chat_id=chat_id,
        sender="ai",
        content=ai_response_content,
        timestamp=datetime.utcnow().isoformat()
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)
    
    return ai_msg # Return the AI message? Or user message? Usually the response to the request. 
    # But here we might want to return the AI response. For now return AI message so user sees immediate reply.
