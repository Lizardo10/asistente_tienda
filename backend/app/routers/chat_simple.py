from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatMessageIn(BaseModel):
    message: str
    chat_id: int = 1

@router.post("/advanced-message")
def post_advanced_message(data: ChatMessageIn):
    """
    Endpoint de chat simplificado que funciona sin base de datos
    """
    try:
        message = data.message.lower()
        
        # Respuestas predefinidas basadas en palabras clave
        if any(word in message for word in ["hola", "hello", "hi", "buenos"]):
            response = "¡Hola! Soy tu asistente de tienda. ¿En qué puedo ayudarte hoy?"
            suggested_products = []
        elif any(word in message for word in ["laptop", "computadora", "ordenador"]):
            response = "Tenemos excelentes laptops gaming disponibles. La Laptop Gaming tiene un precio de $1,299.99 y está perfecta para gaming y trabajo profesional."
            suggested_products = [{
                "id": 1,
                "title": "Laptop Gaming",
                "name": "Laptop Gaming",
                "description": "Laptop para gaming de alta gama",
                "price": 1299.99,
                "stock": 10,
                "active": True,
                "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=300&fit=crop"
            }]
        elif any(word in message for word in ["smartphone", "teléfono", "celular", "móvil"]):
            response = "Tenemos el Smartphone Pro disponible por $899.99. Es un dispositivo con cámara profesional y excelente rendimiento."
            suggested_products = [{
                "id": 2,
                "title": "Smartphone Pro",
                "name": "Smartphone Pro",
                "description": "Smartphone con cámara profesional",
                "price": 899.99,
                "stock": 25,
                "active": True,
                "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=300&fit=crop"
            }]
        elif any(word in message for word in ["auriculares", "audífonos", "headphones"]):
            response = "Los Auriculares Wireless están disponibles por $299.99. Tienen cancelación de ruido y son perfectos para música y llamadas."
            suggested_products = [{
                "id": 3,
                "title": "Auriculares Wireless",
                "name": "Auriculares Wireless",
                "description": "Auriculares inalámbricos con cancelación de ruido",
                "price": 299.99,
                "stock": 50,
                "active": True,
                "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=300&fit=crop"
            }]
        elif any(word in message for word in ["precio", "coste", "cuesta", "vale"]):
            response = "Te ayudo con los precios: Laptop Gaming $1,299.99, Smartphone Pro $899.99, y Auriculares Wireless $299.99. ¿Te interesa algún producto específico?"
            suggested_products = []
        elif any(word in message for word in ["productos", "catálogo", "inventario"]):
            response = "Tenemos 3 productos disponibles: Laptop Gaming ($1,299.99), Smartphone Pro ($899.99), y Auriculares Wireless ($299.99). ¿Quieres saber más sobre alguno?"
            suggested_products = []
        elif any(word in message for word in ["ayuda", "help", "soporte"]):
            response = "Estoy aquí para ayudarte con información sobre productos, precios, disponibilidad y más. ¿Qué necesitas saber?"
            suggested_products = []
        else:
            response = "Entiendo tu consulta. ¿Podrías ser más específico? Puedo ayudarte con información sobre productos, precios, o cualquier otra pregunta sobre nuestra tienda."
            suggested_products = []

        return {
            "response": response,
            "suggested_products": suggested_products,
            "context": {
                "product_mentions": [],
                "suggested_actions": [],
                "recommendations": suggested_products
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando mensaje: {str(e)}")

@router.get("/health")
def chat_health():
    """Endpoint de salud para el chat"""
    return {"status": "ok", "message": "Chat service funcionando"}






















