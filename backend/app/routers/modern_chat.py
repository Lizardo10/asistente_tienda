"""
Router moderno para el chat con Clean Architecture
Usa tu PostgreSQL y OpenAI originales sin modificarlos
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.db import get_db
from datetime import datetime
from app.use_cases.modern_chat_use_cases import ModernChatUseCases

router = APIRouter(prefix="/modern-chat", tags=["modern-chat"])


@router.post("/create")
async def create_chat_session(db: Session = Depends(get_db)):
    """Crear nueva sesión de chat"""
    try:
        # Crear chat en la base de datos
        from app.models import Chat
        
        chat = Chat(
            created_at=datetime.utcnow()
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)
        
        return {
            "chat_id": chat.id,
            "created_at": chat.created_at,
            "status": "active"
        }
    except Exception as e:
        print(f"Error creando chat: {e}")
        # Devolver ID por defecto si falla
        return {
            "chat_id": 1,
            "created_at": datetime.utcnow(),
            "status": "active"
        }


class ChatMessageRequest(BaseModel):
    """Modelo para el mensaje del chat"""
    message: str
    chat_id: int
    user_id: Optional[int] = None

class ChatMessageResponse(BaseModel):
    """Modelo para la respuesta del chat"""
    user_message_id: Optional[int]
    bot_message_id: int
    response: str
    intent: Dict[str, Any]
    recommendations: list
    confidence: float
    context_used: bool
    timestamp: str

@router.post("/advanced-message", response_model=ChatMessageResponse)
@router.post("/modern-message", response_model=ChatMessageResponse)
async def post_modern_message(
    request: ChatMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint moderno para el chat usando Clean Architecture
    Accesible en /advanced-message y /modern-message
    """
    try:
        # Validar chat_id
        if not request.chat_id or request.chat_id <= 0:
            request.chat_id = 1  # Valor por defecto
        
        print(f"🤖 Procesando mensaje: '{request.message}' para chat {request.chat_id}")
        
        # Usar el sistema RAG real
        use_cases = ModernChatUseCases(db)
        result = await use_cases.process_user_message(
            message=request.message,
            chat_id=request.chat_id,
            user_id=request.user_id
        )
        
        print(f"✅ Respuesta generada: {result['response'][:100]}...")
        
        return ChatMessageResponse(
            user_message_id=result.get('user_message_id'),
            bot_message_id=result.get('bot_message_id', 1),
            response=result['response'],
            intent=result.get('intent', {"type": "general", "confidence": 0.8}),
            recommendations=result.get('recommendations', []),
            confidence=result.get('confidence', 0.8),
            context_used=result.get('context_used', False),
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        print(f"❌ Error procesando mensaje: {e}")
        # Respuesta de fallback si hay error
        return ChatMessageResponse(
            user_message_id=1,
            bot_message_id=2,
            response=f"Lo siento, hubo un error procesando tu mensaje: '{request.message}'. ¿Podrías intentar de nuevo?",
            intent={"type": "error", "confidence": 0.5},
            recommendations=[],
            confidence=0.5,
            context_used=False,
            timestamp=datetime.utcnow().isoformat()
        )

@router.get("/history/{chat_id}")
async def get_chat_history(
    chat_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial del chat
    """
    try:
        chat_use_cases = ModernChatUseCases(db)
        history = await chat_use_cases.get_chat_history(chat_id, limit)
        
        return {
            "chat_id": chat_id,
            "history": history,
            "total_messages": len(history)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo historial: {str(e)}")

@router.post("/create")
async def create_new_chat(
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo chat
    """
    try:
        chat_use_cases = ModernChatUseCases(db)
        result = await chat_use_cases.create_new_chat(
            user_id=None
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando chat: {str(e)}")

@router.websocket("/ws/modern-support")
async def websocket_modern_support(websocket: WebSocket):
    """
    WebSocket moderno para el chat en tiempo real
    """
    await websocket.accept()
    
    try:
        # Enviar mensaje de bienvenida
        await websocket.send_json({
            "type": "welcome",
            "message": "¡Hola! Soy tu asistente moderno. ¿En qué puedo ayudarte?",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
            # Recibir mensaje del usuario
            data = await websocket.receive_json()
            message = data.get("message", "")
            chat_id = data.get("chat_id", 1)
            
            if not message:
                continue
            
            # Procesar mensaje (simplificado para WebSocket)
            response = f"Recibí tu mensaje: '{message}'. Estoy procesando tu consulta..."
            
            # Enviar respuesta
            await websocket.send_json({
                "type": "response",
                "message": response,
                "chat_id": chat_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
    except WebSocketDisconnect:
        print("WebSocket desconectado")
    except Exception as e:
        print(f"Error en WebSocket: {e}")
        await websocket.close()

@router.get("/stats")
async def get_chat_stats(
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas del chat
    """
    try:
        from app.services.modern_cache_service import modern_cache_service
        
        stats = await modern_cache_service.get_cache_stats()
        
        return {
            "cache_stats": stats,
            "user_id": None,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")
