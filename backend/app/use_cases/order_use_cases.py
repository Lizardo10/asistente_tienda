"""
Casos de uso para órdenes siguiendo Clean Architecture
Siguiendo el principio de Single Responsibility (SOLID)
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.models_sqlmodel.order import Order, OrderCreate, OrderItem, OrderItemCreate
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository


class OrderUseCases:
    """Casos de uso para órdenes"""
    
    def __init__(self, order_repository: OrderRepository, product_repository: ProductRepository):
        self.order_repository = order_repository
        self.product_repository = product_repository
    
    async def create_order(self, user_id: int, order_data: OrderCreate) -> Order:
        """Crea una nueva orden"""
        # Validar que todos los productos existen y están activos
        for item in order_data.items:
            product = await self.product_repository.get(item.product_id)
            if not product or not product.active:
                raise ValueError(f"Producto {item.product_id} no disponible")
        
        # Crear la orden
        order_dict = {
            "user_id": user_id,
            "status": "pending"
        }
        order = await self.order_repository.create(order_dict)
        
        # Crear los items de la orden
        total_amount = 0
        for item_data in order_data.items:
            product = await self.product_repository.get(item_data.product_id)
            item_dict = {
                "order_id": order.id,
                "product_id": item_data.product_id,
                "quantity": item_data.quantity,
                "price_each": product.price
            }
            await self.order_repository.create_item(item_dict)
            total_amount += product.price * item_data.quantity
        
        return order
    
    async def get_order(self, order_id: int) -> Optional[Order]:
        """Obtiene una orden por ID"""
        return await self.order_repository.get(order_id)
    
    async def get_user_orders(self, user_id: int) -> List[Order]:
        """Obtiene órdenes de un usuario"""
        return await self.order_repository.get_by_user_id(user_id)
    
    async def get_all_orders(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """Obtiene todas las órdenes (admin)"""
        return await self.order_repository.get_multi(skip, limit)
    
    async def update_order_status(self, order_id: int, status: str) -> Optional[Order]:
        """Actualiza el estado de una orden"""
        valid_statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
        if status not in valid_statuses:
            raise ValueError(f"Estado inválido. Estados válidos: {valid_statuses}")
        
        return await self.order_repository.update(order_id, {"status": status})
    
    async def cancel_order(self, order_id: int) -> Optional[Order]:
        """Cancela una orden"""
        order = await self.order_repository.get(order_id)
        if order and order.status in ["pending", "confirmed"]:
            return await self.update_order_status(order_id, "cancelled")
        return None
    
    async def get_orders_by_status(self, status: str) -> List[Order]:
        """Obtiene órdenes por estado"""
        return await self.order_repository.get_by_status(status)
    
    async def get_order_items(self, order_id: int) -> List[OrderItem]:
        """Obtiene items de una orden"""
        return await self.order_repository.get_items_by_order_id(order_id)
    
    async def calculate_order_total(self, order_id: int) -> float:
        """Calcula el total de una orden"""
        items = await self.get_order_items(order_id)
        return sum(item.price_each * item.quantity for item in items)
    
    async def get_orders_analytics(self) -> Dict[str, Any]:
        """Obtiene analytics de órdenes"""
        total_orders = await self.order_repository.count()
        pending_orders = len(await self.order_repository.get_by_status("pending"))
        confirmed_orders = len(await self.order_repository.get_by_status("confirmed"))
        shipped_orders = len(await self.order_repository.get_by_status("shipped"))
        delivered_orders = len(await self.order_repository.get_by_status("delivered"))
        cancelled_orders = len(await self.order_repository.get_by_status("cancelled"))
        
        return {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "confirmed_orders": confirmed_orders,
            "shipped_orders": shipped_orders,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders,
            "completion_rate": (delivered_orders / total_orders * 100) if total_orders > 0 else 0,
            "cancellation_rate": (cancelled_orders / total_orders * 100) if total_orders > 0 else 0
        }
