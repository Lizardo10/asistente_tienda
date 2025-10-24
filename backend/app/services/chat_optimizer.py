"""
Funciones avanzadas para optimización del chat con Redis Cache
"""
import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json
import re

from .. import models
from .redis_py_cache import redis_cache

class ChatOptimizer:
    """Sistema de optimización avanzada para el chat con Redis Cache"""
    
    def __init__(self):
        self.active_connections: Dict[str, Dict] = {}
        self.message_cache: Dict[str, List] = {}
        self.rate_limits: Dict[str, Dict] = {}
        self.user_sessions: Dict[str, Dict] = {}
        self.cache_enabled = False
    
    async def initialize(self):
        """Inicializa el optimizador y conecta al cache"""
        self.cache_enabled = True  # Cache simple siempre está disponible
        print("✅ Chat Optimizer inicializado con Cache en Memoria")
    
    async def optimize_message_processing(
        self, 
        message: str, 
        user_context: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """
        Optimiza el procesamiento de mensajes con Redis Cache
        """
        user_id = user_context.get("user_id") or "guest"
        user_type = user_context.get("user_type", "guest")
        
        # 1. Verificar cache de respuesta completa
        if self.cache_enabled:
            cached_response = await redis_cache.get_cached_response(message)
            if cached_response:
                print(f"🚀 Respuesta obtenida desde cache para: {message[:30]}...")
                return cached_response
        
        # 2. Verificar rate limiting con cache
        if not await self._check_rate_limit_cached(user_id):
            return {
                "type": "error",
                "message": "⚠️ Estás enviando mensajes muy rápido. Espera un momento antes de enviar otro mensaje.",
                "context": {"rate_limited": True}
            }
        
        # 3. Verificar cache de análisis de intención
        intent = None
        if self.cache_enabled:
            intent = await redis_cache.get_cached_intent_analysis(message)
        
        if not intent:
            intent = self._analyze_user_intent(message)
            if self.cache_enabled:
                await redis_cache.cache_intent_analysis(message, intent)
        
        # 4. Verificar cache de detección de spam
        spam_result = None
        if self.cache_enabled:
            spam_result = await redis_cache.get_cached_spam_detection(message)
        
        if not spam_result:
            is_spam = self._detect_spam(message, user_id)
            spam_result = {"is_spam": is_spam, "timestamp": datetime.now().isoformat()}
            if self.cache_enabled:
                await redis_cache.cache_spam_detection(message, is_spam)
        
        if spam_result["is_spam"]:
            return {
                "type": "warning",
                "message": "🚫 Por favor, mantén un lenguaje respetuoso en el chat.",
                "context": {"spam_detected": True}
            }
        
        # 5. Optimización de contexto con cache
        optimized_context = await self._optimize_context_cached(message, user_context, db)
        
        # 6. Respuesta inteligente basada en intención
        response = await self._generate_intelligent_response_cached(
            message, intent, optimized_context, user_context
        )
        
        # 7. Cachear la respuesta completa
        if self.cache_enabled:
            await redis_cache.cache_response(message, response)
        
        # 8. Actualizar métricas de usuario con cache
        await self._update_user_metrics_cached(user_id, message, intent)
        
        return response
    
    def _check_rate_limit(self, user_id: str) -> bool:
        """Verifica rate limiting para prevenir spam"""
        now = time.time()
        
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = {"messages": [], "last_reset": now}
        
        user_limits = self.rate_limits[user_id]
        
        # Limpiar mensajes antiguos (últimos 60 segundos)
        user_limits["messages"] = [
            msg_time for msg_time in user_limits["messages"] 
            if now - msg_time < 60
        ]
        
        # Verificar límite: máximo 10 mensajes por minuto
        if len(user_limits["messages"]) >= 10:
            return False
        
        # Agregar mensaje actual
        user_limits["messages"].append(now)
        return True
    
    def _analyze_user_intent(self, message: str) -> Dict[str, Any]:
        """Analiza la intención del usuario de manera avanzada"""
        message_lower = message.lower()
        
        intents = {
            "greeting": any(word in message_lower for word in [
                "hola", "hello", "hi", "buenos días", "buenas tardes", "buenas noches"
            ]),
            "product_inquiry": any(word in message_lower for word in [
                "producto", "productos", "item", "items", "qué tienen", "catálogo",
                "laptop", "ropa", "zapatos", "precio", "comprar"
            ]),
            "price_inquiry": any(word in message_lower for word in [
                "precio", "precios", "costo", "cuánto cuesta", "valor", "barato", "caro"
            ]),
            "shipping_inquiry": any(word in message_lower for word in [
                "envío", "envíos", "entrega", "delivery", "cuándo llega", "shipping"
            ]),
            "support_request": any(word in message_lower for word in [
                "ayuda", "soporte", "problema", "error", "no funciona", "issue"
            ]),
            "complaint": any(word in message_lower for word in [
                "queja", "malo", "terrible", "pésimo", "odio", "molesto"
            ]),
            "compliment": any(word in message_lower for word in [
                "excelente", "genial", "perfecto", "bueno", "me gusta", "gracias"
            ])
        }
        
        # Detectar intención principal
        primary_intent = max(intents.items(), key=lambda x: x[1])
        
        return {
            "primary": primary_intent[0] if primary_intent[1] else "general",
            "confidence": primary_intent[1],
            "all_intents": intents
        }
    
    def _detect_spam(self, message: str, user_id: str) -> bool:
        """Detecta posibles mensajes de spam o abuso"""
        # Detectar repetición excesiva
        words = message.lower().split()
        if len(words) > 0:
            most_common_word = max(set(words), key=words.count)
            if words.count(most_common_word) > len(words) * 0.6:  # 60% de palabras repetidas
                return True
        
        # Detectar mensajes muy largos (posible spam)
        if len(message) > 500:
            return True
        
        # Detectar caracteres repetidos excesivamente
        if re.search(r'(.)\1{10,}', message):  # 10+ caracteres repetidos
            return True
        
        # Detectar palabras inapropiadas básicas
        inappropriate_words = ["spam", "scam", "fake", "estafa"]
        if any(word in message.lower() for word in inappropriate_words):
            return True
        
        return False
    
    def _optimize_context(
        self, 
        message: str, 
        user_context: Dict[str, Any], 
        db: Session
    ) -> Dict[str, Any]:
        """Optimiza el contexto para respuestas más precisas"""
        user_id = user_context.get("user_id")
        user_type = user_context.get("user_type", "guest")
        
        # Obtener historial optimizado
        history = self._get_optimized_history(user_id, db)
        
        # Obtener contexto de productos relevante
        product_context = self._get_relevant_products(message, db)
        
        # Obtener contexto de usuario
        user_preferences = self._get_user_preferences(user_id, db)
        
        return {
            "history": history,
            "products": product_context,
            "preferences": user_preferences,
            "user_type": user_type,
            "session_data": self.user_sessions.get(str(user_id), {})
        }
    
    def _get_optimized_history(self, user_id: Optional[int], db: Session) -> List[Dict]:
        """Obtiene historial optimizado del usuario"""
        if not user_id:
            return []
        
        try:
            # Obtener últimos 5 mensajes del usuario
            recent_messages = db.query(models.ChatMessage).filter(
                models.ChatMessage.chat_id.in_(
                    db.query(models.Chat.id).filter(
                        models.Chat.user_id == user_id
                    )
                )
            ).order_by(models.ChatMessage.created_at.desc()).limit(5).all()
            
            return [
                {
                    "sender": msg.sender,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat()
                }
                for msg in reversed(recent_messages)
            ]
        except Exception:
            return []
    
    def _get_relevant_products(self, message: str, db: Session) -> List[Dict]:
        """Obtiene productos relevantes basados en el mensaje"""
        try:
            # Buscar productos mencionados en el mensaje
            products = db.query(models.Product).filter(
                models.Product.active == True
            ).all()
            
            relevant_products = []
            message_lower = message.lower()
            
            for product in products:
                # Verificar si el producto es mencionado
                if (product.title.lower() in message_lower or 
                    any(word in product.title.lower() for word in message_lower.split())):
                    relevant_products.append({
                        "id": product.id,
                        "title": product.title,
                        "price": float(product.price),
                        "description": product.description,
                        "relevance_score": 1.0
                    })
            
            # Si no hay productos específicos, devolver productos populares
            if not relevant_products:
                popular_products = products[:3]  # Primeros 3 productos
                relevant_products = [
                    {
                        "id": p.id,
                        "title": p.title,
                        "price": float(p.price),
                        "description": p.description,
                        "relevance_score": 0.5
                    }
                    for p in popular_products
                ]
            
            return relevant_products
        except Exception:
            return []
    
    def _get_user_preferences(self, user_id: Optional[int], db: Session) -> Dict[str, Any]:
        """Obtiene preferencias del usuario"""
        if not user_id:
            return {"type": "guest", "preferences": {}}
        
        try:
            # Aquí podrías implementar lógica para obtener preferencias del usuario
            # Por ahora, devolvemos información básica
            return {
                "type": "registered",
                "user_id": user_id,
                "preferences": {
                    "language": "es",
                    "notifications": True
                }
            }
        except Exception:
            return {"type": "guest", "preferences": {}}
    
    def _generate_intelligent_response(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera respuesta inteligente basada en intención y contexto"""
        
        # Respuestas optimizadas por intención
        if intent["primary"] == "greeting":
            return {
                "type": "bot",
                "message": "¡Hola! 👋 Bienvenido a nuestro chat de soporte. Soy tu asistente virtual y estoy aquí para ayudarte con cualquier consulta sobre productos, precios, envíos o cualquier otra información que necesites. ¿En qué puedo asistirte hoy?",
                "context": {
                    "suggested_actions": ["Ver productos", "Consultar precios", "Información de envío"],
                    "quick_replies": ["Productos", "Precios", "Envíos", "Ayuda"]
                }
            }
        
        elif intent["primary"] == "product_inquiry":
            products = context.get("products", [])
            if products:
                product_list = "\n".join([
                    f"🎯 **{p['title']}** - ${p['price']:.2f}\n"
                    f"   📝 {p['description'][:80]}...\n"
                    f"   🔗 [Ver producto](https://tu-tienda.com/producto/{p['id']})\n"
                    for p in products[:3]
                ])
                
                return {
                    "type": "bot",
                    "message": f"¡Perfecto! 🛍️ Aquí tienes algunos productos que podrían interesarte:\n\n{product_list}\n\n¿Te interesa alguno en particular o necesitas más información?",
                    "context": {
                        "product_mentions": [p['title'] for p in products],
                        "suggested_actions": ["Ver más productos", "Comparar precios", "Agregar al carrito"]
                    }
                }
        
        elif intent["primary"] == "price_inquiry":
            return {
                "type": "bot",
                "message": "💰 Nuestros precios son muy competitivos y van desde $45 hasta $200 aproximadamente. ¿Hay algún producto específico del que te gustaría conocer el precio exacto?",
                "context": {
                    "suggested_actions": ["Ver productos", "Comparar precios", "Ofertas especiales"]
                }
            }
        
        elif intent["primary"] == "shipping_inquiry":
            return {
                "type": "bot",
                "message": "🚚 ¡Excelente pregunta! Ofrecemos varias opciones de envío:\n\n• **Envío estándar**: 2-3 días hábiles - $15\n• **Envío express**: 1 día hábil - $25\n• **Envío gratis**: Para compras superiores a $100\n• **Retiro en tienda**: Gratuito\n\n¿Te gustaría saber más sobre nuestras opciones de envío?",
                "context": {
                    "suggested_actions": ["Calcular envío", "Ver zonas de entrega", "Rastrear pedido"]
                }
            }
        
        elif intent["primary"] == "support_request":
            return {
                "type": "bot",
                "message": "🆘 ¡Por supuesto! Estoy aquí para ayudarte. Puedo asistirte con:\n\n• Información sobre productos\n• Proceso de compra\n• Consultas sobre envíos\n• Resolución de problemas\n\n¿Cuál es el problema específico que necesitas resolver?",
                "context": {
                    "suggested_actions": ["Contactar soporte", "Ver FAQ", "Reportar problema"]
                }
            }
        
        elif intent["primary"] == "complaint":
            return {
                "type": "bot",
                "message": "😔 Lamento mucho que hayas tenido una experiencia negativa. Tu opinión es muy importante para nosotros y queremos resolver cualquier problema que hayas tenido. ¿Podrías contarme más detalles sobre lo que pasó para poder ayudarte mejor?",
                "context": {
                    "suggested_actions": ["Contactar supervisor", "Proceso de devolución", "Compensación"]
                }
            }
        
        elif intent["primary"] == "compliment":
            return {
                "type": "bot",
                "message": "😊 ¡Muchas gracias por tus palabras! Me alegra saber que estás satisfecho con nuestro servicio. ¿Hay algo más en lo que pueda ayudarte hoy?",
                "context": {
                    "suggested_actions": ["Ver más productos", "Dejar reseña", "Recomendar a amigos"]
                }
            }
        
        # Respuesta genérica optimizada
        return {
            "type": "bot",
            "message": f"🤖 Entiendo tu consulta sobre '{message[:50]}...'. Estoy aquí para ayudarte con información sobre nuestros productos, precios, envíos o cualquier otra consulta. ¿Podrías ser más específico sobre lo que necesitas?",
            "context": {
                "suggested_actions": ["Ver productos", "Consultar precios", "Información de envío", "Ayuda"]
            }
        }
    
    def _update_user_metrics(self, user_id: str, message: str, intent: Dict[str, Any]):
        """Actualiza métricas del usuario para mejorar el servicio"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                "message_count": 0,
                "intents": {},
                "last_activity": datetime.now(),
                "session_start": datetime.now()
            }
        
        session = self.user_sessions[user_id]
        session["message_count"] += 1
        session["last_activity"] = datetime.now()
        
        # Actualizar contador de intenciones
        primary_intent = intent["primary"]
        if primary_intent not in session["intents"]:
            session["intents"][primary_intent] = 0
        session["intents"][primary_intent] += 1
    
    def get_chat_analytics(self) -> Dict[str, Any]:
        """Obtiene analytics del chat para monitoreo"""
        return {
            "active_connections": len(self.active_connections),
            "total_sessions": len(self.user_sessions),
            "rate_limited_users": len([
                user for user, limits in self.rate_limits.items()
                if len(limits["messages"]) >= 8
            ]),
            "most_common_intents": self._get_most_common_intents()
        }
    
    def _get_most_common_intents(self) -> List[Dict[str, Any]]:
        """Obtiene las intenciones más comunes"""
        intent_counts = {}
        for session in self.user_sessions.values():
            for intent, count in session["intents"].items():
                if intent not in intent_counts:
                    intent_counts[intent] = 0
                intent_counts[intent] += count
        
        return [
            {"intent": intent, "count": count}
            for intent, count in sorted(intent_counts.items(), key=lambda x: x[1], reverse=True)
        ]
    
    # ==================== MÉTODOS OPTIMIZADOS CON REDIS ====================
    
    async def _check_rate_limit_cached(self, user_id: str) -> bool:
        """Verifica rate limiting usando cache"""
        if not self.cache_enabled:
            return self._check_rate_limit(user_id)
        
        cached_data = await redis_cache.get_cached_rate_limit(user_id)
        now = time.time()
        
        if cached_data:
            # Usar datos del cache
            messages = cached_data.get("messages", [])
            last_reset = cached_data.get("last_reset", now)
            
            # Limpiar mensajes antiguos (últimos 60 segundos)
            messages = [msg_time for msg_time in messages if now - msg_time < 60]
            
            if len(messages) >= 10:
                return False
            
            messages.append(now)
            await redis_cache.cache_rate_limit(user_id, {
                "messages": messages,
                "last_reset": last_reset
            })
            return True
        else:
            # Primera vez, crear entrada
            await redis_cache.cache_rate_limit(user_id, {
                "messages": [now],
                "last_reset": now
            })
            return True
    
    async def _optimize_context_cached(
        self, 
        message: str, 
        user_context: Dict[str, Any], 
        db: Session
    ) -> Dict[str, Any]:
        """Optimiza el contexto usando cache"""
        user_id = user_context.get("user_id")
        
        # Cache de productos
        products_data = None
        if self.cache_enabled:
            products_data = await redis_cache.get_cached_product_context()
        
        if not products_data:
            products_data = self._get_relevant_products(message, db)
            if self.cache_enabled and products_data:
                await redis_cache.cache_product_context(products_data)
        
        # Cache de sesión de usuario
        session_data = None
        if self.cache_enabled and user_id:
            session_data = await redis_cache.get_cached_user_session(str(user_id))
        
        if not session_data:
            session_data = self._get_user_preferences(user_id, db)
            if self.cache_enabled and user_id:
                await redis_cache.cache_user_session(str(user_id), session_data)
        
        # Cache de historial de conversación
        history = []
        chat_id = user_context.get("chat_id")
        if self.cache_enabled and chat_id:
            history = await redis_cache.get_cached_conversation_history(chat_id) or []
        
        if not history and user_id:
            history = self._get_optimized_history(user_id, db)
            if self.cache_enabled and chat_id:
                await redis_cache.cache_conversation_history(chat_id, history)
        
        return {
            "history": history,
            "products": products_data or [],
            "preferences": session_data or {"type": "guest", "preferences": {}},
            "user_type": user_context.get("user_type", "guest"),
            "session_data": session_data or {}
        }
    
    async def _generate_intelligent_response_cached(
        self,
        message: str,
        intent: Dict[str, Any],
        context: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera respuesta inteligente con cache de recomendaciones"""
        user_id = user_context.get("user_id") or "guest"
        
        # Cache de recomendaciones de productos
        recommendations = []
        if self.cache_enabled:
            recommendations = await redis_cache.get_cached_product_recommendations(str(user_id)) or []
        
        # Generar respuesta base
        response = self._generate_intelligent_response(message, intent, context, user_context)
        
        # Agregar recomendaciones cacheadas si están disponibles
        if recommendations and "context" in response:
            response["context"]["recommendations"] = recommendations
        
        return response
    
    async def _update_user_metrics_cached(self, user_id: str, message: str, intent: Dict[str, Any]):
        """Actualiza métricas de usuario usando cache"""
        if not self.cache_enabled:
            self._update_user_metrics(user_id, message, intent)
            return
        
        # Obtener sesión actual del cache
        session_data = await redis_cache.get_cached_user_session(user_id) or {
            "message_count": 0,
            "intents": {},
            "last_activity": datetime.now().isoformat(),
            "session_start": datetime.now().isoformat()
        }
        
        # Actualizar métricas
        session_data["message_count"] += 1
        session_data["last_activity"] = datetime.now().isoformat()
        
        # Actualizar contador de intenciones
        primary_intent = intent["primary"]
        if primary_intent not in session_data["intents"]:
            session_data["intents"][primary_intent] = 0
        session_data["intents"][primary_intent] += 1
        
        # Guardar en cache
        await redis_cache.cache_user_session(user_id, session_data)
    
    async def get_chat_analytics_cached(self) -> Dict[str, Any]:
        """Obtiene analytics del chat con información de cache"""
        base_analytics = self.get_chat_analytics()
        
        if self.cache_enabled:
            cache_stats = await redis_cache.get_cache_stats()
            base_analytics["cache"] = cache_stats
            base_analytics["cache_enabled"] = True
        else:
            base_analytics["cache_enabled"] = False
            base_analytics["cache"] = {"status": "disconnected"}
        
        return base_analytics
    
    async def warm_up_cache(self, db_session):
        """Pre-carga datos importantes en cache"""
        if self.cache_enabled:
            await redis_cache.warm_up_cache(db_session)

# Instancia global del optimizador
chat_optimizer = ChatOptimizer()
