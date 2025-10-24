"""
Sistema de actualización en tiempo real del carrito
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import json
import asyncio
from datetime import datetime

from app.db import get_db
from app.models import User, Order, OrderItem, Product
from app.security import get_current_user

router = APIRouter(prefix="/realtime", tags=["Real-time Updates"])

# Almacenar conexiones WebSocket activas
active_connections: Dict[int, List[WebSocket]] = {}

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        print(f"✅ Usuario {user_id} conectado para actualizaciones en tiempo real")

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        print(f"❌ Usuario {user_id} desconectado")

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except:
                    # Remover conexión si falla
                    self.active_connections[user_id].remove(connection)

    async def broadcast_to_admins(self, message: str):
        """Enviar mensaje a todos los administradores conectados"""
        for user_id, connections in self.active_connections.items():
            # Aquí podrías verificar si el usuario es admin
            for connection in connections:
                try:
                    await connection.send_text(message)
                except:
                    pass

manager = ConnectionManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """Endpoint WebSocket para actualizaciones en tiempo real"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Mantener conexión viva
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


@router.post("/notify-cart-update")
async def notify_cart_update(
    user_id: int,
    cart_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Notificar actualización del carrito"""
    try:
        message = {
            "type": "cart_update",
            "data": cart_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await manager.send_personal_message(json.dumps(message), user_id)
        
        return {"status": "success", "message": "Notificación enviada"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando notificación: {str(e)}")


@router.post("/notify-order-completed")
async def notify_order_completed(
    order_id: int,
    order_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Notificar que una orden fue completada"""
    try:
        # Obtener información de la orden
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        
        # Notificar al usuario
        user_message = {
            "type": "order_completed",
            "data": {
                "order_id": order.id,
                "total_amount": order.total_amount,
                "status": order.status,
                "items_count": len(order.items)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.send_personal_message(json.dumps(user_message), order.user_id)
        
        # Notificar a administradores
        admin_message = {
            "type": "new_order",
            "data": {
                "order_id": order.id,
                "user_email": order.user.email if order.user else "Usuario desconocido",
                "total_amount": order.total_amount,
                "items_count": len(order.items)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.broadcast_to_admins(json.dumps(admin_message))
        
        return {"status": "success", "message": "Notificaciones enviadas"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando notificaciones: {str(e)}")


@router.post("/notify-stock-update")
async def notify_stock_update(
    product_id: int,
    new_stock: int,
    db: Session = Depends(get_db)
):
    """Notificar actualización de stock"""
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        message = {
            "type": "stock_update",
            "data": {
                "product_id": product.id,
                "product_title": product.title,
                "new_stock": new_stock
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Notificar a todos los usuarios conectados
        await manager.broadcast_to_admins(json.dumps(message))
        
        return {"status": "success", "message": "Notificación de stock enviada"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando notificación: {str(e)}")


@router.get("/active-connections")
async def get_active_connections():
    """Obtener conexiones activas"""
    return {
        "active_connections": len(manager.active_connections),
        "users_connected": list(manager.active_connections.keys())
    }
