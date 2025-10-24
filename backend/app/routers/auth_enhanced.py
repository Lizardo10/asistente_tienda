# backend/app/routers/auth_enhanced.py
"""
Router de autenticación mejorado con refresh tokens y gestión de roles
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import secrets

from ..database.connection import get_db
from ..models_sqlmodel.user import User
from ..auth_enhanced import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    decode_token, verify_token_type, TokenType, UserRole, has_role
)
from ..schemas import LoginRequest, RegisterRequest
from ..security import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])

# Esquemas mejorados
from pydantic import BaseModel, EmailStr

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class UpdateProfileRequest(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None

@router.post("/register", response_model=TokenResponse)
async def register_enhanced(
    data: RegisterRequest, 
    db: Session = Depends(get_db),
    request: Request = None
):
    """Registro mejorado con validaciones adicionales"""
    
    # Verificar si el email ya existe
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Validar fortaleza de contraseña
    if len(data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 8 caracteres"
        )
    
    # Crear usuario
    hashed_password = hash_password(data.password)
    user = User(
        email=data.email,
        password_hash=hashed_password,
        full_name=data.full_name,
        role=UserRole.USER,
        active=True,
        mfa_enabled=False,
        created_at=datetime.utcnow()
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generar tokens
    access_token = create_access_token(str(user.id), user.role)
    refresh_token = create_refresh_token(str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=15 * 60,  # 15 minutos
        user={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "created_at": user.created_at.isoformat()
        }
    )

@router.post("/login", response_model=TokenResponse)
async def login_enhanced(
    data: LoginRequest,
    db: Session = Depends(get_db),
    request: Request = None
):
    """Login mejorado con refresh tokens"""
    
    # Buscar usuario
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    # Verificar si el usuario está activo
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cuenta desactivada"
        )
    
    # Actualizar último login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Generar tokens
    access_token = create_access_token(str(user.id), user.role)
    refresh_token = create_refresh_token(str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=15 * 60,  # 15 minutos
        user={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Renovar access token usando refresh token"""
    
    try:
        # Verificar refresh token
        if not verify_token_type(data.refresh_token, TokenType.REFRESH):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresh inválido"
            )
        
        payload = decode_token(data.refresh_token)
        user_id = payload.get("sub")
        
        # Buscar usuario
        user = db.query(User).get(int(user_id))
        if not user or not user.active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado o inactivo"
            )
        
        # Generar nuevo access token
        access_token = create_access_token(str(user.id), user.role)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=data.refresh_token,  # Mantener el mismo refresh token
            expires_in=15 * 60,
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}"
        )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """Logout (en un sistema real, invalidarías el token)"""
    return {"message": "Logout exitoso"}

@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cambiar contraseña"""
    
    # Verificar contraseña actual
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )
    
    # Validar nueva contraseña
    if len(data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nueva contraseña debe tener al menos 8 caracteres"
        )
    
    # Actualizar contraseña
    current_user.password_hash = hash_password(data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Contraseña actualizada exitosamente"}

@router.put("/profile")
async def update_profile(
    data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar perfil de usuario"""
    
    # Verificar si el nuevo email ya existe
    if data.email and data.email != current_user.email:
        existing_user = db.query(User).filter(User.email == data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está en uso"
            )
        current_user.email = data.email
    
    if data.full_name:
        current_user.full_name = data.full_name
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Perfil actualizado exitosamente"}

@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Obtener información del usuario actual"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "active": current_user.active,
        "created_at": current_user.created_at.isoformat(),
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }
