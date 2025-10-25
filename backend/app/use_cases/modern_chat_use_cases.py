"""
Casos de uso modernos para el chat con Clean Architecture
Usa tu PostgreSQL y OpenAI originales sin modificarlos
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.models import Chat, ChatMessage
from app.services.modern_ai_service import modern_ai_service
from app.services.modern_cache_service import modern_cache_service
from app.db import get_db
from sqlalchemy.orm import Session

class IModernChatUseCases(ABC):
    """Interface para los casos de uso del chat moderno - Dependency Inversion Principle"""
    
    @abstractmethod
    async def process_user_message(self, message: str, chat_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def get_chat_history(self, chat_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def create_new_chat(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        pass

class ModernChatUseCases(IModernChatUseCases):
    """Implementación moderna de los casos de uso del chat"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def process_user_message(self, message: str, chat_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Procesa un mensaje del usuario usando Clean Architecture
        """
        try:
            # 1. Guardar mensaje del usuario en tu PostgreSQL
            user_message = ChatMessage(
                chat_id=chat_id,
                sender="user",
                content=message
            )
            self.db.add(user_message)
            self.db.commit()
            self.db.refresh(user_message)
            
            # 2. Obtener contexto del chat
            context = await self._get_chat_context(chat_id, user_id)
            
            # 3. Usar tu API de OpenAI para generar respuesta
            ai_response = await modern_ai_service.generate_smart_response(message, context)
            
            # 4. Guardar respuesta del bot en tu PostgreSQL
            bot_message = ChatMessage(
                chat_id=chat_id,
                sender="bot",
                content=ai_response["response"]
            )
            self.db.add(bot_message)
            self.db.commit()
            self.db.refresh(bot_message)
            
            # 5. Cachear recomendaciones si las hay
            if ai_response.get("recommendations"):
                await modern_cache_service.cache_product_recommendations(
                    str(user_id or "anonymous"),
                    ai_response["recommendations"]
                )
            
            # 6. Retornar respuesta estructurada
            return {
                "user_message_id": user_message.id,
                "bot_message_id": bot_message.id,
                "response": ai_response["response"],
                "intent": ai_response.get("intent", {}),
                "recommendations": ai_response.get("recommendations", []),
                "confidence": ai_response.get("confidence", 0.8),
                "context_used": ai_response.get("context_used", False),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Fallback a respuesta simple
            fallback_response = f"Lo siento, hubo un error procesando tu mensaje. Por favor intenta de nuevo."
            
            bot_message = ChatMessage(
                chat_id=chat_id,
                sender="bot",
                content=fallback_response
            )
            self.db.add(bot_message)
            self.db.commit()
            self.db.refresh(bot_message)
            
            return {
                "user_message_id": None,
                "bot_message_id": bot_message.id,
                "response": fallback_response,
                "intent": {"type": "error", "confidence": 0.0},
                "recommendations": [],
                "confidence": 0.0,
                "context_used": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_chat_history(self, chat_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene el historial del chat desde tu PostgreSQL
        """
        try:
            messages = self.db.query(ChatMessage).filter(
                ChatMessage.chat_id == chat_id
            ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": msg.id,
                    "sender": msg.sender,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in reversed(messages)
            ]
            
        except Exception as e:
            return []
    
    async def create_new_chat(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Crea un nuevo chat en tu PostgreSQL
        """
        try:
            new_chat = Chat(user_id=user_id)
            self.db.add(new_chat)
            self.db.commit()
            self.db.refresh(new_chat)
            
            return {
                "chat_id": new_chat.id,
                "user_id": user_id,
                "created_at": new_chat.created_at.isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_chat_context(self, chat_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Obtiene el contexto del chat para la IA
        """
        try:
            # Obtener historial reciente
            history = await self.get_chat_history(chat_id, limit=5)
            
            # Obtener sesión del usuario del cache
            user_session = None
            if user_id:
                user_session = await modern_cache_service.get_user_session(str(user_id))
            
            # Obtener recomendaciones del cache
            recommendations = []
            if user_id:
                recommendations = await modern_cache_service.get_product_recommendations(str(user_id)) or []
            
            return {
                "chat_id": chat_id,
                "user_id": user_id,
                "history": history,
                "user_session": user_session,
                "recommendations": recommendations,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "chat_id": chat_id,
                "user_id": user_id,
                "history": [],
                "user_session": None,
                "recommendations": [],
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }






















