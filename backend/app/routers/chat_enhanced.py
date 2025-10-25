"""
Router mejorado para el chat con integración completa de OpenAI, audio e imágenes
Sistema moderno con todas las funcionalidades integradas
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import base64
import logging

from app.db import get_db
from app import models
from app.services.openai_service import advanced_chat_completion, generate_contextual_response
from app.services.audio_service import audio_service
from app.services.huggingface_image_service import huggingface_image_service
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat-enhanced", tags=["Enhanced Chat"])

# Modelos Pydantic
class ChatMessageRequest(BaseModel):
    message: str
    chat_id: int = 1
    user_id: Optional[int] = None
    message_type: str = "text"  # text, audio, image

class ChatMessageResponse(BaseModel):
    success: bool
    message_id: int
    response: str
    message_type: str
    recommendations: List[Dict[str, Any]]
    audio_response: Optional[str] = None  # Base64 audio si se solicita
    image_analysis: Optional[Dict[str, Any]] = None
    timestamp: str

class AudioMessageRequest(BaseModel):
    audio_data: str  # Base64
    chat_id: int = 1
    user_id: Optional[int] = None
    filename: str = "audio.wav"

class ImageMessageRequest(BaseModel):
    image_data: str  # Base64
    chat_id: int = 1
    user_id: Optional[int] = None
    filename: str = "image.jpg"

@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint principal para enviar mensajes de texto al chat
    """
    try:
        logger.info(f"💬 Procesando mensaje: '{request.message[:50]}...'")
        
        # Guardar mensaje del usuario
        user_msg = models.ChatMessage(
            chat_id=request.chat_id,
            sender="user",
            content=request.message,
            message_type=request.message_type
        )
        db.add(user_msg)
        db.commit()
        db.refresh(user_msg)
        
        # Obtener historial de conversación
        conversation_history = db.query(models.ChatMessage).filter(
            models.ChatMessage.chat_id == request.chat_id
        ).order_by(models.ChatMessage.created_at.desc()).limit(10).all()
        
        # Convertir historial para OpenAI
        history_for_ai = []
        for msg in reversed(conversation_history[:-1]):  # Excluir mensaje actual
            history_for_ai.append({
                "role": "user" if msg.sender == "user" else "assistant",
                "content": msg.content
            })
        
        # Generar respuesta usando OpenAI
        messages = [
            {
                "role": "system",
                "content": """Eres una consultora de moda experta y elegante para Asistente Tienda, una tienda online de alta calidad. 
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
                
                PERSONALIDAD:
                - Eres una consultora de moda experta y elegante
                - Te emocionas por ayudar a crear looks perfectos
                - Eres detallista pero no abrumadora
                - Mantienes un aire de sofisticación y profesionalismo
                - Siempre terminas con una invitación amigable para más ayuda"""
            }
        ]
        
        # Agregar historial
        messages.extend(history_for_ai)
        
        # Agregar mensaje actual
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        # Generar respuesta
        ai_result = advanced_chat_completion(
            messages=messages,
            model="gpt-4o-mini",
            temperature=0.8,
            max_tokens=500
        )
        
        if ai_result["success"]:
            response_text = ai_result["response"]
        else:
            response_text = "Lo siento, hubo un error procesando tu mensaje. ¿Podrías intentar de nuevo?"
        
        # Buscar productos mencionados para recomendaciones
        recommendations = await get_product_recommendations(request.message, db)
        
        # Guardar respuesta del bot
        bot_msg = models.ChatMessage(
            chat_id=request.chat_id,
            sender="bot",
            content=response_text,
            message_type="text"
        )
        db.add(bot_msg)
        db.commit()
        db.refresh(bot_msg)
        
        logger.info(f"✅ Respuesta generada exitosamente")
        
        return ChatMessageResponse(
            success=True,
            message_id=bot_msg.id,
            response=response_text,
            message_type="text",
            recommendations=recommendations,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Error procesando mensaje: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/audio", response_model=ChatMessageResponse)
async def send_audio_message(
    request: AudioMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint para procesar mensajes de audio
    """
    try:
        logger.info(f"🎤 Procesando mensaje de audio: {request.filename}")
        
        # Transcribir audio
        transcript = await audio_service.transcribe_base64_audio(
            request.audio_data, 
            request.filename
        )
        
        if not transcript:
            raise HTTPException(
                status_code=503, 
                detail="Servicio de transcripción no disponible. Verifique la configuración de OpenAI."
            )
        
        logger.info(f"✅ Audio transcrito: '{transcript[:50]}...'")
        
        # Procesar como mensaje de texto normal
        text_request = ChatMessageRequest(
            message=transcript,
            chat_id=request.chat_id,
            user_id=request.user_id,
            message_type="audio"
        )
        
        # Usar el endpoint de texto
        response = await send_message(text_request, db)
        
        # Marcar como respuesta de audio
        response.message_type = "audio"
        response.response = f"🎤 Entendí: '{transcript}'\n\n{response.response}"
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error procesando audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/image", response_model=ChatMessageResponse)
async def send_image_message(
    request: ImageMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint para procesar mensajes con imágenes
    """
    try:
        logger.info(f"📸 Procesando mensaje con imagen: {request.filename}")
        
        # Decodificar imagen
        image_data = base64.b64decode(request.image_data)
        
        # Analizar imagen
        analysis = huggingface_image_service.analyze_image(image_data)
        
        if not analysis.get("success", False):
            raise HTTPException(status_code=400, detail="Error analizando la imagen")
        
        image_description = analysis["description"]
        logger.info(f"✅ Imagen analizada: '{image_description[:50]}...'")
        
        # Buscar productos similares
        similar_products = await search_products_by_image_description(image_description, db)
        
        # Generar respuesta contextualizada
        context_message = f"📸 He analizado la imagen: **{image_description}**\n\n"
        
        if similar_products:
            product_names = ", ".join([p["title"] for p in similar_products[:3]])
            context_message += f"✨ Encontré {len(similar_products)} producto(s) similar(es): {product_names}\n\n"
        else:
            context_message += "😔 No encontré productos exactamente iguales en nuestro catálogo, pero puedo ayudarte a buscar algo similar.\n\n"
        
        # Crear mensaje combinado
        combined_message = f"{context_message}¿Te gustaría conocer más detalles sobre algún producto o necesitas ayuda con algo más?"
        
        # Guardar mensaje del usuario (con análisis de imagen)
        user_msg = models.ChatMessage(
            chat_id=request.chat_id,
            sender="user",
            content=f"[IMAGEN] {image_description}",
            message_type="image"
        )
        db.add(user_msg)
        db.commit()
        db.refresh(user_msg)
        
        # Guardar respuesta del bot
        bot_msg = models.ChatMessage(
            chat_id=request.chat_id,
            sender="bot",
            content=combined_message,
            message_type="image"
        )
        db.add(bot_msg)
        db.commit()
        db.refresh(bot_msg)
        
        return ChatMessageResponse(
            success=True,
            message_id=bot_msg.id,
            response=combined_message,
            message_type="image",
            recommendations=similar_products,
            image_analysis={
                "description": image_description,
                "features": analysis.get("features", [])
            },
            timestamp=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error procesando imagen: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/upload-audio")
async def upload_audio_file(
    audio_file: UploadFile = File(...),
    chat_id: int = Form(default=1),
    user_id: Optional[int] = Form(default=None),
    db: Session = Depends(get_db)
):
    """
    Endpoint para subir archivos de audio directamente
    """
    try:
        logger.info(f"🎤 Subiendo archivo de audio: {audio_file.filename}")
        
        # Verificar formato
        if not audio_service.is_supported_format(audio_file.filename or "audio.wav"):
            raise HTTPException(
                status_code=400,
                detail=f"Formato no soportado. Formatos válidos: {audio_service.supported_formats}"
            )
        
        # Leer datos del archivo
        audio_data = await audio_file.read()
        
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Archivo de audio vacío")
        
        # Transcribir
        transcript = await audio_service.transcribe_audio(
            audio_data,
            audio_file.filename or "audio.wav"
        )
        
        if not transcript:
            raise HTTPException(
                status_code=503,
                detail="Servicio de transcripción no disponible"
            )
        
        # Procesar como mensaje de texto
        text_request = ChatMessageRequest(
            message=transcript,
            chat_id=chat_id,
            user_id=user_id,
            message_type="audio"
        )
        
        response = await send_message(text_request, db)
        response.message_type = "audio"
        response.response = f"🎤 Entendí: '{transcript}'\n\n{response.response}"
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error subiendo audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/upload-image")
async def upload_image_file(
    image_file: UploadFile = File(...),
    chat_id: int = Form(default=1),
    user_id: Optional[int] = Form(default=None),
    db: Session = Depends(get_db)
):
    """
    Endpoint para subir archivos de imagen directamente
    """
    try:
        logger.info(f"📸 Subiendo archivo de imagen: {image_file.filename}")
        
        # Verificar que sea imagen
        if not image_file.content_type or not image_file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
        
        # Leer datos del archivo
        image_data = await image_file.read()
        
        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="Archivo de imagen vacío")
        
        # Convertir a base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Procesar como mensaje con imagen
        image_request = ImageMessageRequest(
            image_data=image_base64,
            chat_id=chat_id,
            user_id=user_id,
            filename=image_file.filename or "image.jpg"
        )
        
        return await send_image_message(image_request, db)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error subiendo imagen: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.websocket("/ws/enhanced")
async def websocket_enhanced_chat(websocket: WebSocket):
    """
    WebSocket mejorado para chat en tiempo real con todas las funcionalidades
    """
    await websocket.accept()
    
    try:
        # Enviar mensaje de bienvenida
        await websocket.send_json({
            "type": "welcome",
            "message": "¡Hola! 👋 Soy tu asistente de moda personal. Puedo ayudarte con texto, audio e imágenes. ¿En qué puedo asistirte hoy?",
            "features": {
                "text": True,
                "audio": True,
                "image": True,
                "recommendations": True
            },
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
            # Recibir datos del cliente
            data = await websocket.receive_json()
            message_type = data.get("type", "text")
            
            if message_type == "text":
                # Procesar mensaje de texto
                message = data.get("message", "")
                chat_id = data.get("chat_id", 1)
                
                if not message:
                    continue
                
                # Simular procesamiento (en producción usaría la base de datos)
                response = f"Recibí tu mensaje: '{message}'. Estoy procesando tu consulta..."
                
                await websocket.send_json({
                    "type": "response",
                    "message": response,
                    "message_type": "text",
                    "chat_id": chat_id,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            elif message_type == "audio":
                # Procesar audio
                await websocket.send_json({
                    "type": "processing",
                    "message": "🎤 Procesando tu mensaje de audio...",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Simular transcripción
                await websocket.send_json({
                    "type": "response",
                    "message": "🎤 Entendí tu mensaje de audio. ¿En qué más puedo ayudarte?",
                    "message_type": "audio",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            elif message_type == "image":
                # Procesar imagen
                await websocket.send_json({
                    "type": "processing",
                    "message": "📸 Analizando tu imagen...",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Simular análisis
                await websocket.send_json({
                    "type": "response",
                    "message": "📸 He analizado tu imagen. ¿Te gustaría ver productos similares?",
                    "message_type": "image",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
    except WebSocketDisconnect:
        logger.info("🔌 Cliente desconectado del WebSocket mejorado")
    except Exception as e:
        logger.error(f"❌ Error en WebSocket mejorado: {e}")
        await websocket.close()

# Funciones auxiliares
async def get_product_recommendations(message: str, db: Session) -> List[Dict[str, Any]]:
    """Obtener recomendaciones de productos basadas en el mensaje"""
    try:
        # Buscar productos que coincidan con palabras clave
        products = db.query(models.Product).filter(models.Product.active == True).all()
        
        message_lower = message.lower()
        recommendations = []
        
        for product in products:
            product_text = f"{product.title} {product.description}".lower()
            
            # Buscar coincidencias
            if any(word in product_text for word in message_lower.split() if len(word) > 3):
                recommendations.append({
                    "id": product.id,
                    "title": product.title,
                    "description": product.description,
                    "price": float(product.price),
                    "image_url": product.image_url,
                    "similarity_score": 0.8
                })
        
        return recommendations[:3]  # Máximo 3 recomendaciones
        
    except Exception as e:
        logger.error(f"Error obteniendo recomendaciones: {e}")
        return []

async def search_products_by_image_description(description: str, db: Session) -> List[Dict[str, Any]]:
    """Buscar productos similares basados en descripción de imagen"""
    try:
        products = db.query(models.Product).filter(models.Product.active == True).all()
        
        # Mapeo de tipos de ropa
        clothing_types = {
            "jeans": ["pantalon", "jean", "pants"],
            "pants": ["pantalon", "pants"],
            "shirt": ["camisa", "playera", "polo"],
            "shoes": ["zapato", "zapatos", "calzado", "botas"],
            "boots": ["bota", "botas"],
            "dress": ["vestido"],
            "skirt": ["falda"],
            "jacket": ["chaqueta", "chamarra"],
            "hat": ["gorro", "sombrero"],
            "t-shirt": ["camiseta", "playera"]
        }
        
        desc_lower = description.lower()
        similar_products = []
        
        # Identificar tipo de producto
        product_type_found = None
        for eng_type, spanish_equivalents in clothing_types.items():
            if eng_type in desc_lower:
                product_type_found = spanish_equivalents
                break
        
        # Buscar productos similares
        for product in products:
            product_text = f"{product.title} {product.description}".lower()
            score = 0
            
            if product_type_found:
                for type_word in product_type_found:
                    if type_word in product_text:
                        score += 0.8
            
            # Buscar palabras clave
            keywords = [w for w in desc_lower.split() if len(w) > 3]
            for keyword in keywords:
                if keyword in product_text:
                    score += 0.2
            
            if score >= 0.5:
                similar_products.append({
                    "id": product.id,
                    "title": product.title,
                    "description": product.description,
                    "price": float(product.price),
                    "image_url": product.image_url,
                    "similarity_score": score
                })
        
        # Ordenar por score
        similar_products.sort(key=lambda x: x["similarity_score"], reverse=True)
        return similar_products[:3]
        
    except Exception as e:
        logger.error(f"Error buscando productos por imagen: {e}")
        return []

@router.get("/health")
async def health_check():
    """Verificar estado de los servicios"""
    return {
        "status": "ok",
        "services": {
            "openai": "available" if ai_service.client else "unavailable",
            "audio": "available" if audio_service.openai_client else "unavailable",
            "image": "available" if huggingface_image_service.client else "unavailable"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


