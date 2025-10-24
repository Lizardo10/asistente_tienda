"""
Modelos de Usuario usando SQLModel
Siguiendo el principio de Single Responsibility (SOLID)
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from app.database.base import BaseModel, TimestampMixin


class UserBase(SQLModel):
    """Modelo base para usuario"""
    email: str = Field(unique=True, index=True, max_length=255)
    full_name: str = Field(default="", max_length=255)
    is_admin: bool = Field(default=False)
    role: str = Field(default="user", max_length=50)
    balance: float = Field(default=0.0)  # Balance del usuario
    active: bool = Field(default=True)  # Usuario activo/inactivo
    email_verified: bool = Field(default=False)  # Email verificado
    last_login: Optional[datetime] = Field(default=None)  # Último login
    mfa_enabled: bool = Field(default=False)  # MFA habilitado
    mfa_secret: Optional[str] = Field(default=None, max_length=255)  # Secreto TOTP
    email_confirmation_token: Optional[str] = Field(default=None, max_length=255)  # Token de confirmación
    password_reset_token: Optional[str] = Field(default=None, max_length=255)  # Token de reset
    password_reset_expires: Optional[datetime] = Field(default=None)  # Expiración del token


class User(UserBase, BaseModel, TimestampMixin, table=True):
    """Modelo de usuario en la base de datos"""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str = Field(max_length=255)  # Cambiar nombre para consistencia
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    orders: List["Order"] = Relationship(back_populates="user")
    chats: List["Chat"] = Relationship(back_populates="user")
    chat_messages: List["ChatMessage"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    """Modelo para crear usuario"""
    password: str = Field(min_length=6)


class UserRead(UserBase):
    """Modelo para leer usuario"""
    id: int
    created_at: datetime


class UserUpdate(SQLModel):
    """Modelo para actualizar usuario"""
    email: Optional[str] = Field(default=None, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=255)
    is_admin: Optional[bool] = None
    role: Optional[str] = Field(default=None, max_length=50)
    password: Optional[str] = Field(default=None, min_length=6)
