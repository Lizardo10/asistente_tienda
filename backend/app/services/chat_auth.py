"""
Sistema de autorización para el chat WebSocket
"""
from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from ..db import get_db
from .. import models

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "mi-super-secreto-jwt-cambiar-en-produccion")

class ChatAuthorization:
    """Sistema de autorización para el chat"""
    
    @staticmethod
    def verify_user_access(token: Optional[str] = None) -> dict:
        """
        Verifica si el usuario tiene acceso al chat
        Retorna: {"has_access": bool, "user_type": str, "user_id": int}
        """
        # Si no hay token, es un invitado (acceso permitido)
        if not token:
            return {
                "has_access": True,
                "user_type": "guest",
                "user_id": None
            }
        
        try:
            # Decodificar el token JWT
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            user_id = payload.get("sub")
            
            if not user_id:
                return {
                    "has_access": True,
                    "user_type": "guest", 
                    "user_id": None
                }
            
            return {
                "has_access": True,
                "user_type": "user",
                "user_id": int(user_id)
            }
            
        except jwt.ExpiredSignatureError:
            # Token expirado, tratar como invitado
            return {
                "has_access": True,
                "user_type": "guest",
                "user_id": None
            }
        except jwt.InvalidTokenError:
            # Token inválido, tratar como invitado
            return {
                "has_access": True,
                "user_type": "guest",
                "user_id": None
            }
    
    @staticmethod
    def check_user_role(db: Session, user_id: int) -> str:
        """Verifica el rol del usuario en la base de datos"""
        try:
            user = db.query(models.User).filter(models.User.id == user_id).first()
            if user:
                return user.role if hasattr(user, 'role') else "user"
            return "user"
        except Exception:
            return "user"
    
    @staticmethod
    def is_admin_blocked(db: Session, user_id: int) -> bool:
        """Verifica si el usuario es administrador (bloqueado del chat)"""
        if not user_id:
            return False
        
        user_role = ChatAuthorization.check_user_role(db, user_id)
        return user_role == "admin"

async def authorize_chat_connection(websocket: WebSocket, db: Session) -> dict:
    """
    Autoriza la conexión al chat WebSocket
    """
    # Obtener token de los headers o query params
    token = None
    
    # Intentar obtener token de query params
    if websocket.query_params:
        token = websocket.query_params.get("token")
    
    # Intentar obtener token de headers
    if not token:
        headers = dict(websocket.headers)
        auth_header = headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    
    # Verificar acceso
    auth_result = ChatAuthorization.verify_user_access(token)
    
    if not auth_result["has_access"]:
        await websocket.close(code=1008, reason="Acceso denegado al chat")
        raise WebSocketDisconnect("Acceso denegado")
    
    # Si es usuario registrado, verificar que no sea admin
    if auth_result["user_type"] == "user" and auth_result["user_id"]:
        if ChatAuthorization.is_admin_blocked(db, auth_result["user_id"]):
            await websocket.close(code=1008, reason="Los administradores no tienen acceso al chat")
            raise WebSocketDisconnect("Acceso denegado para administradores")
    
    return auth_result

























