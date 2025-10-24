"""
Modelos SQLModel para el área contable
Incluye inventario, ventas, reportes financieros
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum

from app.database.base import BaseModel, TimestampMixin


class TransactionType(str, Enum):
    """Tipos de transacciones contables"""
    SALE = "sale"           # Venta
    PURCHASE = "purchase"   # Compra
    ADJUSTMENT = "adjustment" # Ajuste de inventario
    RETURN = "return"        # Devolución
    DAMAGE = "damage"        # Daño/Pérdida


class InventoryTransaction(BaseModel, TimestampMixin, table=True):
    """Transacciones de inventario"""
    __tablename__ = "inventory_transactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id")
    transaction_type: TransactionType = Field(index=True)
    quantity: int = Field()  # Positivo para entrada, negativo para salida
    unit_cost: Decimal = Field(max_digits=10, decimal_places=2)
    total_cost: Decimal = Field(max_digits=10, decimal_places=2)
    reference_order_id: Optional[int] = Field(default=None, foreign_key="orders.id")
    notes: Optional[str] = Field(default=None)
    admin_user_id: int = Field(foreign_key="users.id")
    
    # Relaciones
    product: "Product" = Relationship()
    order: Optional["Order"] = Relationship()
    admin_user: "User" = Relationship()


class StockLevel(BaseModel, TimestampMixin, table=True):
    """Niveles de stock actuales por producto"""
    __tablename__ = "stock_levels"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id", unique=True, index=True)
    current_stock: int = Field(default=0)
    min_stock_level: int = Field(default=10)  # Nivel mínimo de stock
    max_stock_level: int = Field(default=100)  # Nivel máximo de stock
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    # Relaciones
    product: "Product" = Relationship()


class FinancialReport(BaseModel, TimestampMixin, table=True):
    """Reportes financieros"""
    __tablename__ = "financial_reports"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    report_type: str = Field(index=True)  # daily, weekly, monthly, yearly
    period_start: datetime = Field()
    period_end: datetime = Field()
    
    # Métricas financieras
    total_sales: Decimal = Field(max_digits=12, decimal_places=2, default=0)
    total_orders: int = Field(default=0)
    total_products_sold: int = Field(default=0)
    average_order_value: Decimal = Field(max_digits=10, decimal_places=2, default=0)
    
    # Métricas de inventario
    total_inventory_value: Decimal = Field(max_digits=12, decimal_places=2, default=0)
    low_stock_products: int = Field(default=0)
    out_of_stock_products: int = Field(default=0)
    
    # Métricas de clientes
    total_customers: int = Field(default=0)
    new_customers: int = Field(default=0)
    
    created_by: int = Field(foreign_key="users.id")
    
    # Relaciones
    creator: "User" = Relationship()


class ProductCost(BaseModel, TimestampMixin, table=True):
    """Costos de productos para cálculo de márgenes"""
    __tablename__ = "product_costs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id", unique=True, index=True)
    cost_price: Decimal = Field(max_digits=10, decimal_places=2)
    selling_price: Decimal = Field(max_digits=10, decimal_places=2)
    margin_percentage: Decimal = Field(max_digits=5, decimal_places=2)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    # Relaciones
    product: "Product" = Relationship()


# Schemas Pydantic para las APIs
class InventoryTransactionCreate(SQLModel):
    """Schema para crear transacción de inventario"""
    product_id: int
    transaction_type: TransactionType
    quantity: int
    unit_cost: Decimal
    notes: Optional[str] = None
    reference_order_id: Optional[int] = None


class InventoryTransactionOut(SQLModel):
    """Schema para mostrar transacción de inventario"""
    id: int
    product_id: int
    transaction_type: TransactionType
    quantity: int
    unit_cost: Decimal
    total_cost: Decimal
    notes: Optional[str]
    reference_order_id: Optional[int]
    admin_user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class StockLevelOut(SQLModel):
    """Schema para mostrar nivel de stock"""
    id: int
    product_id: int
    current_stock: int
    min_stock_level: int
    max_stock_level: int
    last_updated: datetime
    product_name: Optional[str] = None
    product_price: Optional[Decimal] = None
    
    class Config:
        from_attributes = True


class StockAdjustmentRequest(SQLModel):
    """Schema para ajustar stock"""
    product_id: int
    new_quantity: int
    reason: str


class FinancialReportOut(SQLModel):
    """Schema para mostrar reporte financiero"""
    id: int
    report_type: str
    period_start: datetime
    period_end: datetime
    total_sales: Decimal
    total_orders: int
    total_products_sold: int
    average_order_value: Decimal
    total_inventory_value: Decimal
    low_stock_products: int
    out_of_stock_products: int
    total_customers: int
    new_customers: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class DashboardStats(SQLModel):
    """Estadísticas para el dashboard contable"""
    total_sales_today: Decimal
    total_orders_today: int
    total_inventory_value: Decimal
    low_stock_products: int
    out_of_stock_products: int
    total_customers: int
    top_selling_products: List[dict]
    recent_transactions: List[dict]
