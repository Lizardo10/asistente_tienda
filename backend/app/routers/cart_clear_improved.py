"""
Sistema de limpieza del carrito mejorado
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import json
from datetime import datetime

from app.db import get_db
from app.models import User
from app.security import get_current_user
from app.routers.realtime import manager

router = APIRouter(prefix="/cart", tags=["Cart Management"])


@router.post("/clear-after-payment")
async def clear_cart_after_payment(
    order_id: int,
    user_email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Limpiar el carrito después de un pago exitoso
    """
    try:
        print(f"🛒 Limpiando carrito para usuario {current_user.email} después de orden #{order_id}")
        
        # Enviar notificación de carrito limpiado
        cart_clear_message = {
            "type": "cart_cleared",
            "data": {
                "message": "Carrito limpiado después de compra exitosa",
                "order_id": order_id,
                "user_email": user_email,
                "user_id": current_user.id,
                "timestamp": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Enviar a todos los usuarios conectados (para que el frontend lo reciba)
        await manager.broadcast_to_admins(json.dumps(cart_clear_message))
        
        # También enviar específicamente al usuario
        await manager.send_personal_message(json.dumps(cart_clear_message), current_user.id)
        
        print(f"✅ Notificación de limpieza de carrito enviada para orden #{order_id}")
        
        return {
            "status": "success",
            "message": "Carrito limpiado después de compra exitosa",
            "order_id": order_id,
            "user_email": user_email,
            "user_id": current_user.id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error limpiando carrito: {e}")
        raise HTTPException(status_code=500, detail=f"Error limpiando carrito: {str(e)}")


@router.post("/force-clear")
async def force_clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Forzar limpieza del carrito (para pruebas)
    """
    try:
        print(f"🛒 Forzando limpieza de carrito para usuario {current_user.email}")
        
        # Enviar notificación de carrito limpiado
        cart_clear_message = {
            "type": "cart_cleared",
            "data": {
                "message": "Carrito limpiado manualmente",
                "user_email": current_user.email,
                "user_id": current_user.id,
                "timestamp": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Enviar notificación
        await manager.send_personal_message(json.dumps(cart_clear_message), current_user.id)
        
        print(f"✅ Carrito limpiado forzadamente para usuario {current_user.email}")
        
        return {
            "status": "success",
            "message": "Carrito limpiado manualmente",
            "user_email": current_user.email,
            "user_id": current_user.id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error limpiando carrito: {e}")
        raise HTTPException(status_code=500, detail=f"Error limpiando carrito: {str(e)}")


@router.get("/status")
async def get_cart_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener estado del carrito
    """
    try:
        return {
            "user_id": current_user.id,
            "user_email": current_user.email,
            "cart_status": "active",
            "last_updated": datetime.utcnow().isoformat(),
            "message": "Carrito activo - esperando limpieza después de compra"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado del carrito: {str(e)}")









