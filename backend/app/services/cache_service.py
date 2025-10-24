"""
Servicio de cache modernizado con Redis Stack
Siguiendo el principio de Single Responsibility (SOLID)
"""
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import hashlib
import aioredis
from aioredis import Redis
import os
from abc import ABC, abstractmethod

# Intentar importar FakeRedis como alternativa
try:
    import fakeredis
    FAKEREDIS_AVAILABLE = True
except ImportError:
    FAKEREDIS_AVAILABLE = False


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


class RedisCacheService(CacheInterface):
    """Implementación de cache con Redis Stack"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[Redis] = None
        self.connected = False
        
        # Configuración de TTL para diferentes tipos de cache
        self.ttl_config = {
            "product_context": 300,      # 5 minutos
            "user_session": 1800,        # 30 minutos
            "intent_analysis": 600,      # 10 minutos
            "response_cache": 900,        # 15 minutos
            "rate_limit": 60,             # 1 minuto
            "spam_detection": 300,        # 5 minutos
            "conversation_history": 1800, # 30 minutos
            "product_recommendations": 600 # 10 minutos
        }
    
    async def connect(self) -> bool:
        """Conecta a Redis o usa FakeRedis como alternativa"""
        try:
            # Intentar conectar con Redis real
            self.redis = aioredis.from_url(
                self.redis_url, 
                decode_responses=True
            )
            await self.redis.ping()
            self.connected = True
            print("✅ Redis real conectado exitosamente")
            return True
        except Exception as e:
            print(f"⚠️ Redis real no disponible: {e}")
            
            # Intentar usar FakeRedis como alternativa
            if FAKEREDIS_AVAILABLE:
                try:
                    fake_redis = fakeredis.FakeAsyncRedis(decode_responses=True)
                    await fake_redis.ping()
                    self.redis = fake_redis
                    self.connected = True
                    print("✅ FakeRedis conectado exitosamente (modo simulado)")
                    return True
                except Exception as fake_e:
                    print(f"⚠️ FakeRedis también falló: {fake_e}")
            
            print("💡 El sistema funcionará sin cache Redis (modo degradado)")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Desconecta de Redis"""
        if self.redis:
            await self.redis.close()
            self.connected = False
    
    def _generate_cache_key(self, prefix: str, identifier: str, *args) -> str:
        """Genera una clave de cache única"""
        key_parts = [prefix, identifier]
        if args:
            key_parts.extend(str(arg) for arg in args)
        
        key_string = ":".join(key_parts)
        if len(key_string) > 200:
            key_string = f"{prefix}:{hashlib.md5(key_string.encode()).hexdigest()}"
        
        return key_string
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del cache"""
        if not self.connected or not self.redis:
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Error obteniendo cache {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Establece un valor en el cache"""
        if not self.connected or not self.redis:
            return False
        
        try:
            serialized_value = json.dumps(value, default=str)
            if ttl:
                await self.redis.setex(key, ttl, serialized_value)
            else:
                await self.redis.set(key, serialized_value)
            return True
        except Exception as e:
            print(f"Error estableciendo cache {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Elimina una clave del cache"""
        if not self.connected or not self.redis:
            return False
        
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Error eliminando cache {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Verifica si una clave existe en el cache"""
        if not self.connected or not self.redis:
            return False
        
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            print(f"Error verificando existencia de cache {key}: {e}")
            return False
    
    # Métodos específicos para el chat optimizado
    async def cache_product_context(self, products_data: List[Dict], ttl: Optional[int] = None) -> bool:
        """Cache del contexto de productos"""
        key = self._generate_cache_key("products", "context")
        ttl = ttl or self.ttl_config["product_context"]
        return await self.set(key, products_data, ttl)
    
    async def get_cached_product_context(self) -> Optional[List[Dict]]:
        """Obtiene el contexto de productos desde cache"""
        key = self._generate_cache_key("products", "context")
        return await self.get(key)
    
    async def cache_user_session(self, user_id: str, session_data: Dict) -> bool:
        """Cache de sesión de usuario"""
        key = self._generate_cache_key("session", user_id)
        ttl = self.ttl_config["user_session"]
        return await self.set(key, session_data, ttl)
    
    async def get_cached_user_session(self, user_id: str) -> Optional[Dict]:
        """Obtiene la sesión de usuario desde cache"""
        key = self._generate_cache_key("session", user_id)
        return await self.get(key)
    
    async def cache_intent_analysis(self, message: str, intent_data: Dict) -> bool:
        """Cache del análisis de intención"""
        message_hash = hashlib.md5(message.lower().encode()).hexdigest()
        key = self._generate_cache_key("intent", message_hash)
        ttl = self.ttl_config["intent_analysis"]
        return await self.set(key, intent_data, ttl)
    
    async def get_cached_intent_analysis(self, message: str) -> Optional[Dict]:
        """Obtiene el análisis de intención desde cache"""
        message_hash = hashlib.md5(message.lower().encode()).hexdigest()
        key = self._generate_cache_key("intent", message_hash)
        return await self.get(key)
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache"""
        if not self.connected or not self.redis:
            return {"status": "disconnected"}
        
        try:
            info = await self.redis.info()
            return {
                "status": "connected",
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """Calcula la tasa de aciertos del cache"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0


# Instancia global del servicio de cache
cache_service = RedisCacheService()
