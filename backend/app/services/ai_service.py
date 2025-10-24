"""
Servicio de IA modernizado con GPT-4 Turbo y LangGraph
Siguiendo el principio de Single Responsibility (SOLID)
"""
import os
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


@dataclass
class AIResponse:
    """Response model para respuestas de IA"""
    success: bool
    content: str
    usage: Optional[Dict[str, int]] = None
    error: Optional[str] = None


class AIServiceInterface(ABC):
    """Interface para el servicio de IA - Dependency Inversion Principle"""
    
    @abstractmethod
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> AIResponse:
        pass
    
    @abstractmethod
    async def analyze_intent(self, message: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def extract_recommendations(self, content: str) -> List[Dict[str, str]]:
        pass


class OpenAIService(AIServiceInterface):
    """Implementación del servicio de IA con OpenAI"""
    
    def __init__(self, api_key: Optional[str] = None):
        # Importar configuración centralizada
        from app.core.config import settings
        
        self.api_key = api_key or settings.openai_api_key
        self.client = None
        
        if OPENAI_AVAILABLE and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                print("OpenAI client inicializado correctamente")
            except Exception as e:
                print(f"Error inicializando OpenAI client: {e}")
                self.client = None
    
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> AIResponse:
        """Genera respuesta usando GPT-4 Turbo"""
        if not self.client:
            return AIResponse(
                success=False,
                content="🤖 (Simulado) Entiendo tu consulta. OpenAI no está configurado.",
                error="OpenAI client not initialized"
            )
        
        try:
            messages = self._build_messages(prompt, context)
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                stream=False
            )
            
            return AIResponse(
                success=True,
                content=response.choices[0].message.content,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )
            
        except Exception as e:
            return AIResponse(
                success=False,
                content=f"Lo siento, hubo un error procesando tu consulta: {str(e)}",
                error=str(e)
            )
    
    def _build_messages(self, prompt: str, context: Dict[str, Any] = None) -> List[Dict[str, str]]:
        """Construye mensajes para el chat"""
        messages = []
        
        # Mensaje del sistema
        system_message = """Eres un asistente de ventas virtual experto para una tienda online. 
        Tu objetivo es ayudar a los clientes de manera profesional, cordial y útil.
        
        INSTRUCCIONES:
        - Mantén un tono amigable y profesional
        - Usa emojis apropiados para hacer las respuestas atractivas
        - Si hay productos disponibles, destaca sus características
        - Responde en español de manera natural
        - Mantén las respuestas concisas pero informativas
        - Muestra entusiasmo genuino por ayudar al cliente"""
        
        messages.append({"role": "system", "content": system_message})
        
        # Agregar contexto si está disponible
        if context:
            if context.get("product_context"):
                messages.append({
                    "role": "system", 
                    "content": f"CONTEXTO DE PRODUCTOS:\n{context['product_context']}"
                })
            
            if context.get("conversation_history"):
                for msg in context["conversation_history"][-5:]:
                    role = "user" if msg.sender == "user" else "assistant"
                    messages.append({"role": role, "content": msg.content})
        
        # Agregar la consulta del usuario
        messages.append({"role": "user", "content": prompt})
        
        return messages
    
    async def analyze_intent(self, message: str) -> Dict[str, Any]:
        """Analiza la intención del mensaje"""
        if not self.client:
            return {"intent": "general", "confidence": 0.5, "entities": []}
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """Analiza la intención del mensaje del usuario. Responde SOLO con un JSON válido en este formato exacto:
{
    "intent": "greeting|product_inquiry|price_inquiry|order_inquiry|general",
    "confidence": 0.8,
    "entities": []
}

No incluyas texto adicional, solo el JSON."""
                    },
                    {"role": "user", "content": message}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            # Obtener respuesta y limpiar
            content = response.choices[0].message.content.strip()
            print(f"Respuesta de análisis de intención: '{content}'")
            
            # Parsear respuesta JSON
            import json
            result = json.loads(content)
            
            # Validar que tenga las claves necesarias
            if not all(key in result for key in ["intent", "confidence", "entities"]):
                raise ValueError("JSON no tiene las claves necesarias")
                
            return result
            
        except json.JSONDecodeError as e:
            print(f"Error JSON en análisis de intención: {e}")
            print(f"Contenido recibido: '{content if 'content' in locals() else 'No disponible'}'")
            return {"intent": "general", "confidence": 0.5, "entities": []}
        except Exception as e:
            print(f"Error analizando intención: {e}")
            return {"intent": "general", "confidence": 0.5, "entities": []}
    
    async def extract_recommendations(self, content: str) -> List[Dict[str, str]]:
        """Extrae recomendaciones de productos de la respuesta"""
        import re
        
        recommendations = []
        patterns = [
            r'recomiendo\s+([^.!?]+)',
            r'te\s+sugiero\s+([^.!?]+)',
            r'producto[s]?\s+([^.!?]+)',
            r'item[s]?\s+([^.!?]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content.lower())
            for match in matches:
                if len(match.strip()) > 3:
                    recommendations.append({
                        "product": match.strip(),
                        "reason": "Recomendado por el asistente"
                    })
        
        return recommendations


class MockAIService(AIServiceInterface):
    """Implementación mock para cuando OpenAI no está disponible"""
    
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> AIResponse:
        """Genera respuesta simulada"""
        prompt_lower = prompt.lower()
        
        # Respuestas inteligentes simuladas
        if any(word in prompt_lower for word in ['hola', 'buenos días', 'saludos']):
            content = "¡Hola! 👋 Bienvenido a nuestra tienda online. Soy tu asistente virtual y estoy aquí para ayudarte con cualquier consulta sobre nuestros productos, precios, envíos o cualquier otra información que necesites. ¿En qué puedo asistirte hoy?"
        elif any(word in prompt_lower for word in ['productos', 'producto', 'items']):
            content = "📦 Tenemos una gran variedad de productos disponibles. ¿Hay algún tipo de producto específico que te interese? Puedo ayudarte a encontrar lo que necesitas."
        elif any(word in prompt_lower for word in ['precio', 'precios', 'costo']):
            content = "💰 Nuestros precios son muy competitivos. Los productos van desde $45 hasta $200 aproximadamente. ¿Hay algún producto específico del que te gustaría conocer el precio exacto?"
        elif any(word in prompt_lower for word in ['comprar', 'pedido', 'orden']):
            content = "🛒 ¡Excelente! Para hacer un pedido es muy fácil:\n\n1. Navega por nuestros productos\n2. Selecciona los que te interesen\n3. Agrégalos al carrito\n4. Procede al checkout\n5. Completa tus datos de envío\n\n¿Necesitas ayuda con algún paso específico?"
        else:
            content = f"🤖 Entiendo tu consulta sobre '{prompt[:50]}...'. Estoy aquí para ayudarte con información sobre nuestros productos, precios, envíos o cualquier otra consulta. ¿Podrías ser más específico sobre lo que necesitas?"
        
        return AIResponse(success=True, content=content)
    
    async def analyze_intent(self, message: str) -> Dict[str, Any]:
        """Analiza intención simulada"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hola', 'saludos']):
            return {"intent": "greeting", "confidence": 0.9, "entities": []}
        elif any(word in message_lower for word in ['producto', 'comprar']):
            return {"intent": "product_inquiry", "confidence": 0.8, "entities": []}
        elif any(word in message_lower for word in ['precio', 'costo']):
            return {"intent": "price_inquiry", "confidence": 0.8, "entities": []}
        else:
            return {"intent": "general", "confidence": 0.5, "entities": []}
    
    async def extract_recommendations(self, content: str) -> List[Dict[str, str]]:
        """Extrae recomendaciones simuladas"""
        return []


# Factory para crear el servicio de IA apropiado
def create_ai_service() -> AIServiceInterface:
    """Factory method para crear el servicio de IA apropiado"""
    # Importar configuración centralizada
    from app.core.config import settings
    
    if OPENAI_AVAILABLE and settings.openai_api_key:
        return OpenAIService(api_key=settings.openai_api_key)
    else:
        return MockAIService()


# Instancia global del servicio de IA
ai_service = create_ai_service()
