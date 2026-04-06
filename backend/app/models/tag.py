from pydantic import BaseModel, Field
from typing import Optional


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#6366f1")


class TagUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = None


class TagResponse(BaseModel):
    id: str
    user_id: str
    name: str
    color: str
    note_count: int = 0
