import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

client = None
if OpenAI and os.getenv("OPENAI_API_KEY"):
    try:
        client = OpenAI()
    except Exception as e:
        print(f"Warning: No se pudo inicializar el cliente de OpenAI: {e}")
        client = None

def ask_openai(prompt: str) -> str:
    """
    Función básica que mantiene compatibilidad con el código existente
    """
    if client is None:
        return generate_smart_response(prompt)
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":"Eres un asistente de soporte amable y breve."},
                      {"role":"user","content": prompt}],
            temperature=0.2,
            max_tokens=300
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"(OpenAI error) {e}"

def advanced_chat_completion(
    messages: List[Dict[str, str]], 
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_tokens: int = 500,
    stream: bool = False
) -> Dict[str, Any]:
    """
    Función avanzada para completar conversaciones con más control
    """
    if client is None:
        return {
            "success": False,
            "error": "OpenAI client not initialized",
            "response": "🤖 (Simulado) Entiendo tu consulta. OpenAI no está configurado."
        }
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
        
        if stream:
            return {
                "success": True,
                "stream": response
            }
        else:
            return {
                "success": True,
                "response": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response": f"Lo siento, hubo un error procesando tu consulta: {str(e)}"
        }

def generate_smart_response(prompt: str, db=None, rag_context: str = "") -> str:
    """
    Genera una respuesta inteligente usando la base de datos y RAG cuando OpenAI no está disponible
    """
    prompt_lower = prompt.lower()
    
    # Respuestas para saludos
    if any(word in prompt_lower for word in ['hola', 'buenos días', 'buenas tardes', 'buenas noches', 'saludos']):
        return "¡Hola! 👋 Bienvenido a nuestra tienda online. Soy tu asistente virtual y estoy aquí para ayudarte con cualquier consulta sobre nuestros productos, precios, envíos o cualquier otra información que necesites. ¿En qué puedo asistirte hoy?"
    
    # Respuestas sobre productos
    if any(word in prompt_lower for word in ['productos', 'producto', 'items', 'artículos', 'qué tienen', 'catálogo']):
        if db:
            try:
                from ..models import Product
                products = db.query(Product).filter(Product.active == True).limit(5).all()
                if products:
                    response = "📦 Aquí tienes algunos de nuestros productos disponibles:\n\n"
                    for product in products:
                        response += f"• **{product.title}** - ${product.price:.2f}\n"
                        if product.description:
                            response += f"  _{product.description[:80]}..._\n\n"
                    response += "¿Te interesa algún producto en particular? Puedo darte más detalles."
                    return response
            except Exception:
                pass
        return "📦 Tenemos una gran variedad de productos disponibles. ¿Hay algún tipo de producto específico que te interese? Puedo ayudarte a encontrar lo que necesitas."
    
    # Respuestas sobre precios
    if any(word in prompt_lower for word in ['precio', 'precios', 'costo', 'costos', 'cuánto cuesta', 'valor']):
        if db:
            try:
                from ..models import Product
                products = db.query(Product).filter(Product.active == True).all()
                if products:
                    min_price = min(p.price for p in products)
                    max_price = max(p.price for p in products)
                    return f"💰 Nuestros precios son muy competitivos. Los productos van desde ${min_price:.2f} hasta ${max_price:.2f}. ¿Hay algún producto específico del que te gustaría conocer el precio exacto?"
            except Exception:
                pass
        return "💰 Nuestros precios son muy competitivos. Los productos van desde $45 hasta $200 aproximadamente. ¿Hay algún producto específico del que te gustaría conocer el precio exacto?"
    
    # Respuestas sobre compras/pedidos
    if any(word in prompt_lower for word in ['comprar', 'pedido', 'orden', 'cómo compro', 'cómo hago un pedido']):
        return "🛒 ¡Excelente! Para hacer un pedido es muy fácil:\n\n1. Navega por nuestros productos\n2. Selecciona los que te interesen\n3. Agrégalos al carrito\n4. Procede al checkout\n5. Completa tus datos de envío\n\n¿Necesitas ayuda con algún paso específico?"
    
    # Respuestas sobre envíos
    if any(word in prompt_lower for word in ['envío', 'envíos', 'entrega', 'delivery', 'cuándo llega']):
        return "🚚 Ofrecemos envíos a toda la ciudad. Los tiempos de entrega son:\n\n• Envío estándar: 2-3 días hábiles\n• Envío express: 1 día hábil\n• Envío gratis en compras mayores a $100\n\n¿Te gustaría saber más sobre nuestras opciones de envío?"
    
    # Respuestas sobre ayuda/soporte
    if any(word in prompt_lower for word in ['ayuda', 'soporte', 'problema', 'issue', 'error']):
        return "🆘 ¡Por supuesto! Estoy aquí para ayudarte. Puedo asistirte con:\n\n• Información sobre productos\n• Proceso de compra\n• Consultas sobre envíos\n• Resolución de problemas\n\n¿Cuál es el problema específico que necesitas resolver?"
    
    # Buscar productos específicos mencionados
    if db:
        try:
            from ..models import Product
            products = db.query(Product).filter(Product.active == True).all()
            for product in products:
                if product.title.lower() in prompt_lower:
                    return f"👕 ¡Perfecto! Sí tenemos **{product.title}** disponible por ${product.price:.2f}. {product.description[:100]}... ¿Te interesa este producto o necesitas más información?"
        except Exception:
            pass
    
    # Usar contexto RAG si está disponible
    if rag_context:
        return f"🤖 Basándome en la información disponible: {rag_context[:200]}... ¿Te gustaría que profundice en algún aspecto específico?"
    
    # Respuesta genérica inteligente
    return f"🤖 Entiendo tu consulta sobre '{prompt[:50]}...'. Estoy aquí para ayudarte con información sobre nuestros productos, precios, envíos o cualquier otra consulta. ¿Podrías ser más específico sobre lo que necesitas?"

