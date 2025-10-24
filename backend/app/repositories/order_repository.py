"""
Repositorio de órdenes siguiendo el patrón Repository
Siguiendo el principio de Single Responsibility (SOLID)
"""
from typing import Optional, List
from sqlmodel import Session, select
from .base_repository import BaseRepository
from app.models_sqlmodel.order import Order, OrderItem


class OrderRepository(BaseRepository[Order]):
    """Repositorio para órdenes"""
    
    def __init__(self, session: Session):
        super().__init__(session, Order)
    
    async def get_by_user_id(self, user_id: int) -> List[Order]:
        """Obtiene órdenes por usuario"""
        statement = select(Order).where(Order.user_id == user_id)
        return self.session.exec(statement).all()
    
    async def get_by_status(self, status: str) -> List[Order]:
        """Obtiene órdenes por estado"""
        statement = select(Order).where(Order.status == status)
        return self.session.exec(statement).all()
    
    async def get_items_by_order_id(self, order_id: int) -> List[OrderItem]:
        """Obtiene items de una orden"""
        statement = select(OrderItem).where(OrderItem.order_id == order_id)
        return self.session.exec(statement).all()
    
    async def create_item(self, item_data: dict) -> OrderItem:
        """Crea un item de orden"""
        item = OrderItem(**item_data)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item
    
    async def get_recent_orders(self, limit: int = 10) -> List[Order]:
        """Obtiene órdenes recientes"""
        statement = (
            select(Order)
            .order_by(Order.created_at.desc())
            .limit(limit)
        )
        return self.session.exec(statement).all()
