"""
Repositorio de chat siguiendo el patrón Repository
Siguiendo el principio de Single Responsibility (SOLID)
"""
from typing import Optional, List
from sqlmodel import Session, select, and_
from .base_repository import BaseRepository
from app.models_sqlmodel.chat import Chat, ChatMessage


class ChatRepository(BaseRepository[Chat]):
    """Repositorio para chats"""
    
    def __init__(self, session: Session):
        super().__init__(session, Chat)
    
    async def get_by_user_id(self, user_id: int) -> List[Chat]:
        """Obtiene chats por usuario"""
        statement = select(Chat).where(Chat.user_id == user_id)
        return self.session.exec(statement).all()
    
    async def get_open_chats(self) -> List[Chat]:
        """Obtiene chats abiertos"""
        statement = select(Chat).where(Chat.status == "open")
        return self.session.exec(statement).all()
    
    async def count_by_status(self, status: str) -> int:
        """Cuenta chats por estado"""
        statement = select(Chat).where(Chat.status == status)
        return len(self.session.exec(statement).all())
    
    async def get_conversation_history(self, chat_id: int, limit: int = 50) -> List[ChatMessage]:
        """Obtiene historial de conversación"""
        statement = (
            select(ChatMessage)
            .where(ChatMessage.chat_id == chat_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        messages = self.session.exec(statement).all()
        return list(reversed(messages))  # Ordenar cronológicamente
    
    async def create_message(self, message_data: dict) -> ChatMessage:
        """Crea un nuevo mensaje"""
        message = ChatMessage(**message_data)
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message
    
    async def get_recent_messages(self, limit: int = 10) -> List[ChatMessage]:
        """Obtiene mensajes recientes"""
        statement = (
            select(ChatMessage)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        return self.session.exec(statement).all()
