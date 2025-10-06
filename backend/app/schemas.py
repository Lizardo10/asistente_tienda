from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional
from datetime import datetime

# -------------------
# Auth
# -------------------
class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: Optional[str] = ""
    password: str

    @field_validator("password")
    @classmethod
    def password_len(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Recuperación de contraseña
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


# -------------------
# Products
# -------------------
class ProductImageOut(BaseModel):
    id: int
    url: str
    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    title: str
    description: str = ""
    price: float
    image_url: str = ""   # principal opcional

    @field_validator("price")
    @classmethod
    def non_negative_price(cls, v: float) -> float:
        if v < 0:
            raise ValueError("El precio no puede ser negativo")
        return v

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    active: Optional[bool] = None

class ProductOut(BaseModel):
    id: int
    title: str
    description: str
    price: float
    image_url: str
    active: bool
    images: List[ProductImageOut] = []   # listado de imágenes extra
    class Config:
        from_attributes = True


# -------------------
# Orders
# -------------------
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]


# Salida de ítems de pedido
class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    price_each: float

    class Config:
        from_attributes = True


# Salida de pedido (incluye items)
class OrderOut(BaseModel):
    id: int
    status: str
    created_at: Optional[datetime] = None  # si tu modelo no lo tiene, queda en None
    items: List[OrderItemOut] = []

    class Config:
        from_attributes = True

# -------------------
# Chat
# -------------------
class ChatMessageIn(BaseModel):
    chat_id: int
    content: str

class ChatMessageOut(BaseModel):
    id: int
    chat_id: int
    sender: str
    content: str
    class Config:
        from_attributes = True
class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = ""
    is_admin: bool
    class Config:
        from_attributes = True
