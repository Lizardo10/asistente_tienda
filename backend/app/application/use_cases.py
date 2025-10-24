"""
Casos de Uso - Capa de Application
Lógica de negocio específica de la aplicación
Siguiendo Clean Architecture y SOLID
"""
from typing import List, Optional, Dict, Any
from decimal import Decimal

from app.domain.entities import ProductEntity, OrderEntity, OrderItemEntity, StockLevelEntity
from app.domain.value_objects import Email, Money, Quantity
from app.domain.repository_interfaces import (
    IProductRepository, IOrderRepository, IStockRepository, IUserRepository
)


class CreateProductUseCase:
    """Caso de uso: Crear Producto (Single Responsibility)"""
    
    def __init__(self, product_repository: IProductRepository):
        self.product_repository = product_repository
    
    def execute(self, title: str, description: str, price: Decimal, image_url: str = "") -> ProductEntity:
        """Ejecutar caso de uso"""
        # Crear entidad
        product = ProductEntity(
            id=None,
            title=title,
            description=description,
            price=price,
            image_url=image_url,
            active=True
        )
        
        # Validar entidad
        errors = product.validate()
        if errors:
            raise ValueError(f"Producto inválido: {', '.join(errors)}")
        
        # Guardar en repositorio
        return self.product_repository.create(product)


class GetProductsUseCase:
    """Caso de uso: Obtener Productos"""
    
    def __init__(self, product_repository: IProductRepository):
        self.product_repository = product_repository
    
    def execute(self, active_only: bool = True) -> List[ProductEntity]:
        """Ejecutar caso de uso"""
        return self.product_repository.get_all(active_only=active_only)


class UpdateProductUseCase:
    """Caso de uso: Actualizar Producto"""
    
    def __init__(self, product_repository: IProductRepository):
        self.product_repository = product_repository
    
    def execute(self, product_id: int, **updates) -> ProductEntity:
        """Ejecutar caso de uso"""
        # Obtener producto existente
        product = self.product_repository.get_by_id(product_id)
        
        if not product:
            raise ValueError(f"Producto {product_id} no encontrado")
        
        # Actualizar campos
        for key, value in updates.items():
            if hasattr(product, key):
                setattr(product, key, value)
        
        # Validar
        errors = product.validate()
        if errors:
            raise ValueError(f"Producto inválido: {', '.join(errors)}")
        
        # Guardar
        return self.product_repository.update(product)


class CreateOrderUseCase:
    """Caso de uso: Crear Orden (con validación de stock)"""
    
    def __init__(
        self, 
        order_repository: IOrderRepository,
        product_repository: IProductRepository,
        stock_repository: IStockRepository,
        user_repository: IUserRepository
    ):
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.stock_repository = stock_repository
        self.user_repository = user_repository
    
    def execute(self, user_id: int, items: List[Dict[str, Any]]) -> OrderEntity:
        """Ejecutar caso de uso"""
        # Verificar usuario
        user = self.user_repository.get_by_id(user_id)
        if not user or not user.active:
            raise ValueError("Usuario inválido o inactivo")
        
        # Crear items de la orden
        order_items = []
        total_amount = Decimal(0)
        
        for item_data in items:
            product_id = item_data["product_id"]
            quantity = item_data["quantity"]
            
            # Verificar producto
            product = self.product_repository.get_by_id(product_id)
            if not product or not product.is_available():
                raise ValueError(f"Producto {product_id} no disponible")
            
            # Verificar stock
            stock = self.stock_repository.get_by_product_id(product_id)
            if stock and not stock.can_fulfill_order(quantity):
                raise ValueError(f"Stock insuficiente para producto {product.title}")
            
            # Crear item
            order_item = OrderItemEntity(
                id=None,
                order_id=None,
                product_id=product_id,
                quantity=quantity,
                price=product.price
            )
            
            order_items.append(order_item)
            total_amount += order_item.calculate_subtotal()
        
        # Verificar balance del usuario
        if not user.can_make_purchase(total_amount):
            raise ValueError("Balance insuficiente para realizar la compra")
        
        # Crear orden
        order = OrderEntity(
            id=None,
            user_id=user_id,
            status="pending",
            items=order_items
        )
        
        # Validar orden
        errors = order.validate()
        if errors:
            raise ValueError(f"Orden inválida: {', '.join(errors)}")
        
        # Guardar orden
        created_order = self.order_repository.create(order)
        
        # Actualizar stock
        for item in order_items:
            self.stock_repository.adjust_stock(
                product_id=item.product_id,
                quantity=-item.quantity,
                reason=f"Venta - Orden #{created_order.id}"
            )
        
        return created_order


class AdjustStockUseCase:
    """Caso de uso: Ajustar Stock"""
    
    def __init__(self, stock_repository: IStockRepository):
        self.stock_repository = stock_repository
    
    def execute(self, product_id: int, new_quantity: int, reason: str, admin_user_id: int) -> bool:
        """Ejecutar caso de uso"""
        # Validar cantidad
        if new_quantity < 0:
            raise ValueError("La cantidad no puede ser negativa")
        
        # Ajustar stock
        return self.stock_repository.adjust_stock(
            product_id=product_id,
            quantity=new_quantity,
            reason=reason
        )


class GetDashboardStatsUseCase:
    """Caso de uso: Obtener Estadísticas del Dashboard"""
    
    def __init__(
        self,
        product_repository: IProductRepository,
        order_repository: IOrderRepository,
        stock_repository: IStockRepository,
        user_repository: IUserRepository
    ):
        self.product_repository = product_repository
        self.order_repository = order_repository
        self.stock_repository = stock_repository
        self.user_repository = user_repository
    
    def execute(self) -> Dict[str, Any]:
        """Ejecutar caso de uso"""
        # Obtener todas las métricas
        all_orders = self.order_repository.get_all()
        all_stock = self.stock_repository.get_all()
        all_customers = self.user_repository.get_all_customers()
        low_stock = self.stock_repository.get_low_stock_products()
        
        return {
            "total_orders": len(all_orders),
            "total_customers": len(all_customers),
            "low_stock_products": len(low_stock),
            "out_of_stock_products": len([s for s in all_stock if s.is_out_of_stock()]),
            "total_inventory_value": sum(s.current_stock * Decimal(100) for s in all_stock)  # Simplificado
        }



