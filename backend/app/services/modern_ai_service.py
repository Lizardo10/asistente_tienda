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
        Genera una respuesta inteligente usando nuestras funciones mejoradas
        """
        try:
            # Importar aquí para evitar problemas de importación circular
            from app.database.connection import get_db
            
            # Obtener base de datos
            db = next(get_db())
            
            # SIEMPRE usar nuestra función inteligente mejorada con OpenAI
            print("🔄 Usando función inteligente mejorada de Asistente Tienda con OpenAI")
            from app.services.openai_service import generate_smart_response
            response = generate_smart_response(message, db)
            
            # Si la respuesta es muy corta o genérica, usar OpenAI directamente
            if len(response) < 50 or "¿En qué puedo ayudarte hoy?" in response:
                print("🔄 Respuesta muy genérica, usando OpenAI directamente")
                response = await self._call_openai_directly(message, db)
            
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
                'zapatos', 'camisas', 'pantalones', 'ropa', 'vestido', 'blusa',
                'tienen', 'disponible', 'disponibles', 'muéstrame', 'muestra', 
                'ver', 'quiero ver', 'mostrar', 'enseñar',
                'recomienda', 'recomendación', 'sugiere', 'sugerir',
                'comprar', 'compras', 'tienda', 'catalogo', 'catálogo',
                'precio', 'precios', 'costo', 'cuánto cuesta',
                'envío', 'envíos', 'entrega', 'delivery',
                'ayuda', 'soporte', 'horario', 'contacto'
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
    
    async def _call_openai_directly(self, message: str, db) -> str:
        """
        Llama directamente a OpenAI con contexto de productos
        """
        try:
            from app.services.openai_service import client
            
            if client is None:
                return "Lo siento, el servicio de IA no está disponible en este momento."
            
            # Obtener productos de la base de datos para contexto
            products_context = ""
            if db:
                try:
                    from app.models import Product
                    products = db.query(Product).filter(Product.active == True).limit(6).all()
                    if products:
                        products_context = "\n\nProductos disponibles en Asistente Tienda:\n"
                        for i, product in enumerate(products, 1):
                            products_context += f"{i}. {product.title} - Q{product.price:.2f} - {product.description}\n"
                except Exception as e:
                    print(f"Error obteniendo productos: {e}")
            
            # Construir mensaje del sistema
            system_message = f"""Eres una consultora de moda experta y elegante para Asistente Tienda, una tienda online de alta calidad. 
            Tu objetivo es ayudar a los clientes de manera sofisticada, profesional y encantadora.
            
            ESTILO DE COMUNICACIÓN:
            - Tono elegante, sofisticado y amigable
            - Usa emojis de manera sutil y profesional
            - Lenguaje refinado pero accesible
            - Respuestas estructuradas y visualmente atractivas
            - Siempre menciona "Asistente Tienda" cuando sea apropiado
            - Máximo 200 palabras por respuesta
            
            INFORMACIÓN DE LA TIENDA:
            - Somos Asistente Tienda, una tienda online especializada en moda
            - Ofrecemos productos de alta calidad con precios competitivos
            - Tenemos envíos a domicilio y atención personalizada
            - Nuestro horario de atención es de lunes a viernes de 9:00 a 18:00
            - Los precios están en Quetzales (Q)
            
            {products_context}
            
            INSTRUCCIONES ESPECÍFICAS:
            - Si preguntan por productos, menciona los disponibles y sus precios
            - Si preguntan por envíos, explica nuestras opciones de entrega
            - Si preguntan por horarios, menciona nuestro horario de atención
            - Siempre ofrece ayuda adicional y menciona que pueden hacer pedidos
            - Usa un tono profesional pero cálido
            - Mantén las respuestas concisas pero informativas
            - Responde siempre en español"""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error llamando a OpenAI directamente: {e}")
            return "Lo siento, hubo un error procesando tu mensaje. Por favor intenta de nuevo."
    
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

