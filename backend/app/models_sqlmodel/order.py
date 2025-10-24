"""
Modelos de Orden usando SQLModel
Siguiendo el principio de Single Responsibility (SOLID)
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from app.database.base import BaseModel, TimestampMixin


class OrderBase(SQLModel):
    """Modelo base para orden"""
    status: str = Field(default="pending", max_length=50)
    total_amount: float = Field(default=0.0)
    payment_method: Optional[str] = Field(default=None, max_length=50)
    payment_status: Optional[str] = Field(default="pending", max_length=50)
    payment_id: Optional[str] = Field(default=None, max_length=100)
    payer_id: Optional[str] = Field(default=None, max_length=100)
    completed_at: Optional[datetime] = Field(default=None)


class Order(OrderBase, BaseModel, TimestampMixin, table=True):
    """Modelo de orden en la base de datos"""
    __tablename__ = "orders"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="orders")
    items: List["OrderItem"] = Relationship(back_populates="order")
    payment_transactions: List["PaymentTransaction"] = Relationship(back_populates="order")


class OrderCreate(SQLModel):
    """Modelo para crear orden"""
    items: List["OrderItemCreate"]


class OrderRead(OrderBase):
    """Modelo para leer orden"""
    id: int
    user_id: int
    created_at: datetime
    items: List["OrderItemRead"]


class OrderItemBase(SQLModel):
    """Modelo base para item de orden"""
    product_id: int
    quantity: int = Field(gt=0)
    price_each: float = Field(gt=0)


class OrderItem(OrderItemBase, BaseModel, table=True):
    """Modelo de item de orden en la base de datos"""
    __tablename__ = "order_items"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    product_id: int = Field(foreign_key="products.id")
    
    # Relationships
    order: Optional[Order] = Relationship(back_populates="items")
    product: Optional["Product"] = Relationship(back_populates="order_items")


class OrderItemCreate(OrderItemBase):
    """Modelo para crear item de orden"""
    pass


class OrderItemRead(OrderItemBase):
    """Modelo para leer item de orden"""
    id: int
    order_id: int
