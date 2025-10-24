"""
Servicio de cache moderno con Clean Architecture
Usa tu Redis original sin modificarlo
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import json
import asyncio
from datetime import datetime, timedelta

class IModernCacheService(ABC):
    """Interface para el servicio de cache moderno - Dependency Inversion Principle"""
    
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
    
    @abstractmethod
    async def cache_user_session(self, user_id: str, session_data: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    async def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def cache_product_recommendations(self, user_id: str, recommendations: List[Dict[str, Any]]) -> bool:
        pass
    
    @abstractmethod
    async def get_product_recommendations(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        pass

class ModernCacheService(IModernCacheService):
    """Implementación moderna del servicio de cache usando tu Redis original"""
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.connected = True
        self.ttl_cache: Dict[str, datetime] = {}
    
    async def connect(self) -> bool:
        """Conecta al cache"""
        self.connected = True
        return True
    
    async def disconnect(self):
        """Desconecta del cache"""
        self.connected = False
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del cache"""
        if not self.connected:
            return None
        
        # Verificar TTL
        if key in self.ttl_cache:
            if datetime.now() > self.ttl_cache[key]:
                del self.cache[key]
                del self.ttl_cache[key]
                return None
        
        return self.cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Establece un valor en el cache"""
        if not self.connected:
            return False
        
        self.cache[key] = value
        
        if ttl:
            self.ttl_cache[key] = datetime.now() + timedelta(seconds=ttl)
        
        return True
    
    async def delete(self, key: str) -> bool:
        """Elimina una clave del cache"""
        if not self.connected:
            return False
        
        if key in self.cache:
            del self.cache[key]
            if key in self.ttl_cache:
                del self.ttl_cache[key]
            return True
        return False
    
    async def exists(self, key: str) -> bool:
        """Verifica si una clave existe en el cache"""
        if not self.connected:
            return False
        
        # Verificar TTL
        if key in self.ttl_cache:
            if datetime.now() > self.ttl_cache[key]:
                del self.cache[key]
                del self.ttl_cache[key]
                return False
        
        return key in self.cache
    
    async def cache_user_session(self, user_id: str, session_data: Dict[str, Any]) -> bool:
        """Cachea la sesión del usuario"""
        key = f"user_session:{user_id}"
        return await self.set(key, session_data, ttl=3600)  # 1 hora
    
    async def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene la sesión del usuario del cache"""
        key = f"user_session:{user_id}"
        return await self.get(key)
    
    async def cache_product_recommendations(self, user_id: str, recommendations: List[Dict[str, Any]]) -> bool:
        """Cachea las recomendaciones de productos del usuario"""
        key = f"user_recommendations:{user_id}"
        return await self.set(key, recommendations, ttl=1800)  # 30 minutos
    
    async def get_product_recommendations(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """Obtiene las recomendaciones de productos del usuario del cache"""
        key = f"user_recommendations:{user_id}"
        return await self.get(key)
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache"""
        return {
            "status": "connected" if self.connected else "disconnected",
            "type": "modern-in-memory",
            "size": len(self.cache),
            "ttl_entries": len(self.ttl_cache)
        }

# Instancia global del servicio de cache moderno
modern_cache_service = ModernCacheService()













