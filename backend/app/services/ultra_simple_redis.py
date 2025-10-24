"""
Servicio de Redis Cache ultra-simplificado sin conflictos
"""
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

class UltraSimpleRedisCache:
    """Servicio de cache ultra-simplificado usando solo FakeRedis"""
    
    def __init__(self):
        self.redis = None
        self.connected = False
        
        # Configuración de TTL
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
        """Conecta usando solo FakeRedis"""
        try:
            import fakeredis
            # Crear instancia de FakeRedis
            self.redis = fakeredis.FakeAsyncRedis(decode_responses=True)
            await self.redis.ping()
            self.connected = True
            print("✅ FakeRedis conectado exitosamente")
            return True
        except Exception as e:
            print(f"⚠️ Error conectando FakeRedis: {e}")
            self.connected = False
            return False
    
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
    
    # Métodos específicos para el chat
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
    
    async def cache_response(self, query: str, response_data: Dict) -> bool:
        """Cache de respuestas frecuentes"""
        query_hash = hashlib.md5(query.lower().encode()).hexdigest()
        key = self._generate_cache_key("response", query_hash)
        ttl = self.ttl_config["response_cache"]
        return await self.set(key, response_data, ttl)
    
    async def get_cached_response(self, query: str) -> Optional[Dict]:
        """Obtiene respuesta desde cache"""
        query_hash = hashlib.md5(query.lower().encode()).hexdigest()
        key = self._generate_cache_key("response", query_hash)
        return await self.get(key)
    
    async def cache_rate_limit(self, user_id: str, rate_data: Dict) -> bool:
        """Cache de rate limiting"""
        key = self._generate_cache_key("rate_limit", user_id)
        ttl = self.ttl_config["rate_limit"]
        return await self.set(key, rate_data, ttl)
    
    async def get_cached_rate_limit(self, user_id: str) -> Optional[Dict]:
        """Obtiene datos de rate limiting desde cache"""
        key = self._generate_cache_key("rate_limit", user_id)
        return await self.get(key)
    
    async def cache_conversation_history(self, chat_id: int, history: List[Dict]) -> bool:
        """Cache del historial de conversación"""
        key = self._generate_cache_key("conversation", str(chat_id))
        ttl = self.ttl_config["conversation_history"]
        return await self.set(key, history, ttl)
    
    async def get_cached_conversation_history(self, chat_id: int) -> Optional[List[Dict]]:
        """Obtiene historial de conversación desde cache"""
        key = self._generate_cache_key("conversation", str(chat_id))
        return await self.get(key)
    
    async def cache_product_recommendations(self, user_id: str, recommendations: List[Dict]) -> bool:
        """Cache de recomendaciones de productos"""
        key = self._generate_cache_key("recommendations", user_id)
        ttl = self.ttl_config["product_recommendations"]
        return await self.set(key, recommendations, ttl)
    
    async def get_cached_product_recommendations(self, user_id: str) -> Optional[List[Dict]]:
        """Obtiene recomendaciones de productos desde cache"""
        key = self._generate_cache_key("recommendations", user_id)
        return await self.get(key)
    
    async def cache_spam_detection(self, message: str, is_spam: bool) -> bool:
        """Cache de detección de spam"""
        message_hash = hashlib.md5(message.encode()).hexdigest()
        key = self._generate_cache_key("spam", message_hash)
        ttl = self.ttl_config["spam_detection"]
        return await self.set(key, {"is_spam": is_spam, "timestamp": datetime.now().isoformat()}, ttl)
    
    async def get_cached_spam_detection(self, message: str) -> Optional[Dict]:
        """Obtiene resultado de detección de spam desde cache"""
        message_hash = hashlib.md5(message.encode()).hexdigest()
        key = self._generate_cache_key("spam", message_hash)
        return await self.get(key)
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache"""
        if not self.connected or not self.redis:
            return {"status": "disconnected"}
        
        try:
            # Obtener información básica del cache
            keys = await self.redis.keys("*")
            return {
                "status": "connected",
                "cache_type": "fakeredis",
                "total_keys": len(keys),
                "keys_sample": keys[:10] if keys else []
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def warm_up_cache(self, db_session) -> bool:
        """Pre-carga datos importantes en el cache"""
        try:
            from ..models import Product
            
            # Cache de productos
            products = db_session.query(Product).filter(Product.active == True).all()
            products_data = [
                {
                    "id": p.id,
                    "title": p.title,
                    "price": float(p.price),
                    "description": p.description,
                    "image_url": p.image_url
                }
                for p in products
            ]
            
            await self.cache_product_context(products_data)
            print(f"✅ Cache pre-cargado con {len(products_data)} productos")
            return True
            
        except Exception as e:
            print(f"Error pre-cargando cache: {e}")
            return False

# Instancia global del servicio de cache
redis_cache = UltraSimpleRedisCache()
