def generate_contextual_response(
    query: str,
    context: Dict[str, Any],
    conversation_history: List[Dict[str, str]] = None
) -> str:
    """
    Genera una respuesta contextualizada usando el sistema RAG avanzado
    """
    if client is None:
        # Usar respuesta inteligente con contexto de la base de datos
        rag_context = ""
        if context.get("document_context"):
            rag_context = context["document_context"]
        elif context.get("product_context"):
            rag_context = context["product_context"]
        
        return generate_smart_response(query, rag_context=rag_context)
    
    # Construir mensajes para el chat
    messages = []
    
    # Mensaje del sistema con personalidad mejorada para productos
    # Mensaje del sistema con personalidad elegante y sofisticada
    system_message = """Eres una consultora de moda experta y elegante para una tienda online de alta calidad. 
    Tu objetivo es ayudar a los clientes de manera sofisticada, profesional y encantadora.
    
    ESTILO DE COMUNICACIÓN:
    - Tono elegante, sofisticado y amigable
    - Usa emojis de manera sutil y profesional
    - Lenguaje refinado pero accesible
    - Respuestas estructuradas y visualmente atractivas
    - Máximo 200 palabras por respuesta
    
    CUANDO MUESTRES PRODUCTOS:
    - Presenta cada producto como una joya única
    - Destaca características especiales y beneficios
    - Usa descripciones evocativas y atractivas
    - NO incluyas enlaces técnicos ni URLs
    - Enfócate en la experiencia del cliente
    - Sugiere combinaciones y estilos
    
    FORMATO ELEGANTE PARA PRODUCTOS:
    ✨ [Nombre del producto] - $[precio]
    💎 [Descripción atractiva y beneficios]
    🛍️ [Sugerencia de uso o combinación]
    
    PERSONALIDAD:
    - Eres una consultora de moda experta y elegante
    - Te emocionas por ayudar a crear looks perfectos
    - Eres detallista pero no abrumadora
    - Mantienes un aire de sofisticación y profesionalismo
    - Siempre terminas con una invitación amigable para más ayuda
    
    EJEMPLOS DE FRASES ELEGANTES:
    - Permíteme presentarte nuestros tesoros más preciados...
    - Este artículo es simplemente excepcional porque...
    - Imagínate luciendo este hermoso...
    - ¿Te gustaría conocer más detalles sobre algún producto en particular?"""
    
    messages.append({"role": "system", "content": system_message})
    
    # Agregar historial de conversación
    if conversation_history:
        for msg in conversation_history[-6:]:  # Últimos 6 mensajes para contexto
            # Manejar tanto objetos como diccionarios
            if isinstance(msg, dict):
                role = "user" if msg.get("sender") == "user" else "assistant"
                content = msg.get("content", "")
            else:
                role = "user" if msg.sender == "user" else "assistant"
                content = msg.content
            messages.append({"role": role, "content": content})
    
    # Construir prompt contextual mejorado
    context_parts = []
    
    if context.get("product_context"):
        context_parts.append(f"INFORMACIÓN DE PRODUCTOS DISPONIBLES:\n{context['product_context']}")
    
    if context.get("document_context"):
        context_parts.append(f"INFORMACIÓN ADICIONAL:\n{context['document_context']}")
    
    if context.get("product_mentions"):
        context_parts.append(f"El cliente mencionó estos productos: {', '.join(context['product_mentions'])}")
    
    if context_parts:
        context_prompt = "\n\n".join(context_parts)
        messages.append({"role": "system", "content": f"CONTEXTO ACTUAL:\n{context_prompt}"})
    
    # Agregar la consulta del usuario
    messages.append({"role": "user", "content": query})
    
    # Generar respuesta
    result = advanced_chat_completion(
        messages=messages,
        model="gpt-4o-mini",
        temperature=0.8,  # Aumentar creatividad
        max_tokens=500    # Permitir respuestas más largas para productos
    )
    
    if result["success"]:
        return result["response"]
    else:
        return result["response"]  # Ya incluye mensaje de error amigable

def extract_product_recommendations(response: str) -> List[Dict[str, str]]:
    """
    Extrae recomendaciones de productos de la respuesta del LLM
    """
    # Patrón simple para detectar menciones de productos
    import re
    
    recommendations = []
    # Buscar patrones como "Producto X", "Te recomiendo Y", etc.
    patterns = [
        r'recomiendo\s+([^.!?]+)',
        r'te\s+sugiero\s+([^.!?]+)',
        r'producto[s]?\s+([^.!?]+)',
        r'item[s]?\s+([^.!?]+)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, response.lower())
        for match in matches:
            if len(match.strip()) > 3:
                recommendations.append({
                    "product": match.strip(),
                    "reason": "Recomendado por el asistente"
                })
    
    return recommendations
