# backend/app/routers/auth_complete.py
"""
Router de autenticación completo con todas las funcionalidades avanzadas
Incluye: refresh tokens, MFA, cambio de contraseñas, gestión de perfiles, confirmación de email
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import secrets

from ..database.connection import get_db
from ..models_sqlmodel.user import User
from ..auth_enhanced import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    decode_token, verify_token_type, TokenType, UserRole, has_role,
    verify_refresh_token
)
from ..schemas import LoginRequest, RegisterRequest
from ..security import get_current_user
from ..services.brevo_service import brevo_email_service as email_service
from ..services.mfa_service import MFAService

router = APIRouter(prefix="/auth-complete", tags=["authentication-complete"])

# Esquemas mejorados
from pydantic import BaseModel, EmailStr

class RegistrationResponse(BaseModel):
    message: str
    email_sent: bool
    user: Dict[str, Any]

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

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str

class EmailConfirmationRequest(BaseModel):
    token: str

class MFAEnableRequest(BaseModel):
    code: str

class MFADisableRequest(BaseModel):
    password: str

@router.post("/register", response_model=RegistrationResponse)
async def register_complete(
    data: RegisterRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    request: Request = None
):
    """Registro completo con confirmación de email"""
    
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
    
    # Generar token de confirmación
    confirmation_token = secrets.token_urlsafe(32)
    
    # Crear usuario
    hashed_password = hash_password(data.password)
    user = User(
        email=data.email,
        password_hash=hashed_password,
        full_name=data.full_name,
        role=UserRole.USER,
        active=False,  # Cambiado a False hasta confirmar email
        mfa_enabled=False,
        email_verified=False,
        email_confirmation_token=confirmation_token,
        created_at=datetime.utcnow()
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Enviar email de confirmación en background
    background_tasks.add_task(
        email_service.send_confirmation_email,
        user.email,
        confirmation_token
    )
    
    # NO generar tokens hasta que se confirme el email
    return {
        "message": "Usuario registrado exitosamente. Revisa tu email para confirmar tu cuenta.",
        "email_sent": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "email_verified": user.email_verified,
            "created_at": user.created_at.isoformat()
        }
    }

@router.post("/login", response_model=TokenResponse)
async def login_complete(
    data: LoginRequest,
    db: Session = Depends(get_db),
    request: Request = None
):
    """Login completo con verificación de email"""
    
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
    
    # Verificar si el email está confirmado
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debes confirmar tu email antes de iniciar sesión"
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
            "email_verified": user.email_verified,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token_complete(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Renovar access token usando refresh token"""
    
    # Verificar refresh token
    user_id = verify_refresh_token(data.refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresh inválido"
        )
    
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
            "role": user.role,
            "email_verified": user.email_verified
        }
    )

@router.post("/confirm-email", response_model=TokenResponse)
async def confirm_email(
    data: EmailConfirmationRequest,
    db: Session = Depends(get_db)
):
    """Confirmar email con token y hacer login automático"""
    
    user = db.query(User).filter(
        User.email_confirmation_token == data.token
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de confirmación inválido o expirado"
        )
    
    # Confirmar email
    user.email_verified = True
    user.email_confirmation_token = None
    user.active = True  # Activar cuenta
    db.commit()
    
    # Enviar email de bienvenida en background
    email_service.send_welcome_email(user.email, user.full_name)
    
    # Generar tokens para login automático
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
            "email_verified": user.email_verified,
            "active": user.active,
            "created_at": user.created_at.isoformat()
        }
    )

@router.post("/password-reset-request")
async def password_reset_request(
    data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Solicitar recuperación de contraseña"""
    
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        # Por seguridad, no revelar si el email existe o no
        return {"message": "Si el email existe, recibirás un enlace de recuperación"}
    
    # Generar token de reset
    reset_token = secrets.token_urlsafe(32)
    reset_expires = datetime.utcnow() + timedelta(hours=1)
    
    # Guardar token en la base de datos
    user.password_reset_token = reset_token
    user.password_reset_expires = reset_expires
    db.commit()
    
    # Enviar email de recuperación en background
    background_tasks.add_task(
        email_service.send_password_reset_email,
        user.email,
        reset_token
    )
    
    # Para pruebas: devolver el token en la respuesta
    # En producción, esto debería eliminarse por seguridad
    return {
        "message": "Si el email existe, recibirás un enlace de recuperación",
        "token": reset_token,  # Solo para pruebas
        "expires_in": 3600  # 1 hora
    }

@router.post("/password-reset-confirm")
async def password_reset_confirm(
    data: PasswordResetConfirmRequest,
    db: Session = Depends(get_db)
):
    """Confirmar recuperación de contraseña"""
    
    user = db.query(User).filter(
        User.password_reset_token == data.token,
        User.password_reset_expires > datetime.utcnow()
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de recuperación inválido o expirado"
        )
    
    # Validar nueva contraseña
    if len(data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nueva contraseña debe tener al menos 8 caracteres"
        )
    
    # Actualizar contraseña
    user.password_hash = hash_password(data.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    db.commit()
    
    return {"message": "Contraseña actualizada exitosamente"}

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
        current_user.email_verified = False  # Requerir nueva confirmación
    
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
        "email_verified": current_user.email_verified,
        "mfa_enabled": current_user.mfa_enabled,
        "created_at": current_user.created_at.isoformat(),
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """Logout (en un sistema real, invalidarías el token)"""
    return {"message": "Logout exitoso"}

# Endpoints MFA
@router.post("/mfa/setup")
async def setup_mfa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Configurar MFA"""
    
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA ya está habilitado"
        )
    
    # Generar secreto TOTP
    secret = MFAService.generate_totp_secret()
    
    # Generar QR
    qr_code = MFAService.generate_totp_qr(secret, current_user.email)
    
    # Guardar secreto temporalmente
    current_user.mfa_secret = secret
    db.commit()
    
    return {
        "secret": secret,
        "qr_code": qr_code,
        "manual_entry_key": secret
    }

@router.post("/mfa/enable")
async def enable_mfa(
    data: MFAEnableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Habilitar MFA"""
    
    if not current_user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes configurar MFA primero"
        )
    
    if not MFAService.verify_totp_code(current_user.mfa_secret, data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código inválido"
        )
    
    # Habilitar MFA
    current_user.mfa_enabled = True
    db.commit()
    
    return {"message": "MFA habilitado exitosamente"}

@router.post("/mfa/disable")
async def disable_mfa(
    data: MFADisableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deshabilitar MFA"""
    
    if not verify_password(data.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña incorrecta"
        )
    
    # Deshabilitar MFA
    current_user.mfa_enabled = False
    current_user.mfa_secret = None
    db.commit()
    
    return {"message": "MFA deshabilitado exitosamente"}

@router.get("/mfa/status")
async def get_mfa_status(
    current_user: User = Depends(get_current_user)
):
    """Obtener estado de MFA"""
    return {
        "mfa_enabled": current_user.mfa_enabled,
        "totp_configured": bool(current_user.mfa_secret)
    }
