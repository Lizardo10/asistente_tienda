"""
Casos de uso para usuarios siguiendo Clean Architecture
Siguiendo el principio de Single Responsibility (SOLID)
"""
from typing import Dict, Any, Optional
from datetime import datetime
from app.models_sqlmodel.user import User, UserCreate, UserUpdate
from app.repositories.user_repository import UserRepository
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.core.config import settings

# Configuración de hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserUseCases:
    """Casos de uso para usuarios"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Crea un nuevo usuario"""
        # Verificar si el email ya existe
        existing_user = await self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("El email ya está registrado")
        
        # Hash de la contraseña
        password_hash = pwd_context.hash(user_data.password)
        
        # Crear usuario
        user_dict = user_data.dict()
        user_dict["password_hash"] = password_hash
        del user_dict["password"]  # No guardar contraseña en texto plano
        
        return await self.user_repository.create(user_dict)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Autentica un usuario"""
        user = await self.user_repository.get_by_email(email)
        if not user:
            return None
        
        if not pwd_context.verify(password, user.password_hash):
            return None
        
        # Actualizar último login
        await self.user_repository.update_last_login(user.id)
        
        return user
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Obtiene usuario por ID"""
        return await self.user_repository.get(user_id)
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Actualiza un usuario"""
        update_data = user_data.dict(exclude_unset=True)
        
        # Si se actualiza la contraseña, hacer hash
        if "password" in update_data:
            update_data["password_hash"] = pwd_context.hash(update_data["password"])
            del update_data["password"]
        
        return await self.user_repository.update(user_id, update_data)
    
    async def delete_user(self, user_id: int) -> bool:
        """Elimina un usuario"""
        return await self.user_repository.delete(user_id)
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Obtiene todos los usuarios con paginación"""
        return await self.user_repository.get_multi(skip, limit)
    
    async def get_admins(self) -> list[User]:
        """Obtiene todos los administradores"""
        return await self.user_repository.get_admins()
    
    async def promote_to_admin(self, user_id: int) -> Optional[User]:
        """Promueve un usuario a administrador"""
        return await self.user_repository.update(user_id, {
            "is_admin": True,
            "role": "admin"
        })
    
    async def demote_from_admin(self, user_id: int) -> Optional[User]:
        """Degrada un administrador a usuario normal"""
        return await self.user_repository.update(user_id, {
            "is_admin": False,
            "role": "user"
        })
    
    def create_access_token(self, user: User) -> str:
        """Crea token JWT para el usuario"""
        to_encode = {
            "sub": str(user.id),
            "email": user.email,
            "is_admin": user.is_admin,
            "role": user.role,
            "exp": datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
        }
        
        return jwt.encode(to_encode, settings.jwt_secret, algorithm="HS256")
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifica un token JWT"""
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
            return payload
        except JWTError:
            return None
