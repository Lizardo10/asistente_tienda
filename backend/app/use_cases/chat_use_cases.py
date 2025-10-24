"""
Casos de uso para el chat siguiendo Clean Architecture
Siguiendo el principio de Single Responsibility (SOLID)
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.models_sqlmodel.chat import Chat, ChatMessage, ChatCreate, ChatMessageCreate
from app.repositories.chat_repository import ChatRepository
from app.services.ai_service import ai_service
from app.services.rag_service import advanced_rag_answer
from app.services.openai_service import generate_contextual_response
from app.database.connection import get_db
from app.services.simple_cache_service import cache_service


class ChatUseCases:
    """Casos de uso para el chat"""
    
    def __init__(self, chat_repository: ChatRepository):
        self.chat_repository = chat_repository
    
    async def create_chat(self, user_id: Optional[int] = None) -> Chat:
        """Crea un nuevo chat"""
        chat_data = ChatCreate(user_id=user_id)
        return await self.chat_repository.create(chat_data.dict())
    
    async def send_message(self, chat_id: int, content: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Envía un mensaje y genera respuesta del bot"""
        # Guardar mensaje del usuario
        user_message_data = ChatMessageCreate(
            chat_id=chat_id,
            sender="user",
            content=content,
            user_id=user_id
        )
        user_message = await self.chat_repository.create_message(user_message_data.dict())
        
        # Obtener historial de conversación
        conversation_history = await self.chat_repository.get_conversation_history(chat_id)
        
        # Obtener contexto RAG con productos de la base de datos
        db = next(get_db())
        
        # Convertir historial al formato que espera el RAG
        history_for_rag = []
        if conversation_history:
            for hist_msg in conversation_history:
                if hasattr(hist_msg, 'sender') and hasattr(hist_msg, 'content'):
                    history_for_rag.append({
                        "sender": hist_msg.sender,
                        "content": hist_msg.content
                    })
        
        # Usar RAG avanzado para obtener contexto real de productos
        rag_result = advanced_rag_answer(content, db, conversation_history)
        
        # Generar respuesta contextual usando OpenAI con el contexto RAG
        ai_response_text = generate_contextual_response(content, rag_result, conversation_history)
        
        # Analizar intención
        intent_analysis = await ai_service.analyze_intent(content)
        
        # Guardar respuesta del bot
        bot_message_data = ChatMessageCreate(
            chat_id=chat_id,
            sender="bot",
            content=ai_response_text,
            user_id=None
        )
        bot_message = await self.chat_repository.create_message(bot_message_data.dict())
        
        # Extraer recomendaciones
        recommendations = await ai_service.extract_recommendations(ai_response_text)
        
        return {
            "user_message": user_message,
            "bot_message": bot_message,
            "response": ai_response_text,
            "context": {
                "intent": intent_analysis,
                "recommendations": recommendations,
                "usage": {"total_tokens": 0}  # Placeholder
            }
        }
    
    async def get_chat_history(self, chat_id: int, limit: int = 50) -> List[ChatMessage]:
        """Obtiene el historial de chat"""
        return await self.chat_repository.get_conversation_history(chat_id, limit)
    
    async def close_chat(self, chat_id: int) -> bool:
        """Cierra un chat"""
        return await self.chat_repository.update(chat_id, {"status": "closed"})
    
    async def get_user_chats(self, user_id: int) -> List[Chat]:
        """Obtiene los chats de un usuario"""
        return await self.chat_repository.get_by_user_id(user_id)
    
    async def get_chat_analytics(self) -> Dict[str, Any]:
        """Obtiene analytics del chat"""
        total_chats = await self.chat_repository.count()
        open_chats = await self.chat_repository.count_by_status("open")
        closed_chats = await self.chat_repository.count_by_status("closed")
        
        # Obtener estadísticas de cache
        cache_stats = await cache_service.get_cache_stats()
        
        return {
            "total_chats": total_chats,
            "open_chats": open_chats,
            "closed_chats": closed_chats,
            "cache_stats": cache_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
