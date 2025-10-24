"""
Servicio de contabilidad ultra simplificado
Solo funciones básicas
"""
from sqlmodel import Session, select, func
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy import text

from app.models_sqlmodel.product import Product
from app.models_sqlmodel.user import User


class AccountingService:
    """Servicio básico para contabilidad"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas básicas"""
        try:
            # Total de productos
            total_products = self.db.exec(
                select(func.count(Product.id))
            ).first() or 0
            
            # Total de clientes
            total_customers = self.db.exec(
                select(func.count(User.id)).where(User.is_admin == False)
            ).first() or 0
            
            return {
                "total_sales_today": 0,
                "total_orders_today": 0,
                "total_inventory_value": 0,
                "low_stock_products": 0,
                "out_of_stock_products": 0,
                "total_customers": total_customers,
                "total_products": total_products,
                "top_selling_products": [],
                "recent_transactions": []
            }
            
        except Exception as e:
            print(f"Error: {e}")
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
        """Ajustar stock"""
        try:
            # Usar UPSERT para PostgreSQL
            query = text("""
                INSERT INTO stock_levels (product_id, current_stock, min_stock_level, max_stock_level, last_updated)
                VALUES (:product_id, :new_quantity, 10, 100, CURRENT_TIMESTAMP)
                ON CONFLICT (product_id) 
                DO UPDATE SET 
                    current_stock = :new_quantity,
                    last_updated = CURRENT_TIMESTAMP
            """)
            
            self.db.exec(query, {
                "product_id": product_id,
                "new_quantity": new_quantity
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
