"""
Modelos de Chat usando SQLModel
Siguiendo el principio de Single Responsibility (SOLID)
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from app.database.base import BaseModel, TimestampMixin


class ChatBase(SQLModel):
    """Modelo base para chat"""
    status: str = Field(default="open", max_length=50)


class Chat(ChatBase, BaseModel, TimestampMixin, table=True):
    """Modelo de chat en la base de datos"""
    __tablename__ = "chats"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="chats")
    messages: List["ChatMessage"] = Relationship(back_populates="chat")


class ChatCreate(SQLModel):
    """Modelo para crear chat"""
    user_id: Optional[int] = None


class ChatRead(ChatBase):
    """Modelo para leer chat"""
    id: int
    user_id: Optional[int]
    created_at: datetime
    messages: List["ChatMessageRead"]


class ChatMessageBase(SQLModel):
    """Modelo base para mensaje de chat"""
    sender: str = Field(max_length=50)  # "user" | "bot" | "agent"
    content: str


class ChatMessage(ChatMessageBase, BaseModel, TimestampMixin, table=True):
    """Modelo de mensaje de chat en la base de datos"""
    __tablename__ = "chat_messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    chat_id: int = Field(foreign_key="chats.id")
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    chat: Optional[Chat] = Relationship(back_populates="messages")
    user: Optional["User"] = Relationship(back_populates="chat_messages")


class ChatMessageCreate(ChatMessageBase):
    """Modelo para crear mensaje de chat"""
    chat_id: int
    user_id: Optional[int] = None


class ChatMessageRead(ChatMessageBase):
    """Modelo para leer mensaje de chat"""
    id: int
    chat_id: int
    user_id: Optional[int]
    created_at: datetime
