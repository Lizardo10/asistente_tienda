"""
Router para funcionalidades administrativas financieras
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.db import get_db
from app.models import User, Order, OrderItem, Product
from app.security import get_current_admin

router = APIRouter(prefix="/admin/financial", tags=["Admin Financial"])


@router.get("/dashboard")
async def get_financial_dashboard(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Obtener estadísticas del dashboard financiero
    """
    try:
        # Calcular fechas
        today = datetime.utcnow().date()
        month_start = today.replace(day=1)
        year_start = today.replace(month=1, day=1)
        
        # Ingresos totales
        total_revenue = db.query(func.sum(Order.total_amount)).filter(
            Order.payment_status == "completed"
        ).scalar() or 0
        
        # Ingresos este mes
        revenue_this_month = db.query(func.sum(Order.total_amount)).filter(
            Order.payment_status == "completed",
            Order.created_at >= month_start
        ).scalar() or 0
        
        # Total de órdenes
        total_orders = db.query(func.count(Order.id)).filter(
            Order.payment_status == "completed"
        ).scalar() or 0
        
        # Órdenes este mes
        orders_this_month = db.query(func.count(Order.id)).filter(
            Order.payment_status == "completed",
            Order.created_at >= month_start
        ).scalar() or 0
        
        # Órdenes hoy
        orders_today = db.query(func.count(Order.id)).filter(
            Order.payment_status == "completed",
            Order.created_at >= today
        ).scalar() or 0
        
        # Ingresos hoy
        revenue_today = db.query(func.sum(Order.total_amount)).filter(
            Order.payment_status == "completed",
            Order.created_at >= today
        ).scalar() or 0
        
        # Usuarios activos (que han hecho al menos una compra)
        active_users = db.query(func.count(func.distinct(Order.user_id))).filter(
            Order.payment_status == "completed"
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
            desc('total_sold')
        ).limit(5).all()
        
        # Órdenes recientes
        recent_orders = db.query(Order).join(User).filter(
            Order.payment_status == "completed"
        ).order_by(desc(Order.created_at)).limit(10).all()
        
        return {
            "total_revenue": float(total_revenue),
            "revenue_this_month": float(revenue_this_month),
            "revenue_today": float(revenue_today),
            "total_orders": total_orders,
            "orders_this_month": orders_this_month,
            "orders_today": orders_today,
            "active_users": active_users,
            "top_products": [
                {
                    "id": p.id,
                    "title": p.title,
                    "price": float(p.price),
                    "sales": p.total_sold
                }
                for p in top_products
            ],
            "recent_orders": [
                {
                    "id": o.id,
                    "customer_email": o.user.email if o.user else "N/A",
                    "total_amount": float(o.total_amount),
                    "status": o.status,
                    "created_at": o.created_at.isoformat()
                }
                for o in recent_orders
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")


@router.get("/transactions")
async def get_transactions(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Obtener todas las transacciones completadas
    """
    try:
        transactions = db.query(Order).filter(
            Order.payment_status == "completed"
        ).order_by(desc(Order.created_at)).all()
        
        return [
            {
                "id": t.id,
                "user_email": t.user.email if t.user else "N/A",
                "amount": float(t.total_amount),
                "payment_method": t.payment_method,
                "status": t.status,
                "created_at": t.created_at.isoformat(),
                "completed_at": t.completed_at.isoformat() if t.completed_at else None
            }
            for t in transactions
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo transacciones: {str(e)}")


@router.get("/orders")
async def get_orders(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Obtener todas las órdenes
    """
    try:
        orders = db.query(Order).join(User).order_by(desc(Order.created_at)).all()
        
        return [
            {
                "id": o.id,
                "user_email": o.user.email if o.user else "N/A",
                "total_amount": float(o.total_amount),
                "payment_method": o.payment_method,
                "payment_status": o.payment_status,
                "status": o.status,
                "created_at": o.created_at.isoformat(),
                "completed_at": o.completed_at.isoformat() if o.completed_at else None,
                "items": [
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "price_each": float(item.price_each)
                    }
                    for item in o.items
                ]
            }
            for o in orders
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo órdenes: {str(e)}")


@router.get("/reports")
async def get_financial_reports(
    period: str = "month",
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Generar reportes financieros
    """
    try:
        # Determinar fechas según el período
        today = datetime.utcnow().date()
        
        if period == "today":
            start_date = today
            end_date = today
        elif period == "week":
            start_date = today - timedelta(days=7)
            end_date = today
        elif period == "month":
            start_date = today.replace(day=1)
            end_date = today
        elif period == "year":
            start_date = today.replace(month=1, day=1)
            end_date = today
        elif period == "custom" and start_date and end_date:
            start_date = datetime.fromisoformat(start_date).date()
            end_date = datetime.fromisoformat(end_date).date()
        else:
            start_date = today.replace(day=1)
            end_date = today
        
        # Consulta de órdenes completadas en el período
        orders_query = db.query(Order).filter(
            Order.payment_status == "completed",
            Order.created_at >= start_date,
            Order.created_at <= end_date + timedelta(days=1)
        )
        
        # Estadísticas básicas
        total_revenue = db.query(func.sum(Order.total_amount)).filter(
            Order.payment_status == "completed",
            Order.created_at >= start_date,
            Order.created_at <= end_date + timedelta(days=1)
        ).scalar() or 0
        
        total_orders = orders_query.count()
        
        # Ingresos por día
        daily_revenue = db.query(
            func.date(Order.created_at).label('date'),
            func.sum(Order.total_amount).label('revenue')
        ).filter(
            Order.payment_status == "completed",
            Order.created_at >= start_date,
            Order.created_at <= end_date + timedelta(days=1)
        ).group_by(func.date(Order.created_at)).all()
        
        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_revenue": float(total_revenue),
            "total_orders": total_orders,
            "daily_revenue": [
                {
                    "date": d.date.isoformat(),
                    "revenue": float(d.revenue)
                }
                for d in daily_revenue
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reporte: {str(e)}")