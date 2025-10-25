from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str

# Usuarios de ejemplo (en producción usarías una base de datos)
USERS = [
    {
        "id": 1,
        "email": "admin@tienda.com",
        "password": "admin123",
        "full_name": "Administrador",
        "is_admin": True
    },
    {
        "id": 2,
        "email": "usuario@tienda.com",
        "password": "usuario123",
        "full_name": "Usuario Normal",
        "is_admin": False
    }
]

@router.post("/login")
def login(user_data: UserLogin):
    """Endpoint de login simplificado"""
    try:
        # Buscar usuario
        user = next((u for u in USERS if u["email"] == user_data.email and u["password"] == user_data.password), None)
        
        if not user:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        # Generar token simple (en producción usarías JWT)
        token = f"token_{user['id']}_{user['email']}"
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "is_admin": user["is_admin"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en login: {str(e)}")

@router.post("/register")
def register(user_data: UserRegister):
    """Endpoint de registro simplificado"""
    try:
        # Verificar si el usuario ya existe
        existing_user = next((u for u in USERS if u["email"] == user_data.email), None)
        if existing_user:
            raise HTTPException(status_code=400, detail="El usuario ya existe")
        
        # Crear nuevo usuario
        new_user = {
            "id": len(USERS) + 1,
            "email": user_data.email,
            "password": user_data.password,
            "full_name": user_data.full_name,
            "is_admin": False
        }
        
        USERS.append(new_user)
        
        return {
            "message": "Usuario registrado exitosamente",
            "user": {
                "id": new_user["id"],
                "email": new_user["email"],
                "full_name": new_user["full_name"],
                "is_admin": new_user["is_admin"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en registro: {str(e)}")

@router.get("/me")
def get_me(token: str = None):
    """Endpoint para obtener información del usuario actual"""
    try:
        if not token or not token.startswith("token_"):
            raise HTTPException(status_code=401, detail="Token inválido")
        
        # Extraer información del token simple
        parts = token.split("_")
        if len(parts) < 3:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user_id = int(parts[1])
        user_email = parts[2]
        
        # Buscar usuario
        user = next((u for u in USERS if u["id"] == user_id and u["email"] == user_email), None)
        
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
        return {
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "is_admin": user["is_admin"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo usuario: {str(e)}")

@router.get("/health")
def auth_health():
    """Endpoint de salud para auth"""
    return {"status": "ok", "message": "Auth service funcionando"}






















