from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class ChatBase(BaseModel):
    title: str

class ChatCreate(ChatBase):
    pass

class Chat(ChatBase):
    id: int
    user_id: int
    created_at: str
    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    content: str
    sender: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    chat_id: int
    timestamp: str
    class Config:
        from_attributes = True

class ReportBase(BaseModel):
    content: str

class Report(ReportBase):
    id: int
    chat_id: int
    created_at: str
    class Config:
        from_attributes = True
