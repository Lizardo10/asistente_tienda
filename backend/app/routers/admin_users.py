"""
Router para gestión de administradores
Solo administradores pueden crear otros administradores
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from app.db import get_db
from app.models import User
from app.security import get_current_admin
from app.auth_utils import hash_password

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])


@router.post("/create-admin")
async def create_admin(
    email: str,
    password: str,
    full_name: str = "",
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Crear un nuevo administrador (SOLO para administradores)
    """
    try:
        # Verificar que el email no exista
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="El email ya está registrado")
        
        # Crear nuevo administrador
        new_admin = User(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            is_admin=True,
            role="admin",
            active=True,
            email_verified=True,  # Los admins se crean como verificados
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        
        return {
            "status": "success",
            "message": "Administrador creado exitosamente",
            "admin": {
                "id": new_admin.id,
                "email": new_admin.email,
                "full_name": new_admin.full_name,
                "role": new_admin.role,
                "is_admin": new_admin.is_admin,
                "active": new_admin.active,
                "created_at": new_admin.created_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando administrador: {str(e)}")


@router.post("/create-user")
async def create_user(
    email: str,
    password: str,
    full_name: str = "",
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Crear un nuevo usuario normal (SOLO para administradores)
    """
    try:
        # Verificar que el email no exista
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="El email ya está registrado")
        
        # Crear nuevo usuario
        new_user = User(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            is_admin=False,
            role="user",
            active=True,
            email_verified=True,  # Los usuarios creados por admin se verifican automáticamente
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "status": "success",
            "message": "Usuario creado exitosamente",
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "full_name": new_user.full_name,
                "role": new_user.role,
                "is_admin": new_user.is_admin,
                "active": new_user.active,
                "created_at": new_user.created_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando usuario: {str(e)}")


@router.get("/list")
async def list_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Listar todos los usuarios (SOLO para administradores)
    """
    try:
        users = db.query(User).order_by(User.created_at.desc()).all()
        
        return {
            "users": [
                {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "is_admin": user.is_admin,
                    "active": user.active,
                    "email_verified": user.email_verified,
                    "balance": user.balance,
                    "created_at": user.created_at.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None
                }
                for user in users
            ],
            "total": len(users)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando usuarios: {str(e)}")


@router.put("/toggle-admin/{user_id}")
async def toggle_admin_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Cambiar el estado de administrador de un usuario (SOLO para administradores)
    """
    try:
        # No permitir que un admin se quite a sí mismo los permisos
        if user_id == current_admin.id:
            raise HTTPException(status_code=400, detail="No puedes cambiar tu propio estado de administrador")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Cambiar estado de administrador
        user.is_admin = not user.is_admin
        user.role = "admin" if user.is_admin else "user"
        user.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Estado de administrador {'activado' if user.is_admin else 'desactivado'}",
            "user": {
                "id": user.id,
                "email": user.email,
                "is_admin": user.is_admin,
                "role": user.role
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cambiando estado de administrador: {str(e)}")


@router.put("/toggle-active/{user_id}")
async def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Activar/desactivar un usuario (SOLO para administradores)
    """
    try:
        # No permitir que un admin se desactive a sí mismo
        if user_id == current_admin.id:
            raise HTTPException(status_code=400, detail="No puedes desactivar tu propia cuenta")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Cambiar estado activo
        user.active = not user.active
        user.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Usuario {'activado' if user.active else 'desactivado'}",
            "user": {
                "id": user.id,
                "email": user.email,
                "active": user.active
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cambiando estado del usuario: {str(e)}")


@router.get("/admins")
async def list_admins(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Listar solo administradores (SOLO para administradores)
    """
    try:
        admins = db.query(User).filter(User.is_admin == True).order_by(User.created_at.desc()).all()
        
        return {
            "admins": [
                {
                    "id": admin.id,
                    "email": admin.email,
                    "full_name": admin.full_name,
                    "active": admin.active,
                    "email_verified": admin.email_verified,
                    "created_at": admin.created_at.isoformat(),
                    "last_login": admin.last_login.isoformat() if admin.last_login else None
                }
                for admin in admins
            ],
            "total": len(admins)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando administradores: {str(e)}")









