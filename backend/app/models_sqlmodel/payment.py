"""
Modelos de Pago y Transacciones usando SQLModel
Para tracking completo de pagos y reportes financieros
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from app.database.base import BaseModel, TimestampMixin


class PaymentTransactionBase(SQLModel):
    """Modelo base para transacción de pago"""
    order_id: int
    payment_method: str = Field(max_length=50)  # paypal, stripe, etc.
    payment_provider_id: Optional[str] = Field(default=None, max_length=100)  # PayPal payment ID
    amount: float = Field(gt=0)
    currency: str = Field(default="USD", max_length=3)
    status: str = Field(default="pending", max_length=50)  # pending, completed, failed, refunded
    transaction_id: Optional[str] = Field(default=None, max_length=100)  # PayPal transaction ID
    payer_id: Optional[str] = Field(default=None, max_length=100)  # PayPal payer ID
    fee_amount: Optional[float] = Field(default=None, ge=0)  # Comisión del proveedor
    net_amount: Optional[float] = Field(default=None, ge=0)  # Cantidad neta después de comisiones
    processed_at: Optional[datetime] = Field(default=None)
    failure_reason: Optional[str] = Field(default=None, max_length=500)


class PaymentTransaction(PaymentTransactionBase, BaseModel, TimestampMixin, table=True):
    """Modelo de transacción de pago en la base de datos"""
    __tablename__ = "payment_transactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    order: Optional["Order"] = Relationship(back_populates="payment_transactions")


class PaymentRefundBase(SQLModel):
    """Modelo base para reembolso"""
    transaction_id: int
    refund_amount: float = Field(gt=0)
    refund_reason: Optional[str] = Field(default=None, max_length=500)
    refund_provider_id: Optional[str] = Field(default=None, max_length=100)
    status: str = Field(default="pending", max_length=50)  # pending, completed, failed
    processed_at: Optional[datetime] = Field(default=None)


class PaymentRefund(PaymentRefundBase, BaseModel, TimestampMixin, table=True):
    """Modelo de reembolso en la base de datos"""
    __tablename__ = "payment_refunds"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: int = Field(foreign_key="payment_transactions.id")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    transaction: Optional[PaymentTransaction] = Relationship()


class FinancialReportBase(SQLModel):
    """Modelo base para reporte financiero"""
    period_start: datetime
    period_end: datetime
    total_revenue: float = Field(default=0.0, ge=0)
    total_transactions: int = Field(default=0, ge=0)
    total_fees: float = Field(default=0.0, ge=0)
    net_revenue: float = Field(default=0.0, ge=0)
    refunded_amount: float = Field(default=0.0, ge=0)
    successful_transactions: int = Field(default=0, ge=0)
    failed_transactions: int = Field(default=0, ge=0)


class FinancialReport(FinancialReportBase, BaseModel, TimestampMixin, table=True):
    """Modelo de reporte financiero en la base de datos"""
    __tablename__ = "financial_reports"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


# Schemas para API
class PaymentTransactionCreate(SQLModel):
    """Modelo para crear transacción de pago"""
    order_id: int
    payment_method: str
    payment_provider_id: Optional[str] = None
    amount: float
    currency: str = "USD"


class PaymentTransactionRead(PaymentTransactionBase):
    """Modelo para leer transacción de pago"""
    id: int
    created_at: datetime


class PaymentRefundCreate(SQLModel):
    """Modelo para crear reembolso"""
    transaction_id: int
    refund_amount: float
    refund_reason: Optional[str] = None


class PaymentRefundRead(PaymentRefundBase):
    """Modelo para leer reembolso"""
    id: int
    created_at: datetime


class FinancialReportRead(FinancialReportBase):
    """Modelo para leer reporte financiero"""
    id: int
    created_at: datetime


class DashboardStats(SQLModel):
    """Estadísticas para el dashboard de administrador"""
    total_revenue: float
    total_orders: int
    total_transactions: int
    successful_transactions: int
    failed_transactions: int
    pending_transactions: int
    total_fees: float
    net_revenue: float
    refunded_amount: float
    average_order_value: float
    conversion_rate: float
    revenue_today: float
    revenue_this_month: float
    revenue_this_year: float
    orders_today: int
    orders_this_month: int
    orders_this_year: int









