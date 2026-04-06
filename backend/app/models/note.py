from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import uuid


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(default="")
    content_text: str = Field(default="")
    source_type: Literal["note", "url", "pdf"] = "note"
    source_url: Optional[str] = None
    tag_ids: list[str] = []


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    content_text: Optional[str] = None
    tag_ids: Optional[list[str]] = None


class NoteResponse(BaseModel):
    id: str
    user_id: str
    title: str
    content: str
    content_text: str
    source_type: str
    source_url: Optional[str]
    file_path: Optional[str]
    is_public: bool
    public_slug: Optional[str]
    is_starred: bool = False
    is_deleted: bool = False
    tags: list[dict] = []
    created_at: datetime
    updated_at: datetime


class NotePublicToggle(BaseModel):
    is_public: bool


class NoteStarToggle(BaseModel):
    is_starred: bool
