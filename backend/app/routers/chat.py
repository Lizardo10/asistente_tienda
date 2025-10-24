from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from ..db import get_db
from .. import models, schemas
from ..security import get_current_admin
from ..services.openai_service import ask_openai, generate_contextual_response, extract_product_recommendations
from ..services.rag_service import rag_answer, advanced_rag_answer

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/message")
def post_message(data: schemas.ChatMessageIn, db: Session = Depends(get_db)):
    """
    Endpoint básico de chat con RAG avanzado por defecto
    """
    try:
        # Guardar mensaje del usuario
        msg = models.ChatMessage(chat_id=data.chat_id, sender="user", content=data.content)
        db.add(msg)
        db.commit()
        db.refresh(msg)

        # Obtener historial de conversación reciente para contexto
        conversation_history = db.query(models.ChatMessage).filter(
            models.ChatMessage.chat_id == data.chat_id
        ).order_by(models.ChatMessage.created_at.desc()).limit(10).all()
        
        # Convertir a formato para el RAG
        history_for_rag = []
        for hist_msg in reversed(conversation_history[:-1]):  # Excluir el mensaje actual
            history_for_rag.append({
                "sender": hist_msg.sender,
                "content": hist_msg.content
            })

        # Usar RAG avanzado por defecto (mejor que el básico)
        rag_result = advanced_rag_answer(data.content, db, history_for_rag)
        
        # Generar respuesta contextualizada
        answer = generate_contextual_response(
            query=data.content,
            context=rag_result,
            conversation_history=history_for_rag
        )
        
        # Extraer recomendaciones de productos
        recommendations = extract_product_recommendations(answer)
        
        # Guardar respuesta del bot
        bot_msg = models.ChatMessage(chat_id=data.chat_id, sender="bot", content=answer)
        db.add(bot_msg)
        db.commit()
        db.refresh(bot_msg)
        
        return {
            "user_message_id": msg.id,
            "bot_message_id": bot_msg.id,
            "response": answer,
            "context": {
                "product_mentions": rag_result.get("product_mentions", []),
                "suggested_actions": rag_result.get("suggested_actions", []),
                "recommendations": recommendations
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando mensaje: {str(e)}")

@router.post("/advanced-message")
def post_advanced_message(data: schemas.ChatAdvancedMessageIn, db: Session = Depends(get_db)):
    """
    Endpoint avanzado que usa RAG mejorado con contexto de productos y conversación
    """
    try:
        # Guardar mensaje del usuario
        msg = models.ChatMessage(chat_id=data.chat_id, sender="user", content=data.message)
        db.add(msg)
        db.commit()
        db.refresh(msg)

        # Obtener historial de conversación reciente
        conversation_history = db.query(models.ChatMessage).filter(
            models.ChatMessage.chat_id == data.chat_id
        ).order_by(models.ChatMessage.created_at.desc()).limit(10).all()
        
        # Convertir a formato para el RAG
        history_for_rag = []
        for hist_msg in reversed(conversation_history[:-1]):  # Excluir el mensaje actual
            history_for_rag.append({
                "sender": hist_msg.sender,
                "content": hist_msg.content
            })

        # Usar RAG avanzado
        rag_result = advanced_rag_answer(data.message, db, history_for_rag)
        
        # Generar respuesta contextualizada
        answer = generate_contextual_response(
            query=data.message,
            context=rag_result,
            conversation_history=history_for_rag
        )
        
        # Extraer recomendaciones de productos
        recommendations = extract_product_recommendations(answer)
        
        # Guardar respuesta del bot
        bot_msg = models.ChatMessage(chat_id=data.chat_id, sender="bot", content=answer)
        db.add(bot_msg)
        db.commit()
        db.refresh(bot_msg)

        return {
            "user_message_id": msg.id,
            "bot_message_id": bot_msg.id,
            "response": answer,
            "context": {
                "product_mentions": rag_result.get("product_mentions", []),
                "suggested_actions": rag_result.get("suggested_actions", []),
                "recommendations": recommendations
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando mensaje: {str(e)}")

@router.get("/history/{chat_id}")
def get_chat_history(chat_id: int, db: Session = Depends(get_db)):
    """
    Obtiene el historial de conversación de un chat específico
    """
    messages = db.query(models.ChatMessage).filter(
        models.ChatMessage.chat_id == chat_id
    ).order_by(models.ChatMessage.created_at.asc()).all()
    
    return {
        "chat_id": chat_id,
        "messages": [
            {
                "id": msg.id,
                "sender": msg.sender,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    }

@router.post("/create")
def create_chat(user_id: int = None, db: Session = Depends(get_db)):
    """
    Crea un nuevo chat
    """
    chat = models.Chat(user_id=user_id, status="open")
    db.add(chat)
    db.commit()
    db.refresh(chat)
    
    return {
        "chat_id": chat.id,
        "status": chat.status,
        "created_at": chat.created_at.isoformat()
    }

# WebSocket endpoint removido - se maneja directamente en main.py
# @router.websocket("/support")
# async def ws_support(websocket: WebSocket, db: Session = Depends(get_db)):
#     await websocket.accept()
#     # Crear chat (anónimo) al conectar
#     chat = models.Chat(status="open")
#     db.add(chat); db.commit(); db.refresh(chat)
#     await websocket.send_json({"type":"chat_opened", "chat_id": chat.id})
#
#     try:
#         while True:
#             data = await websocket.receive_text()
#             
#             # Guardar mensaje del usuario
#             m = models.ChatMessage(chat_id=chat.id, sender="user", content=data)
#             db.add(m); db.commit(); db.refresh(m)
#
#             # Obtener historial de conversación reciente
#             conversation_history = db.query(models.ChatMessage).filter(
#                 models.ChatMessage.chat_id == chat.id
#             ).order_by(models.ChatMessage.created_at.desc()).limit(10).all()
#             
#             # Convertir a formato para el RAG
#             history_for_rag = []
#             for hist_msg in reversed(conversation_history[:-1]):  # Excluir el mensaje actual
#                 history_for_rag.append({
#                     "sender": hist_msg.sender,
#                     "content": hist_msg.content
#                 })
#
#             # Usar RAG avanzado
#             rag_result = advanced_rag_answer(data, db, history_for_rag)
#             
#             # Generar respuesta contextualizada
#             answer = generate_contextual_response(
#                 query=data,
#                 context=rag_result,
#                 conversation_history=history_for_rag
#             )
#
#             # Extraer recomendaciones de productos
#             recommendations = extract_product_recommendations(answer)
#
#             # Guardar respuesta del bot
#             b = models.ChatMessage(chat_id=chat.id, sender="bot", content=answer)
#             db.add(b); db.commit(); db.refresh(b)
#
#             # Enviar respuesta con contexto adicional
#             response_data = {
#                 "type": "bot", 
#                 "message": answer,
#                 "context": {
#                     "product_mentions": rag_result.get("product_mentions", []),
#                     "suggested_actions": rag_result.get("suggested_actions", []),
#                     "recommendations": recommendations
#                 }
#             }
#             
#             await websocket.send_json(response_data)
#     except WebSocketDisconnect:
#         chat.status = "closed"
#         db.commit()
#         return

@router.get("/admin/history", response_model=List[Dict[str, Any]], dependencies=[Depends(get_current_admin)])
def get_chat_history_admin(
    limit: int = 50,
    offset: int = 0,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Obtener historial de chats para administradores.
    Pueden ver todos los chats o filtrar por usuario específico.
    """
    query = db.query(models.Chat)
    
    if user_id:
        query = query.filter(models.Chat.user_id == user_id)
    
    chats = query.order_by(models.Chat.created_at.desc()).offset(offset).limit(limit).all()
    
    result = []
    for chat in chats:
        # Obtener mensajes del chat
        messages = db.query(models.ChatMessage).filter(
            models.ChatMessage.chat_id == chat.id
        ).order_by(models.ChatMessage.created_at.asc()).all()
        
        # Obtener información del usuario si existe
        user_info = None
        if chat.user_id:
            user = db.query(models.User).get(chat.user_id)
            if user:
                user_info = {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "is_admin": user.is_admin
                }
        
        result.append({
            "chat_id": chat.id,
            "user": user_info,
            "is_guest": chat.user_id is None,
            "status": chat.status,
            "created_at": chat.created_at,
            "message_count": len(messages),
            "last_message": messages[-1].content if messages else None,
            "last_message_time": messages[-1].created_at if messages else None
        })
    
    return result

@router.get("/admin/chat/{chat_id}/messages", response_model=List[Dict[str, Any]], dependencies=[Depends(get_current_admin)])
def get_chat_messages_admin(chat_id: int, db: Session = Depends(get_db)):
    """
    Obtener todos los mensajes de un chat específico para administradores.
    """
    chat = db.query(models.Chat).get(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    
    messages = db.query(models.ChatMessage).filter(
        models.ChatMessage.chat_id == chat_id
    ).order_by(models.ChatMessage.created_at.asc()).all()
    
    result = []
    for msg in messages:
        result.append({
            "id": msg.id,
            "sender": msg.sender,
            "content": msg.content,
            "created_at": msg.created_at,
            "user_id": msg.user_id
        })
    
    return result
