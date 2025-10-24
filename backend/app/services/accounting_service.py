"""
Servicio de contabilidad e inventario
Maneja transacciones, stock, reportes financieros
"""
from sqlmodel import Session, select, func
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from app.models_sqlmodel.accounting import (
    InventoryTransaction, StockLevel, FinancialReport, ProductCost,
    TransactionType, InventoryTransactionCreate, StockAdjustmentRequest
)
from app.models_sqlmodel.product import Product
from app.models_sqlmodel.order import Order, OrderItem
from app.models_sqlmodel.user import User


class AccountingService:
    """Servicio para gestión contable e inventario"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== INVENTARIO ====================
    
    def get_stock_levels(self) -> List[Dict[str, Any]]:
        """Obtener niveles de stock de todos los productos"""
        query = select(
            StockLevel,
            Product.name,
            Product.price
        ).join(Product).order_by(StockLevel.current_stock.asc())
        
        results = self.db.exec(query).all()
        
        return [
            {
                "id": stock.id,
                "product_id": stock.product_id,
                "product_name": product_name,
                "product_price": float(product_price),
                "current_stock": stock.current_stock,
                "min_stock_level": stock.min_stock_level,
                "max_stock_level": stock.max_stock_level,
                "last_updated": stock.last_updated,
                "status": self._get_stock_status(stock.current_stock, stock.min_stock_level)
            }
            for stock, product_name, product_price in results
        ]
    
    def get_low_stock_products(self) -> List[Dict[str, Any]]:
        """Obtener productos con stock bajo"""
        query = select(
            StockLevel,
            Product.name,
            Product.price
        ).join(Product).where(
            StockLevel.current_stock <= StockLevel.min_stock_level
        ).order_by(StockLevel.current_stock.asc())
        
        results = self.db.exec(query).all()
        
        return [
            {
                "product_id": stock.product_id,
                "product_name": product_name,
                "current_stock": stock.current_stock,
                "min_stock_level": stock.min_stock_level,
                "product_price": float(product_price)
            }
            for stock, product_name, product_price in results
        ]
    
    def adjust_stock(self, product_id: int, new_quantity: int, reason: str, admin_user_id: int) -> bool:
        """Ajustar stock de un producto"""
        try:
            # Obtener producto
            product = self.db.get(Product, product_id)
            if not product:
                return False
            
            # Obtener o crear nivel de stock
            stock_level = self.db.exec(
                select(StockLevel).where(StockLevel.product_id == product_id)
            ).first()
            
            if not stock_level:
                stock_level = StockLevel(
                    product_id=product_id,
                    current_stock=0,
                    min_stock_level=10,
                    max_stock_level=100
                )
                self.db.add(stock_level)
                self.db.flush()
            
            # Calcular diferencia
            old_quantity = stock_level.current_stock
            quantity_change = new_quantity - old_quantity
            
            # Actualizar stock
            stock_level.current_stock = new_quantity
            stock_level.last_updated = datetime.utcnow()
            
            # Crear transacción de inventario
            transaction = InventoryTransaction(
                product_id=product_id,
                transaction_type=TransactionType.ADJUSTMENT,
                quantity=quantity_change,
                unit_cost=product.price,  # Usar precio de venta como referencia
                total_cost=abs(quantity_change * product.price),
                notes=f"Ajuste manual: {reason}. Stock anterior: {old_quantity}",
                admin_user_id=admin_user_id
            )
            
            self.db.add(transaction)
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Error ajustando stock: {e}")
            return False
    
    def add_inventory_transaction(self, transaction_data: InventoryTransactionCreate, admin_user_id: int) -> bool:
        """Agregar transacción de inventario"""
        try:
            # Crear transacción
            transaction = InventoryTransaction(
                **transaction_data.dict(),
                admin_user_id=admin_user_id,
                total_cost=abs(transaction_data.quantity * transaction_data.unit_cost)
            )
            
            self.db.add(transaction)
            
            # Actualizar stock
            stock_level = self.db.exec(
                select(StockLevel).where(StockLevel.product_id == transaction_data.product_id)
            ).first()
            
            if not stock_level:
                stock_level = StockLevel(
                    product_id=transaction_data.product_id,
                    current_stock=0,
                    min_stock_level=10,
                    max_stock_level=100
                )
                self.db.add(stock_level)
            
            # Actualizar cantidad de stock
            stock_level.current_stock += transaction_data.quantity
            stock_level.last_updated = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Error creando transacción: {e}")
            return False
    
    # ==================== REPORTES FINANCIEROS ====================
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas para el dashboard contable"""
        today = datetime.utcnow().date()
        
        # Ventas del día (calculando desde OrderItems)
        today_orders = self.db.exec(
            select(func.sum(OrderItem.price * OrderItem.quantity))
            .join(Order)
            .where(func.date(Order.created_at) == today)
        ).first() or 0
        
        today_orders_count = self.db.exec(
            select(func.count(Order.id))
            .where(func.date(Order.created_at) == today)
        ).first() or 0
        
        # Valor total del inventario
        inventory_value = self.db.exec(
            select(func.sum(StockLevel.current_stock * Product.price))
            .join(Product)
        ).first() or 0
        
        # Productos con stock bajo
        low_stock_count = self.db.exec(
            select(func.count(StockLevel.id))
            .where(StockLevel.current_stock <= StockLevel.min_stock_level)
        ).first() or 0
        
        # Productos sin stock
        out_of_stock_count = self.db.exec(
            select(func.count(StockLevel.id))
            .where(StockLevel.current_stock == 0)
        ).first() or 0
        
        # Total de clientes
        total_customers = self.db.exec(
            select(func.count(User.id))
            .where(User.is_admin == False)
        ).first() or 0
        
        # Productos más vendidos
        top_products = self.db.exec(
            select(
                Product.name,
                func.sum(OrderItem.quantity).label('total_sold'),
                func.sum(OrderItem.quantity * OrderItem.price).label('total_revenue')
            )
            .join(OrderItem)
            .join(Order)
            .where(func.date(Order.created_at) >= today - timedelta(days=30))
            .group_by(Product.id, Product.name)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(5)
        ).all()
        
        # Transacciones recientes
        recent_transactions = self.db.exec(
            select(
                InventoryTransaction,
                Product.name,
                User.email
            )
            .join(Product)
            .join(User)
            .order_by(InventoryTransaction.created_at.desc())
            .limit(10)
        ).all()
        
        return {
            "total_sales_today": float(today_orders),
            "total_orders_today": today_orders_count,
            "total_inventory_value": float(inventory_value),
            "low_stock_products": low_stock_count,
            "out_of_stock_products": out_of_stock_count,
            "total_customers": total_customers,
            "top_selling_products": [
                {
                    "name": name,
                    "total_sold": total_sold,
                    "total_revenue": float(total_revenue)
                }
                for name, total_sold, total_revenue in top_products
            ],
            "recent_transactions": [
                {
                    "id": trans.id,
                    "product_name": product_name,
                    "transaction_type": trans.transaction_type,
                    "quantity": trans.quantity,
                    "total_cost": float(trans.total_cost),
                    "admin_email": admin_email,
                    "created_at": trans.created_at
                }
                for trans, product_name, admin_email in recent_transactions
            ]
        }
    
    def generate_financial_report(self, report_type: str, period_start: datetime, period_end: datetime, admin_user_id: int) -> bool:
        """Generar reporte financiero"""
        try:
             # Calcular métricas (usando OrderItems)
             total_sales = self.db.exec(
                 select(func.sum(OrderItem.price * OrderItem.quantity))
                 .join(Order)
                 .where(Order.created_at >= period_start, Order.created_at <= period_end)
             ).first() or 0
            
            total_orders = self.db.exec(
                select(func.count(Order.id))
                .where(Order.created_at >= period_start, Order.created_at <= period_end)
            ).first() or 0
            
            total_products_sold = self.db.exec(
                select(func.sum(OrderItem.quantity))
                .join(Order)
                .where(Order.created_at >= period_start, Order.created_at <= period_end)
            ).first() or 0
            
            average_order_value = total_sales / total_orders if total_orders > 0 else 0
            
            # Valor del inventario
            inventory_value = self.db.exec(
                select(func.sum(StockLevel.current_stock * Product.price))
                .join(Product)
            ).first() or 0
            
            # Productos con stock bajo
            low_stock = self.db.exec(
                select(func.count(StockLevel.id))
                .where(StockLevel.current_stock <= StockLevel.min_stock_level)
            ).first() or 0
            
            # Productos sin stock
            out_of_stock = self.db.exec(
                select(func.count(StockLevel.id))
                .where(StockLevel.current_stock == 0)
            ).first() or 0
            
            # Clientes
            total_customers = self.db.exec(
                select(func.count(User.id))
                .where(User.is_admin == False)
            ).first() or 0
            
            new_customers = self.db.exec(
                select(func.count(User.id))
                .where(User.created_at >= period_start, User.created_at <= period_end, User.is_admin == False)
            ).first() or 0
            
            # Crear reporte
            report = FinancialReport(
                report_type=report_type,
                period_start=period_start,
                period_end=period_end,
                total_sales=total_sales,
                total_orders=total_orders,
                total_products_sold=total_products_sold,
                average_order_value=average_order_value,
                total_inventory_value=inventory_value,
                low_stock_products=low_stock,
                out_of_stock_products=out_of_stock,
                total_customers=total_customers,
                new_customers=new_customers,
                created_by=admin_user_id
            )
            
            self.db.add(report)
            self.db.commit()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Error generando reporte: {e}")
            return False
    
    # ==================== UTILIDADES ====================
    
    def _get_stock_status(self, current_stock: int, min_stock: int) -> str:
        """Determinar estado del stock"""
        if current_stock == 0:
            return "out_of_stock"
        elif current_stock <= min_stock:
            return "low_stock"
        else:
            return "in_stock"
    
    def initialize_product_stock(self, product_id: int, initial_stock: int = 0) -> bool:
        """Inicializar stock para un producto nuevo"""
        try:
            existing_stock = self.db.exec(
                select(StockLevel).where(StockLevel.product_id == product_id)
            ).first()
            
            if not existing_stock:
                stock_level = StockLevel(
                    product_id=product_id,
                    current_stock=initial_stock,
                    min_stock_level=10,
                    max_stock_level=100
                )
                self.db.add(stock_level)
                self.db.commit()
                return True
            
            return False
            
        except Exception as e:
            self.db.rollback()
            print(f"Error inicializando stock: {e}")
            return False
