from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# ------------ Message Schemas ------------

class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    """
    Used when the client sends a new user message.
    """
    pass


class MessageRead(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    order_index: int
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ------------ Conversation Schemas ------------

class ConversationCreate(BaseModel):
    user_id: int
    mode: str 
    title: Optional[str] = None
    first_message: str
    document_ids: Optional[List[int]] = None


class ConversationRead(BaseModel):
    id: int
    user_id: int
    mode: str
    title: Optional[str]
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    messages: List[MessageRead]

    class Config:
        from_attributes = True


class ConversationListItem(BaseModel):
    id: int
    user_id: int
    mode: str
    title: Optional[str]
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ------------ User Schemas (simple) ------------

class UserCreate(BaseModel):
    email: str
    full_name: Optional[str] = None


class UserRead(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ------------ Document Schemas ------------

class DocumentCreate(BaseModel):
    user_id: int
    name: str
    source_type: Optional[str] = "upload"
    raw_text: Optional[str] = None


class DocumentRead(BaseModel):
    id: int
    user_id: int
    name: str
    source_type: Optional[str] = None
    storage_path: Optional[str] = None
    raw_text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True