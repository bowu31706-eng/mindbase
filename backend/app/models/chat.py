from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None  # 为空则新建对话
    message: str = Field(..., min_length=1, max_length=2000)


class SourceChunk(BaseModel):
    note_id: str
    note_title: str
    chunk_text: str
    score: float


class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    answer: str
    sources: list[SourceChunk] = []


class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    last_message: Optional[str] = None
