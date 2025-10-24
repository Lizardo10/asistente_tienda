"""
Repositorio de usuarios siguiendo el patrón Repository
Siguiendo el principio de Single Responsibility (SOLID)
"""
from typing import Optional, List
from sqlmodel import Session, select
from .base_repository import BaseRepository
from app.models_sqlmodel.user import User


class UserRepository(BaseRepository[User]):
    """Repositorio para usuarios"""
    
    def __init__(self, session: Session):
        super().__init__(session, User)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene usuario por email"""
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()
    
    async def get_admins(self) -> List[User]:
        """Obtiene todos los administradores"""
        statement = select(User).where(User.is_admin == True)
        return self.session.exec(statement).all()
    
    async def get_by_role(self, role: str) -> List[User]:
        """Obtiene usuarios por rol"""
        statement = select(User).where(User.role == role)
        return self.session.exec(statement).all()
    
    async def update_last_login(self, user_id: int) -> Optional[User]:
        """Actualiza el último login del usuario"""
        from datetime import datetime
        return await self.update(user_id, {"updated_at": datetime.utcnow()})
