"""
Servicio de IA moderno con Clean Architecture
Usa tu API de OpenAI original sin modificarla
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from app.services.openai_service import ask_openai, generate_contextual_response, extract_product_recommendations
from app.services.rag_service import rag_answer, advanced_rag_answer

class IModernAIService(ABC):
    """Interface para el servicio de IA moderno - Dependency Inversion Principle"""
    
    @abstractmethod
    async def generate_smart_response(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def analyze_user_intent(self, message: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def generate_product_recommendations(self, user_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

class ModernAIService(IModernAIService):
    """Implementación moderna del servicio de IA usando tu OpenAI original"""
    
    def __init__(self):
        self.cache = {}  # Cache simple para optimizar respuestas
    
    async def generate_response(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Alias para generate_smart_response para compatibilidad"""
        return await self.generate_smart_response(message, context)
    
    async def generate_smart_response(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera una respuesta inteligente usando tu API de OpenAI con RAG
        """
        try:
            # Importar aquí para evitar problemas de importación circular
            from app.database.connection import get_db
            from app.services.rag_service import advanced_rag_answer
            
            # Obtener contexto RAG real con productos de la base de datos
            db = next(get_db())
            
            # Convertir historial del chat al formato que espera el RAG
            history_for_rag = []
            if context.get("history"):
                for hist_msg in context["history"]:
                    # Manejar tanto objetos como diccionarios
                    if isinstance(hist_msg, dict):
                        history_for_rag.append({
                            "sender": hist_msg.get("sender", "user"),
                            "content": hist_msg.get("content", "")
                        })
                    else:
                        history_for_rag.append({
                            "sender": hist_msg.sender,
                            "content": hist_msg.content
                        })
            
            # Usar RAG avanzado para obtener contexto real de productos
            rag_result = advanced_rag_answer(message, db, history_for_rag)
            
            # Usar tu función original de OpenAI con el contexto RAG real
            response = generate_contextual_response(message, rag_result, history_for_rag)
            
            # Analizar intención del usuario
            intent = await self.analyze_user_intent(message)
            
            # Generar recomendaciones si es necesario
            recommendations = []
            print(f"🔍 Analizando intención: {intent}")
            if intent.get("type") == "product_inquiry":
                print("✅ Intención detectada como product_inquiry, generando recomendaciones...")
                recommendations = await self.generate_product_recommendations(context)
                print(f"📦 Recomendaciones generadas: {len(recommendations)}")
            else:
                print(f"⚠️ Intención no es product_inquiry: {intent.get('type')}")
            
            return {
                "response": response,
                "intent": intent,
                "recommendations": recommendations,
                "confidence": 0.95,
                "timestamp": context.get("timestamp"),
                "context_used": True,
                "rag_context": rag_result  # Incluir contexto RAG para debugging
            }
            
        except Exception as e:
            print(f"Error en ModernAIService: {e}")
            import traceback
            traceback.print_exc()
            # Fallback a tu función original
            fallback_response = ask_openai(message)
            return {
                "response": fallback_response,
                "intent": {"type": "general", "confidence": 0.7},
                "recommendations": [],
                "confidence": 0.7,
                "timestamp": context.get("timestamp"),
                "context_used": False,
                "error": str(e)
            }
    
    async def analyze_user_intent(self, message: str) -> Dict[str, Any]:
        """
        Analiza la intención del usuario usando patrones mejorados
        """
        try:
            message_lower = message.lower()
            
            # Patrones para detectar consultas de productos
            product_patterns = [
                'producto', 'productos', 'item', 'items',
                'zapatos', 'camisas', 'pantalones', 'ropa',
                'tienen', 'disponible', 'disponibles',
                'muéstrame', 'muestra', 'ver', 'quiero ver',
                'recomienda', 'recomendación', 'sugiere',
                'comprar', 'compras', 'tienda', 'catalogo'
            ]
            
            # Detectar si es una consulta de productos
            is_product_inquiry = any(pattern in message_lower for pattern in product_patterns)
            
            # Detectar entidades específicas
            entities = []
            if 'zapatos' in message_lower:
                entities.append('zapatos')
            if 'camisas' in message_lower:
                entities.append('camisas')
            if 'pantalones' in message_lower:
                entities.append('pantalones')
            if 'ropa' in message_lower:
                entities.append('ropa')
            
            return {
                "type": "product_inquiry" if is_product_inquiry else "general",
                "confidence": 0.9 if is_product_inquiry else 0.7,
                "entities": entities,
                "sentiment": "neutral"
            }
            
        except Exception as e:
            return {
                "type": "general",
                "confidence": 0.5,
                "entities": [],
                "sentiment": "neutral",
                "error": str(e)
            }
    
    async def generate_product_recommendations(self, user_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Genera recomendaciones de productos reales de la base de datos
        """
        try:
            print("🔍 Iniciando generación de recomendaciones...")
            from app.db import get_db
            from app import models
            
            # Obtener productos reales de la base de datos
            print("📊 Obteniendo productos de la base de datos...")
            db = next(get_db())
            products = db.query(models.Product).filter(models.Product.active == True).limit(6).all()
            
            print(f"📦 Productos encontrados: {len(products)}")
            
            if not products:
                print("⚠️ No hay productos activos en la base de datos")
                return []
            
            # Convertir productos a formato de recomendación
            recommendations = []
            for i, product in enumerate(products[:3]):  # Máximo 3 recomendaciones
                print(f"🛍️ Procesando producto {i+1}: {product.title}")
                recommendations.append({
                    "id": product.id,
                    "title": product.title,
                    "price": float(product.price),
                    "image_url": product.image_url,
                    "description": product.description,
                    "reason": f"Producto destacado de nuestra colección",
                    "confidence": 0.9 - (i * 0.1)
                })
            
            print(f"✅ Generadas {len(recommendations)} recomendaciones reales")
            return recommendations
            
        except Exception as e:
            print(f"❌ Error generando recomendaciones: {e}")
            import traceback
            traceback.print_exc()
            return []

# Instancia global del servicio de IA moderno
modern_ai_service = ModernAIService()

