"""
Modelos de Producto usando SQLModel
Siguiendo el principio de Single Responsibility (SOLID)
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from app.database.base import BaseModel, TimestampMixin


class ProductBase(SQLModel):
    """Modelo base para producto"""
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default="")
    price: float = Field(gt=0)
    category: Optional[str] = Field(default="general", max_length=100)
    stock: int = Field(default=0, ge=0)
    active: bool = Field(default=True)


class Product(ProductBase, BaseModel, TimestampMixin, table=True):
    """Modelo de producto en la base de datos"""
    __tablename__ = "products"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    image_url: Optional[str] = Field(default="", max_length=500)
    
    # Relationships
    images: List["ProductImage"] = Relationship(back_populates="product")
    order_items: List["OrderItem"] = Relationship(back_populates="product")


class ProductCreate(ProductBase):
    """Modelo para crear producto"""
    image_url: Optional[str] = Field(default="", max_length=500)


class ProductRead(ProductBase):
    """Modelo para leer producto"""
    id: int
    image_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


class ProductUpdate(SQLModel):
    """Modelo para actualizar producto"""
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None)
    price: Optional[float] = Field(default=None, gt=0)
    category: Optional[str] = Field(default=None, max_length=100)
    stock: Optional[int] = Field(default=None, ge=0)
    image_url: Optional[str] = Field(default=None, max_length=500)
    active: Optional[bool] = None


class ProductImage(BaseModel, table=True):
    """Modelo para imágenes de productos"""
    __tablename__ = "product_images"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id")
    url: str = Field(max_length=500)
    
    # Relationships
    product: Optional[Product] = Relationship(back_populates="images")
