"""
Servicio de contabilidad simplificado
Compatible con modelos existentes
"""
from sqlmodel import Session, select, func
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from app.models_sqlmodel.product import Product
from app.models_sqlmodel.order import Order, OrderItem
from app.models_sqlmodel.user import User


class AccountingService:
    """Servicio simplificado para gestión contable"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas básicas para el dashboard"""
        try:
            today = datetime.utcnow().date()
            
            # Órdenes del día
            today_orders_count = self.db.exec(
                select(func.count(Order.id))
                .where(func.date(Order.created_at) == today)
            ).first() or 0
            
            # Ventas del día (suma de precios de OrderItems)
            today_sales = 0
            if today_orders_count > 0:
                today_orders = self.db.exec(
                    select(Order).where(func.date(Order.created_at) == today)
                ).all()
                
                for order in today_orders:
                    order_items = self.db.exec(
                        select(OrderItem).where(OrderItem.order_id == order.id)
                    ).all()
                    
                    for item in order_items:
                        today_sales += float(item.price * item.quantity)
            
            # Total de clientes
            total_customers = self.db.exec(
                select(func.count(User.id)).where(User.is_admin == False)
            ).first() or 0
            
            # Productos totales
            total_products = self.db.exec(
                select(func.count(Product.id))
            ).first() or 0
            
            # Simular datos de stock (por ahora)
            return {
                "total_sales_today": today_sales,
                "total_orders_today": today_orders_count,
                "total_inventory_value": 0,  # Se calculará cuando tengamos stock
                "low_stock_products": 0,
                "out_of_stock_products": 0,
                "total_customers": total_customers,
                "total_products": total_products,
                "top_selling_products": [],
                "recent_transactions": []
            }
            
        except Exception as e:
            print(f"Error en dashboard stats: {e}")
            return {
                "total_sales_today": 0,
                "total_orders_today": 0,
                "total_inventory_value": 0,
                "low_stock_products": 0,
                "out_of_stock_products": 0,
                "total_customers": 0,
                "total_products": 0,
                "top_selling_products": [],
                "recent_transactions": []
            }
    
    def get_stock_levels(self) -> List[Dict[str, Any]]:
        """Obtener niveles de stock (usando tabla stock_levels)"""
        try:
            # Usar SQL directo para evitar problemas de relaciones
            from sqlalchemy import text
            
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
            
            result = self.db.exec(query)
            
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
                    "status": self._get_stock_status(row.current_stock, row.min_stock_level)
                }
                for row in result
            ]
            
        except Exception as e:
            print(f"Error obteniendo stock: {e}")
            return []
    
    def adjust_stock(self, product_id: int, new_quantity: int, reason: str, admin_user_id: int) -> bool:
        """Ajustar stock usando SQL directo"""
        try:
            from sqlalchemy import text
            
            # Actualizar stock
            update_query = text("""
                INSERT INTO stock_levels (product_id, current_stock, min_stock_level, max_stock_level, last_updated)
                VALUES (:product_id, :new_quantity, 10, 100, CURRENT_TIMESTAMP)
                ON CONFLICT (product_id) 
                DO UPDATE SET 
                    current_stock = :new_quantity,
                    last_updated = CURRENT_TIMESTAMP
            """)
            
            self.db.exec(update_query, {
                "product_id": product_id,
                "new_quantity": new_quantity
            })
            
            # Registrar transacción
            transaction_query = text("""
                INSERT INTO inventory_transactions 
                (product_id, transaction_type, quantity, unit_cost, total_cost, notes, admin_user_id)
                VALUES (:product_id, 'adjustment', :quantity, 0, 0, :notes, :admin_user_id)
            """)
            
            self.db.exec(transaction_query, {
                "product_id": product_id,
                "quantity": new_quantity,
                "notes": f"Ajuste manual: {reason}",
                "admin_user_id": admin_user_id
            })
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Error ajustando stock: {e}")
            return False
    
    def _get_stock_status(self, current_stock: int, min_stock: int) -> str:
        """Determinar estado del stock"""
        if current_stock == 0:
            return "out_of_stock"
        elif current_stock <= min_stock:
            return "low_stock"
        else:
            return "in_stock"
