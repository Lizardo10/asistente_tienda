from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models_sqlmodel.user import User
from app.models_sqlmodel.chat import ChatMessage, ChatMessageCreate
from app.security import get_current_user
from typing import List, Optional
from datetime import datetime
import json

router = APIRouter(prefix="/admin/chat-history", tags=["Chat History"])
public_router = APIRouter(prefix="/chat-history", tags=["Chat History Public"])

@router.get("/conversations")
async def get_all_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener todas las conversaciones de chat (solo admins)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Solo administradores pueden ver el historial de chat")
    
    try:
        # Obtener todas las conversaciones agrupadas por chat_id
        conversations = db.query(ChatMessage).order_by(ChatMessage.created_at.desc()).all()
        
        # Agrupar por chat_id
        conversations_by_id = {}
        for msg in conversations:
            chat_id = str(msg.chat_id) if msg.chat_id else "guest"
            if chat_id not in conversations_by_id:
                conversations_by_id[chat_id] = {
                    "chat_id": chat_id,
                    "user_email": "Usuario Guest",  # No hay campo user_email en la clase existente
                    "user_id": msg.user_id,
                    "messages": [],
                    "last_message": msg.created_at,
                    "message_count": 0
                }
            
            conversations_by_id[chat_id]["messages"].append({
                "id": msg.id,
                "content": msg.content,
                "sender": msg.sender,
                "created_at": msg.created_at.isoformat(),
                "message_type": "text",  # No hay campo message_type en la clase existente
                "message_data": {}  # No hay campo message_data en la clase existente
            })
            conversations_by_id[chat_id]["message_count"] += 1
        
        # Convertir a lista y ordenar por última actividad
        result = list(conversations_by_id.values())
        result.sort(key=lambda x: x["last_message"], reverse=True)
        
        return {
            "success": True,
            "conversations": result,
            "total": len(result)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo conversaciones: {str(e)}")

@router.get("/conversations/{chat_id}")
async def get_conversation_details(
    chat_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener detalles de una conversación específica"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Solo administradores pueden ver el historial de chat")
    
    try:
        messages = db.query(ChatMessage).filter(
            ChatMessage.chat_id == chat_id
        ).order_by(ChatMessage.created_at.asc()).all()
        
        if not messages:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
        conversation_data = {
            "chat_id": chat_id,
            "user_email": "Usuario Guest",
            "user_id": messages[0].user_id,
            "messages": [],
            "created_at": messages[0].created_at.isoformat(),
            "last_activity": messages[-1].created_at.isoformat(),
            "message_count": len(messages)
        }
        
        for msg in messages:
            conversation_data["messages"].append({
                "id": msg.id,
                "content": msg.content,
                "sender": msg.sender,
                "created_at": msg.created_at.isoformat(),
                "message_type": "text",
                "message_data": {}
            })
        
        return {
            "success": True,
            "conversation": conversation_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo conversación: {str(e)}")

@router.delete("/conversations/{chat_id}")
async def delete_conversation(
    chat_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar una conversación específica"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Solo administradores pueden eliminar conversaciones")
    
    try:
        messages = db.query(ChatMessage).filter(ChatMessage.chat_id == chat_id).all()
        
        if not messages:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
        for msg in messages:
            db.delete(msg)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Conversación {chat_id} eliminada exitosamente",
            "deleted_messages": len(messages)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error eliminando conversación: {str(e)}")

@router.get("/stats")
async def get_chat_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener estadísticas de chat"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Solo administradores pueden ver estadísticas")
    
    try:
        # Estadísticas generales
        total_messages = db.query(ChatMessage).count()
        total_conversations = db.query(ChatMessage.chat_id).distinct().count()
        
        # Mensajes por tipo
        user_messages = db.query(ChatMessage).filter(ChatMessage.sender == "user").count()
        bot_messages = db.query(ChatMessage).filter(ChatMessage.sender == "bot").count()
        
        # Conversaciones con usuarios registrados vs guest
        registered_conversations = db.query(ChatMessage).filter(
            ChatMessage.user_id.isnot(None)
        ).distinct(ChatMessage.chat_id).count()
        
        guest_conversations = total_conversations - registered_conversations
        
        return {
            "success": True,
            "stats": {
                "total_messages": total_messages,
                "total_conversations": total_conversations,
                "user_messages": user_messages,
                "bot_messages": bot_messages,
                "registered_conversations": registered_conversations,
                "guest_conversations": guest_conversations,
                "avg_messages_per_conversation": round(total_messages / total_conversations, 2) if total_conversations > 0 else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")

# ==================== ENDPOINTS PÚBLICOS ====================

@public_router.post("/save-message")
async def save_message(
    message_data: dict,
    db: Session = Depends(get_db)
):
    """Guardar mensaje de chat (público para usuarios guest y registrados)"""
    try:
        # Validar datos requeridos
        chat_id = message_data.get('chat_id')
        if not chat_id:
            raise HTTPException(status_code=400, detail="chat_id es requerido")
        
        # Convertir chat_id a int si es string
        try:
            chat_id = int(chat_id)
        except (ValueError, TypeError):
            chat_id = 1  # Valor por defecto
        
        # Verificar si el chat existe, si no, crearlo
        from app.models_sqlmodel.chat import Chat
        existing_chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if not existing_chat:
            # Crear nuevo chat
            new_chat = Chat(
                id=chat_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(new_chat)
            db.commit()
            print(f"✅ Chat {chat_id} creado automáticamente")
        
        # Crear mensaje usando la clase existente
        chat_message = ChatMessage(
            chat_id=chat_id,
            user_id=message_data.get('user_id'),
            sender=message_data.get('sender', 'user'),
            content=message_data.get('content', ''),
            created_at=datetime.utcnow()
        )
        
        db.add(chat_message)
        db.commit()
        db.refresh(chat_message)
        
        return {
            "success": True,
            "message_id": chat_message.id,
            "message": "Mensaje guardado exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error guardando mensaje: {e}")
        raise HTTPException(status_code=500, detail=f"Error guardando mensaje: {str(e)}")

@public_router.get("/conversations/{chat_id}")
async def get_conversation_public(
    chat_id: str,
    db: Session = Depends(get_db)
):
    """Obtener conversación específica (público)"""
    try:
        messages = db.query(ChatMessage).filter(
            ChatMessage.chat_id == chat_id
        ).order_by(ChatMessage.created_at.asc()).all()
        
        if not messages:
            return {
                "success": True,
                "conversation": {
                    "chat_id": chat_id,
                    "messages": []
                }
            }
        
        conversation_data = {
            "chat_id": chat_id,
            "user_email": "Usuario Guest",
            "user_id": messages[0].user_id,
            "messages": [],
            "created_at": messages[0].created_at.isoformat(),
            "last_activity": messages[-1].created_at.isoformat(),
            "message_count": len(messages)
        }
        
        for msg in messages:
            conversation_data["messages"].append({
                "id": msg.id,
                "content": msg.content,
                "sender": msg.sender,
                "created_at": msg.created_at.isoformat(),
                "message_type": "text",
                "message_data": {}
            })
        
        return {
            "success": True,
            "conversation": conversation_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo conversación: {str(e)}")
