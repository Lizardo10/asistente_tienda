"""
Modelo simplificado de Product sin relaciones complejas
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class ProductBase(SQLModel):
    """Base para el modelo de producto"""
    name: str = Field(max_length=100)
    description: str = Field(max_length=1000)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    active: bool = Field(default=True)


class Product(ProductBase, table=True):
    """Modelo de producto simplificado"""
    __tablename__ = "products"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    image_url: Optional[str] = Field(default="", max_length=500)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class ProductCreate(ProductBase):
    """Modelo para crear producto"""
    image_url: Optional[str] = Field(default="", max_length=500)


class ProductRead(ProductBase):
    """Modelo para leer producto"""
    id: int
    image_url: Optional[str]
    created_at: Optional[datetime]


class ProductUpdate(SQLModel):
    """Modelo para actualizar producto"""
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    price: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    active: Optional[bool] = None
    image_url: Optional[str] = Field(default=None, max_length=500)
