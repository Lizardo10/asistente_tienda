"""
Sistema de gestión del carrito con limpieza automática
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import json
from datetime import datetime

from app.db import get_db
from app.models import User
from app.security import get_current_user
from app.routers.realtime import manager

router = APIRouter(prefix="/cart", tags=["Cart Management"])


@router.post("/clear")
async def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Limpiar el carrito del usuario
    """
    try:
        # Enviar notificación de carrito limpiado
        cart_clear_message = {
            "type": "cart_cleared",
            "data": {
                "message": "Carrito limpiado manualmente",
                "user_id": current_user.id,
                "timestamp": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await manager.send_personal_message(json.dumps(cart_clear_message), current_user.id)
        
        return {
            "status": "success",
            "message": "Carrito limpiado exitosamente",
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error limpiando carrito: {str(e)}")


@router.post("/clear-after-order")
async def clear_cart_after_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Limpiar el carrito después de una orden completada
    """
    try:
        # Enviar notificación de carrito limpiado después de orden
        cart_clear_message = {
            "type": "cart_cleared",
            "data": {
                "message": "Carrito limpiado después de compra exitosa",
                "order_id": order_id,
                "user_id": current_user.id,
                "timestamp": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await manager.send_personal_message(json.dumps(cart_clear_message), current_user.id)
        
        return {
            "status": "success",
            "message": "Carrito limpiado después de orden",
            "order_id": order_id,
            "user_id": current_user.id
        }
        
    except Exception as e:
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
            "cart_status": "active",
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado del carrito: {str(e)}")
