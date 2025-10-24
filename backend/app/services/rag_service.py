import os, glob
from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from sqlalchemy.orm import Session
import re
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

RAG_INDEX_PATH = os.getenv("RAG_INDEX_PATH", "rag_index")

def _load_index():
    if not os.path.isdir(RAG_INDEX_PATH):
        return None
    try:
        # Solo cargar el índice si tenemos una API key válida
        if not os.getenv("OPENAI_API_KEY") or "sk-proj-" not in os.getenv("OPENAI_API_KEY", ""):
            return None
        embeddings = OpenAIEmbeddings()  # requiere OPENAI_API_KEY
        return FAISS.load_local(RAG_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    except Exception:
        return None

def _extract_product_mentions(query: str) -> List[str]:
    """Extrae posibles menciones de productos de la consulta"""
    # Patrones comunes para identificar productos
    patterns = [
        r'producto[s]?\s+([^.!?]+)',  # "producto X"
        r'item[s]?\s+([^.!?]+)',      # "item X"
        r'quiero\s+([^.!?]+)',        # "quiero X"
        r'busco\s+([^.!?]+)',         # "busco X"
        r'necesito\s+([^.!?]+)',      # "necesito X"
        r'me\s+interesa\s+([^.!?]+)', # "me interesa X"
        r'(\w+)\s+de\s+\w+',          # "X de Y"
    ]
    
    mentions = []
    for pattern in patterns:
        matches = re.findall(pattern, query.lower())
        mentions.extend(matches)
    
    return [m.strip() for m in mentions if len(m.strip()) > 2]

def _get_product_context(db: Session, query: str) -> str:
    """Obtiene contexto de productos de la base de datos con enlaces de compra"""
    from ..models_sqlmodel.product import Product
    
    # Buscar productos por título o descripción
    products = db.query(Product).filter(
        Product.active == True
    ).all()
    
    if not products:
        return ""
    
    # Crear contexto de productos mejorado y elegante
    product_context = "✨ NUESTROS PRODUCTOS DESTACADOS:\n\n"
    
    for product in products[:8]:  # Limitar a 8 productos para mejor legibilidad
        price_str = f"${product.price:.2f}" if product.price else "Consultar precio"
        
        # Crear descripción más elegante
        product_context += f"🌟 **{product.title}** - {price_str}\n"
        if product.description:
            # Limpiar y mejorar la descripción
            clean_description = product.description.replace('\n', ' ').strip()
            if len(clean_description) > 100:
                clean_description = clean_description[:100] + "..."
            product_context += f"   💎 {clean_description}\n"
        product_context += f"   🛒 Disponible para compra inmediata\n\n"
    
    # Agregar información adicional más elegante
    product_context += """
🎁 BENEFICIOS EXCLUSIVOS:
• Garantía de calidad en todos nuestros productos
• Envío gratuito en compras superiores a $100
• Proceso de compra rápido y seguro
• Atención personalizada 24/7
• Devoluciones sin complicaciones

💫 ¿Te interesa algún producto en particular? ¡Pregúntame por más detalles!
"""
    
    return product_context

def rag_answer(query: str, db: Optional[Session] = None) -> str:
    """
    Versión básica que mantiene compatibilidad con el código existente
    """
    vs = _load_index()
    if vs is None:
        return ""
    docs: List[Document] = vs.similarity_search(query, k=3)
    parts = [d.page_content.strip() for d in docs if d.page_content]
    if not parts:
        return ""
    return "\n---\n".join(parts[:3])

def advanced_rag_answer(query: str, db: Session, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Sistema RAG avanzado que combina documentos, productos y contexto de conversación
    """
    result = {
        "document_context": "",
        "product_context": "",
        "conversation_context": "",
        "product_mentions": [],
        "suggested_actions": []
    }
    
    # 1. Extraer menciones de productos
    product_mentions = _extract_product_mentions(query)
    result["product_mentions"] = product_mentions
    
    # 2. Buscar en documentos RAG (solo si está disponible)
    try:
        vs = _load_index()
        if vs:
            docs: List[Document] = vs.similarity_search(query, k=5)
            if docs:
                result["document_context"] = "\n---\n".join([d.page_content.strip() for d in docs if d.page_content])
    except Exception as e:
        # Si hay error con RAG, continuar sin él
        print(f"RAG error (continuando sin RAG): {e}")
        result["document_context"] = ""
    
    # 3. Obtener contexto de productos
    if db:
        result["product_context"] = _get_product_context(db, query)
    
    # 4. Analizar historial de conversación para contexto
    if conversation_history:
        recent_messages = conversation_history[-5:]  # Últimos 5 mensajes
        conversation_summary = []
        for msg in recent_messages:
            # Manejar tanto objetos como diccionarios
            if isinstance(msg, dict):
                sender = msg.get("sender", "user")
                content = msg.get("content", "")
                conversation_summary.append(f"{sender}: {content}")
            else:
                try:
                    conversation_summary.append(f"{msg.sender}: {msg.content}")
                except AttributeError:
                    # Si falla, intentar como diccionario
                    conversation_summary.append(f"{msg.get('sender', 'user')}: {msg.get('content', '')}")
        result["conversation_context"] = "\n".join(conversation_summary)
    
    # 5. Sugerir acciones basadas en la consulta
    query_lower = query.lower()
    if any(word in query_lower for word in ['comprar', 'comprar', 'precio', 'costo']):
        result["suggested_actions"].append("mostrar_productos")
    if any(word in query_lower for word in ['ayuda', 'soporte', 'problema']):
        result["suggested_actions"].append("contactar_soporte")
    if any(word in query_lower for word in ['información', 'detalles', 'características']):
        result["suggested_actions"].append("proporcionar_informacion")
    
    return result

def create_contextual_prompt(query: str, rag_result: Dict[str, Any], user_context: Dict[str, Any] = None) -> str:
    """
    Crea un prompt contextualizado para el LLM basado en los resultados del RAG
    """
    prompt_parts = []
    
    # Sistema de personalidad
    system_prompt = """Eres un asistente de ventas virtual experto y extremadamente amable para una tienda online. 
    Tu objetivo es ayudar a los clientes de manera profesional, cordial y útil. 
    
    INSTRUCCIONES IMPORTANTES:
    - Siempre mantén un tono amigable, profesional y empático
    - Si no sabes algo, admítelo honestamente y ofrece alternativas
    - Proporciona información precisa y útil sobre productos
    - Sugiere productos relevantes cuando sea apropiado
    - Responde en español de manera natural y conversacional
    - Si hay información sobre productos, úsala para dar respuestas específicas
    - Mantén las respuestas concisas pero informativas
    - Muestra entusiasmo genuino por ayudar al cliente"""
    
    prompt_parts.append(f"SISTEMA: {system_prompt}")
    
    # Contexto de conversación previa
    if rag_result.get("conversation_context"):
        prompt_parts.append(f"CONTEXTO DE CONVERSACIÓN:\n{rag_result['conversation_context']}\n")
    
    # Contexto de productos
    if rag_result.get("product_context"):
        prompt_parts.append(f"INFORMACIÓN DE PRODUCTOS:\n{rag_result['product_context']}\n")
    
    # Contexto de documentos
    if rag_result.get("document_context"):
        prompt_parts.append(f"INFORMACIÓN ADICIONAL:\n{rag_result['document_context']}\n")
    
    # Información del usuario si está disponible
    if user_context:
        if user_context.get("is_logged_in"):
            prompt_parts.append(f"El cliente está registrado y puede hacer pedidos.")
        if user_context.get("previous_orders"):
            prompt_parts.append(f"El cliente tiene historial de compras previas.")
    
    # Menciones de productos específicos
    if rag_result.get("product_mentions"):
        prompt_parts.append(f"El cliente mencionó: {', '.join(rag_result['product_mentions'])}")
    
    # La consulta del usuario
    prompt_parts.append(f"CONSULTA DEL CLIENTE: {query}")
    
    # Instrucciones finales
    prompt_parts.append("""
    Por favor, responde de manera amable y útil. Si el cliente pregunta sobre un producto específico, 
    proporciona información detallada. Si no está seguro, ofrece buscar más información o sugerir 
    productos similares. Siempre mantén un tono profesional y amigable.""")
    
    return "\n\n".join(prompt_parts)
