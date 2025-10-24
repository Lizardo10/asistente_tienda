"""
Router básico para contabilidad
Solo funciones esenciales
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Dict, Any
from sqlalchemy import text

from app.database import get_db
from app.routers.auth import get_current_user
from app.models_sqlmodel.user import User

router = APIRouter(prefix="/admin/accounting", tags=["Accounting"])


def verify_admin(user: User = Depends(get_current_user)):
    """Verificar que el usuario sea administrador"""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden acceder a esta área"
        )
    return user


@router.get("/dashboard")
async def get_dashboard_stats(
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Dashboard básico de contabilidad"""
    try:
        # Estadísticas básicas usando SQL directo
        products_result = db.execute(text("SELECT COUNT(*) as count FROM products"))
        products_count = products_result.scalar()
        
        users_result = db.execute(text("SELECT COUNT(*) as count FROM users WHERE is_admin = false"))
        users_count = users_result.scalar()
        
        orders_result = db.execute(text("SELECT COUNT(*) as count FROM orders"))
        orders_count = orders_result.scalar()
        
        return {
            "total_sales_today": 0,
            "total_orders_today": orders_count,
            "total_inventory_value": 0,
            "low_stock_products": 0,
            "out_of_stock_products": 0,
            "total_customers": users_count,
            "total_products": products_count,
            "top_selling_products": [],
            "recent_transactions": []
        }
        
    except Exception as e:
        print(f"Error en dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/inventory/stock-levels")
async def get_stock_levels(
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Obtener niveles de stock"""
    try:
        query = text("""
            SELECT 
                sl.id,
                sl.product_id,
                p.title as product_name,
                p.price as product_price,
                sl.current_stock,
                sl.min_stock_level,
                sl.max_stock_level,
                sl.last_updated
            FROM stock_levels sl
            JOIN products p ON sl.product_id = p.id
            ORDER BY sl.current_stock ASC
        """)
        
        result = db.execute(query)
        
        return [
            {
                "id": row.id,
                "product_id": row.product_id,
                "product_name": row.product_name,
                "product_price": float(row.product_price),
                "current_stock": row.current_stock,
                "min_stock_level": row.min_stock_level,
                "max_stock_level": row.max_stock_level,
                "last_updated": row.last_updated,
                "status": "in_stock" if row.current_stock > row.min_stock_level else "low_stock" if row.current_stock > 0 else "out_of_stock"
            }
            for row in result
        ]
        
    except Exception as e:
        print(f"Error obteniendo stock: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/inventory/adjust-stock")
async def adjust_stock(
    adjustment: Dict[str, Any],
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Ajustar stock de un producto"""
    try:
        product_id = adjustment["product_id"]
        new_quantity = adjustment["new_quantity"]
        reason = adjustment["reason"]
        
        # Usar UPSERT para PostgreSQL
        query = text("""
            INSERT INTO stock_levels (product_id, current_stock, min_stock_level, max_stock_level, last_updated)
            VALUES (:product_id, :new_quantity, 10, 100, CURRENT_TIMESTAMP)
            ON CONFLICT (product_id) 
            DO UPDATE SET 
                current_stock = :new_quantity,
                last_updated = CURRENT_TIMESTAMP
        """)
        
        db.execute(query, {
            "product_id": product_id,
            "new_quantity": new_quantity
        })
        
        db.commit()
        
        return {"message": "Stock ajustado correctamente"}
        
    except Exception as e:
        print(f"Error ajustando stock: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
