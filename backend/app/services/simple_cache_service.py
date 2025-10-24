"""
Servicio de caché simplificado
Implementa el patrón Repository y principios SOLID
"""
import json
from typing import Any, Optional, Dict
from abc import ABC, abstractmethod


class CacheInterface(ABC):
    """Interface para el servicio de cache - Dependency Inversion Principle"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        pass


class SimpleCacheService(CacheInterface):
    """Implementación simple de cache en memoria"""
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.connected = True
    
    async def connect(self) -> bool:
        """Simula conexión al cache"""
        self.connected = True
        return True
    
    async def disconnect(self):
        """Simula desconexión del cache"""
        self.connected = False
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del cache"""
        return self.cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Establece un valor en el cache"""
        self.cache[key] = value
        return True
    
    async def delete(self, key: str) -> bool:
        """Elimina una clave del cache"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    async def exists(self, key: str) -> bool:
        """Verifica si una clave existe en el cache"""
        return key in self.cache


# Instancia global del servicio de cache
cache_service = SimpleCacheService()
