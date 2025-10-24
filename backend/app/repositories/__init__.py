"""
Repositorios de la aplicación siguiendo el patrón Repository
Siguiendo el principio de Dependency Inversion (SOLID)
"""
from .user_repository import UserRepository
from .product_repository import ProductRepository
from .order_repository import OrderRepository
from .chat_repository import ChatRepository

__all__ = [
    "UserRepository",
    "ProductRepository", 
    "OrderRepository",
    "ChatRepository"
]
