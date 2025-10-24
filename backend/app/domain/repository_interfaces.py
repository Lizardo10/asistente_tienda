"""
Interfaces de Repositorios - Capa de Domain
Abstracciones para acceso a datos (Dependency Inversion Principle)
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities import ProductEntity, UserEntity, OrderEntity, StockLevelEntity


class IProductRepository(ABC):
    """Interface para repositorio de productos (SOLID: Dependency Inversion)"""
    
    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[ProductEntity]:
        """Obtener producto por ID"""
        pass
    
    @abstractmethod
    def get_all(self, active_only: bool = True) -> List[ProductEntity]:
        """Obtener todos los productos"""
        pass
    
    @abstractmethod
    def create(self, product: ProductEntity) -> ProductEntity:
        """Crear nuevo producto"""
        pass
    
    @abstractmethod
    def update(self, product: ProductEntity) -> ProductEntity:
        """Actualizar producto"""
        pass
    
    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """Eliminar producto"""
        pass
    
    @abstractmethod
    def search_by_description(self, query: str) -> List[ProductEntity]:
        """Buscar productos por descripción"""
        pass


class IUserRepository(ABC):
    """Interface para repositorio de usuarios"""
    
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        """Obtener usuario por ID"""
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[UserEntity]:
        """Obtener usuario por email"""
        pass
    
    @abstractmethod
    def create(self, user: UserEntity) -> UserEntity:
        """Crear nuevo usuario"""
        pass
    
    @abstractmethod
    def update(self, user: UserEntity) -> UserEntity:
        """Actualizar usuario"""
        pass
    
    @abstractmethod
    def get_all_customers(self) -> List[UserEntity]:
        """Obtener todos los clientes (no admins)"""
        pass


class IOrderRepository(ABC):
    """Interface para repositorio de órdenes"""
    
    @abstractmethod
    def get_by_id(self, order_id: int) -> Optional[OrderEntity]:
        """Obtener orden por ID"""
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: int) -> List[OrderEntity]:
        """Obtener órdenes de un usuario"""
        pass
    
    @abstractmethod
    def create(self, order: OrderEntity) -> OrderEntity:
        """Crear nueva orden"""
        pass
    
    @abstractmethod
    def update(self, order: OrderEntity) -> OrderEntity:
        """Actualizar orden"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[OrderEntity]:
        """Obtener todas las órdenes"""
        pass


class IStockRepository(ABC):
    """Interface para repositorio de stock"""
    
    @abstractmethod
    def get_by_product_id(self, product_id: int) -> Optional[StockLevelEntity]:
        """Obtener nivel de stock por producto"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[StockLevelEntity]:
        """Obtener todos los niveles de stock"""
        pass
    
    @abstractmethod
    def update_stock(self, stock: StockLevelEntity) -> StockLevelEntity:
        """Actualizar nivel de stock"""
        pass
    
    @abstractmethod
    def get_low_stock_products(self) -> List[StockLevelEntity]:
        """Obtener productos con stock bajo"""
        pass
    
    @abstractmethod
    def adjust_stock(self, product_id: int, quantity: int, reason: str) -> bool:
        """Ajustar stock de un producto"""
        pass


class ICacheRepository(ABC):
    """Interface para repositorio de cache"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Obtener valor del cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: str, expire: int = 3600) -> bool:
        """Guardar valor en cache"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Eliminar valor del cache"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Verificar si existe una key"""
        pass



