# backend/app/auth_enhanced.py
"""
Sistema de autenticación mejorado con JWT
Incluye refresh tokens, roles, y seguridad avanzada
"""
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from typing import Optional, Dict, Any
import os
import secrets
from enum import Enum

# Configuración mejorada
ALGORITHM = "HS256"
JWT_SECRET = os.getenv("JWT_SECRET", "changeme-super-secret")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))  # 15 min
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))     # 7 días

# Hash robusto
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

class UserRole(str, Enum):
    """Roles de usuario"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"
    SELLER = "seller"

class TokenType(str, Enum):
    """Tipos de token"""
    ACCESS = "access"
    REFRESH = "refresh"

def hash_password(password: str) -> str:
    """Hash seguro de contraseña"""
    if not isinstance(password, str):
        password = str(password)
    return pwd_context.hash(password.strip())

def verify_password(plain: str, hashed: str) -> bool:
    """Verificar contraseña"""
    if not isinstance(plain, str):
        plain = str(plain)
    return pwd_context.verify(plain.strip(), hashed)

def create_access_token(user_id: str, role: str = UserRole.USER) -> str:
    """Crear token de acceso"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": user_id,
        "role": role,
        "type": TokenType.ACCESS,
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(32)  # JWT ID único
    }
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    """Crear token de refresh"""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": user_id,
        "type": TokenType.REFRESH,
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(32)
    }
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

def verify_refresh_token(token: str) -> Optional[str]:
    """Verificar refresh token y devolver user_id"""
    try:
        payload = decode_token(token)
        if payload.get("type") != TokenType.REFRESH:
            return None
        return payload.get("sub")
    except ValueError:
        return None

def decode_token(token: str) -> Dict[str, Any]:
    """Decodificar token con validación mejorada"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        
        # Validar que el token no haya expirado
        if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
            raise JWTError("Token expired")
            
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")

def verify_token_type(token: str, expected_type: TokenType) -> bool:
    """Verificar que el token sea del tipo correcto"""
    try:
        payload = decode_token(token)
        return payload.get("type") == expected_type
    except ValueError:
        return False

def generate_password_reset_token(email: str) -> str:
    """Generar token para reset de contraseña"""
    expire = datetime.utcnow() + timedelta(minutes=30)  # 30 minutos
    to_encode = {
        "email": email,
        "type": "password_reset",
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

def verify_password_reset_token(token: str) -> Optional[str]:
    """Verificar token de reset de contraseña"""
    try:
        payload = decode_token(token)
        if payload.get("type") != "password_reset":
            return None
        return payload.get("email")
    except ValueError:
        return None

# Funciones de validación de roles
def has_role(user_role: str, required_role: str) -> bool:
    """Verificar si el usuario tiene el rol requerido"""
    role_hierarchy = {
        UserRole.USER: 1,
        UserRole.SELLER: 2,
        UserRole.MODERATOR: 3,
        UserRole.ADMIN: 4
    }
    
    user_level = role_hierarchy.get(user_role, 0)
    required_level = role_hierarchy.get(required_role, 0)
    
    return user_level >= required_level

def is_admin(user_role: str) -> bool:
    """Verificar si es administrador"""
    return user_role == UserRole.ADMIN

def is_moderator_or_admin(user_role: str) -> bool:
    """Verificar si es moderador o admin"""
    return user_role in [UserRole.MODERATOR, UserRole.ADMIN]


