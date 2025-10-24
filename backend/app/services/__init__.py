"""
Servicios de la aplicación siguiendo Clean Architecture
Siguiendo el principio de Dependency Inversion (SOLID)
"""
from .simple_cache_service import cache_service

__all__ = [
    "cache_service"
]
