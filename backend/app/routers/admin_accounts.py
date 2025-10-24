"""
Sistema de gestión de cuentas y saldos para PayPal
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
from datetime import datetime

from app.db import get_db
from app.models import User, Order, OrderItem, Product
from app.security import get_current_admin

router = APIRouter(prefix="/admin/accounts", tags=["Admin Accounts"])


def get_receiver_account(db: Session) -> User:
    """
    Obtener o crear la cuenta receptora de PayPal
    """
    # Buscar cuenta receptora (admin especial para recibir pagos)
    receiver = db.query(User).filter(User.email == "paypal_receiver@tienda.com").first()
    
    if not receiver:
        # Crear cuenta receptora si no existe
        from app.auth_utils import hash_password
        receiver = User(
            email="paypal_receiver@tienda.com",
            password_hash=hash_password("receiver123456"),
            full_name="Cuenta Receptora PayPal",
            is_admin=True,
            role="admin",
            active=True,
            email_verified=True,
            balance=0.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(receiver)
        db.commit()
        db.refresh(receiver)
        print(f"✅ Cuenta receptora creada: {receiver.email}")
    
    return receiver


def update_product_stock(db: Session, order: Order):
    """
    Actualizar stock de productos después de una venta
    """
    try:
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                # Reducir stock
                if hasattr(product, 'stock'):
                    product.stock = max(0, product.stock - item.quantity)
                else:
                    # Si no hay campo stock, agregarlo
                    print(f"⚠️ Producto {product.id} no tiene campo stock")
                
                # Actualizar fecha de modificación
                product.updated_at = datetime.utcnow()
        
        db.commit()
        print(f"✅ Stock actualizado para orden #{order.id}")
        
    except Exception as e:
        print(f"❌ Error actualizando stock: {e}")


def process_paypal_payment(db: Session, order: Order, amount: float):
    """
    Procesar pago de PayPal y actualizar saldos
    """
    try:
        # Obtener cuenta receptora
        receiver = get_receiver_account(db)
        
        # Agregar dinero a la cuenta receptora
        receiver.balance += amount
        
        # Actualizar stock de productos
        update_product_stock(db, order)
        
        # Marcar orden como completada
        order.payment_status = "completed"
        order.status = "completed"
        order.completed_at = datetime.utcnow()
        
        db.commit()
        
        print(f"✅ Pago procesado: Q{amount} agregado a cuenta receptora")
        print(f"✅ Saldo receptor: Q{receiver.balance}")
        
        return receiver
        
    except Exception as e:
        print(f"❌ Error procesando pago: {e}")
        raise


@router.get("/receiver-balance")
async def get_receiver_balance(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Obtener saldo de la cuenta receptora
    """
    try:
        receiver = get_receiver_account(db)
        
        return {
            "receiver_email": receiver.email,
            "balance": receiver.balance,
            "total_orders": db.query(func.count(Order.id)).filter(Order.payment_status == "completed").scalar() or 0,
            "total_revenue": db.query(func.sum(Order.total_amount)).filter(Order.payment_status == "completed").scalar() or 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo saldo: {str(e)}")


@router.post("/add-to-receiver")
async def add_to_receiver_balance(
    amount: float,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Agregar dinero a la cuenta receptora (para pruebas)
    """
    try:
        if amount <= 0:
            raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0")
        
        receiver = get_receiver_account(db)
        receiver.balance += amount
        db.commit()
        
        return {
            "status": "success",
            "message": f"Q{amount} agregado a cuenta receptora",
            "new_balance": receiver.balance
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error agregando saldo: {str(e)}")


@router.get("/financial-summary")
async def get_financial_summary(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Obtener resumen financiero completo
    """
    try:
        receiver = get_receiver_account(db)
        
        # Estadísticas de órdenes
        total_orders = db.query(func.count(Order.id)).filter(Order.payment_status == "completed").scalar() or 0
        total_revenue = db.query(func.sum(Order.total_amount)).filter(Order.payment_status == "completed").scalar() or 0
        
        # Órdenes de hoy
        today = datetime.utcnow().date()
        orders_today = db.query(func.count(Order.id)).filter(
            Order.payment_status == "completed",
            Order.created_at >= today
        ).scalar() or 0
        
        revenue_today = db.query(func.sum(Order.total_amount)).filter(
            Order.payment_status == "completed",
            Order.created_at >= today
        ).scalar() or 0
        
        # Productos más vendidos
        top_products = db.query(
            Product.id,
            Product.title,
            Product.price,
            func.sum(OrderItem.quantity).label('total_sold')
        ).join(OrderItem).join(Order).filter(
            Order.payment_status == "completed"
        ).group_by(Product.id, Product.title, Product.price).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(5).all()
        
        return {
            "receiver_balance": receiver.balance,
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "orders_today": orders_today,
            "revenue_today": float(revenue_today),
            "top_products": [
                {
                    "id": p.id,
                    "title": p.title,
                    "price": float(p.price),
                    "sold": p.total_sold
                }
                for p in top_products
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo resumen: {str(e)}")
