"""
Servicio de Cache simplificado (sin Redis por ahora)
"""
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

class SimpleCacheService:
    """Servicio de cache en memoria como alternativa a Redis"""
    
    def __init__(self):
        self.cache: Dict[str, Dict] = {}
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
        self.connected = True  # Siempre conectado en memoria
    
    def _generate_cache_key(self, prefix: str, identifier: str, *args) -> str:
        """Genera una clave de cache única"""
        key_parts = [prefix, identifier]
        if args:
            key_parts.extend(str(arg) for arg in args)
        
        key_string = ":".join(key_parts)
        if len(key_string) > 200:
            key_string = f"{prefix}:{hashlib.md5(key_string.encode()).hexdigest()}"
        
        return key_string
    
    def _is_expired(self, cache_entry: Dict) -> bool:
        """Verifica si una entrada del cache ha expirado"""
        if "expires_at" not in cache_entry:
            return False
        
        return datetime.now() > datetime.fromisoformat(cache_entry["expires_at"])
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del cache"""
        if key not in self.cache:
            return None
        
        cache_entry = self.cache[key]
        if self._is_expired(cache_entry):
            del self.cache[key]
            return None
        
        return cache_entry["value"]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Establece un valor en el cache"""
        expires_at = None
        if ttl:
            expires_at = (datetime.now() + timedelta(seconds=ttl)).isoformat()
        
        self.cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": datetime.now().isoformat()
        }
        return True
    
    def delete(self, key: str) -> bool:
        """Elimina una clave del cache"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def exists(self, key: str) -> bool:
        """Verifica si una clave existe en el cache"""
        if key not in self.cache:
            return False
        
        if self._is_expired(self.cache[key]):
            del self.cache[key]
            return False
        
        return True
    
    # ==================== MÉTODOS ESPECÍFICOS PARA EL CHAT ====================
    
    def cache_product_context(self, products_data: List[Dict], ttl: Optional[int] = None) -> bool:
        """Cache del contexto de productos"""
        key = self._generate_cache_key("products", "context")
        ttl = ttl or self.ttl_config["product_context"]
        return self.set(key, products_data, ttl)
    
    def get_cached_product_context(self) -> Optional[List[Dict]]:
        """Obtiene el contexto de productos desde cache"""
        key = self._generate_cache_key("products", "context")
        return self.get(key)
    
    def cache_user_session(self, user_id: str, session_data: Dict) -> bool:
        """Cache de sesión de usuario"""
        key = self._generate_cache_key("session", user_id)
        ttl = self.ttl_config["user_session"]
        return self.set(key, session_data, ttl)
    
    def get_cached_user_session(self, user_id: str) -> Optional[Dict]:
        """Obtiene la sesión de usuario desde cache"""
        key = self._generate_cache_key("session", user_id)
        return self.get(key)
    
    def cache_intent_analysis(self, message: str, intent_data: Dict) -> bool:
        """Cache del análisis de intención"""
        message_hash = hashlib.md5(message.lower().encode()).hexdigest()
        key = self._generate_cache_key("intent", message_hash)
        ttl = self.ttl_config["intent_analysis"]
        return self.set(key, intent_data, ttl)
    
    def get_cached_intent_analysis(self, message: str) -> Optional[Dict]:
        """Obtiene el análisis de intención desde cache"""
        message_hash = hashlib.md5(message.lower().encode()).hexdigest()
        key = self._generate_cache_key("intent", message_hash)
        return self.get(key)
    
    def cache_response(self, query: str, response_data: Dict) -> bool:
        """Cache de respuestas frecuentes"""
        query_hash = hashlib.md5(query.lower().encode()).hexdigest()
        key = self._generate_cache_key("response", query_hash)
        ttl = self.ttl_config["response_cache"]
        return self.set(key, response_data, ttl)
    
    def get_cached_response(self, query: str) -> Optional[Dict]:
        """Obtiene respuesta desde cache"""
        query_hash = hashlib.md5(query.lower().encode()).hexdigest()
        key = self._generate_cache_key("response", query_hash)
        return self.get(key)
    
    def cache_rate_limit(self, user_id: str, rate_data: Dict) -> bool:
        """Cache de rate limiting"""
        key = self._generate_cache_key("rate_limit", user_id)
        ttl = self.ttl_config["rate_limit"]
        return self.set(key, rate_data, ttl)
    
    def get_cached_rate_limit(self, user_id: str) -> Optional[Dict]:
        """Obtiene datos de rate limiting desde cache"""
        key = self._generate_cache_key("rate_limit", user_id)
        return self.get(key)
    
    def cache_conversation_history(self, chat_id: int, history: List[Dict]) -> bool:
        """Cache del historial de conversación"""
        key = self._generate_cache_key("conversation", str(chat_id))
        ttl = self.ttl_config["conversation_history"]
        return self.set(key, history, ttl)
    
    def get_cached_conversation_history(self, chat_id: int) -> Optional[List[Dict]]:
        """Obtiene historial de conversación desde cache"""
        key = self._generate_cache_key("conversation", str(chat_id))
        return self.get(key)
    
    def cache_product_recommendations(self, user_id: str, recommendations: List[Dict]) -> bool:
        """Cache de recomendaciones de productos"""
        key = self._generate_cache_key("recommendations", user_id)
        ttl = self.ttl_config["product_recommendations"]
        return self.set(key, recommendations, ttl)
    
    def get_cached_product_recommendations(self, user_id: str) -> Optional[List[Dict]]:
        """Obtiene recomendaciones de productos desde cache"""
        key = self._generate_cache_key("recommendations", user_id)
        return self.get(key)
    
    def cache_spam_detection(self, message: str, is_spam: bool) -> bool:
        """Cache de detección de spam"""
        message_hash = hashlib.md5(message.encode()).hexdigest()
        key = self._generate_cache_key("spam", message_hash)
        ttl = self.ttl_config["spam_detection"]
        return self.set(key, {"is_spam": is_spam, "timestamp": datetime.now().isoformat()}, ttl)
    
    def get_cached_spam_detection(self, message: str) -> Optional[Dict]:
        """Obtiene resultado de detección de spam desde cache"""
        message_hash = hashlib.md5(message.encode()).hexdigest()
        key = self._generate_cache_key("spam", message_hash)
        return self.get(key)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache"""
        total_entries = len(self.cache)
        expired_entries = sum(1 for entry in self.cache.values() if self._is_expired(entry))
        
        return {
            "status": "connected",
            "cache_type": "in_memory",
            "total_entries": total_entries,
            "expired_entries": expired_entries,
            "active_entries": total_entries - expired_entries,
            "memory_usage": f"{len(str(self.cache))} characters"
        }
    
    def warm_up_cache(self, db_session) -> bool:
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
            
            self.cache_product_context(products_data)
            print(f"✅ Cache pre-cargado con {len(products_data)} productos")
            return True
            
        except Exception as e:
            print(f"Error pre-cargando cache: {e}")
            return False

# Instancia global del servicio de cache
redis_cache = SimpleCacheService()

























