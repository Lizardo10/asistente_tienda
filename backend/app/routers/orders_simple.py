from fastapi import APIRouter, HTTPException, Header
from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/orders", tags=["orders"])

class OrderItem(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItem]

# Órdenes de ejemplo (en producción usarías una base de datos)
ORDERS = [
    {
        "id": 1,
        "user_id": 2,
        "total": 1299.99,
        "status": "completed",
        "created_at": "2024-01-15T10:30:00",
        "items": [
            {
                "id": 1,
                "product_id": 1,
                "quantity": 1,
                "product": {
                    "id": 1,
                    "name": "Laptop Gaming",
                    "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=300&fit=crop"
                }
            }
        ]
    }
]

@router.post("")
def create_order(order_data: OrderCreate, authorization: str = Header(None)):
    """Crear una nueva orden"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de autorización requerido")
        
        token = authorization.split(" ")[1]
        
        # Extraer información del token simple
        parts = token.split("_")
        if len(parts) < 3:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user_id = int(parts[1])
        
        # Crear nueva orden
        new_order = {
            "id": len(ORDERS) + 1,
            "user_id": user_id,
            "total": sum(item.quantity * 100 for item in order_data.items),  # Precio simulado
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "items": [
                {
                    "id": i + 1,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "product": {
                        "id": item.product_id,
                        "name": f"Producto {item.product_id}",
                        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=300&fit=crop"
                    }
                }
                for i, item in enumerate(order_data.items)
            ]
        }
        
        ORDERS.append(new_order)
        
        return {
            "message": "Orden creada exitosamente",
            "order": new_order
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando orden: {str(e)}")

@router.get("/my")
def get_my_orders(authorization: str = Header(None)):
    """Obtener órdenes del usuario actual"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de autorización requerido")
        
        token = authorization.split(" ")[1]
        
        # Extraer información del token simple
        parts = token.split("_")
        if len(parts) < 3:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user_id = int(parts[1])
        
        # Filtrar órdenes del usuario
        user_orders = [order for order in ORDERS if order["user_id"] == user_id]
        
        return user_orders
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo órdenes: {str(e)}")

@router.get("")
def get_all_orders(authorization: str = Header(None)):
    """Obtener todas las órdenes (solo admin)"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de autorización requerido")
        
        token = authorization.split(" ")[1]
        
        # Extraer información del token simple
        parts = token.split("_")
        if len(parts) < 3:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user_email = parts[2]
        
        # Verificar si es admin
        if user_email != "admin@tienda.com":
            raise HTTPException(status_code=403, detail="Acceso denegado")
        
        return ORDERS
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo órdenes: {str(e)}")

@router.get("/{order_id}")
def get_order_detail(order_id: int, authorization: str = Header(None)):
    """Obtener detalles de una orden específica"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token de autorización requerido")
        
        token = authorization.split(" ")[1]
        
        # Extraer información del token simple
        parts = token.split("_")
        if len(parts) < 3:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user_id = int(parts[1])
        
        # Buscar orden
        order = next((o for o in ORDERS if o["id"] == order_id), None)
        
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        
        # Verificar permisos
        if order["user_id"] != user_id and parts[2] != "admin@tienda.com":
            raise HTTPException(status_code=403, detail="Acceso denegado")
        
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo orden: {str(e)}")

@router.get("/health")
def orders_health():
    """Endpoint de salud para órdenes"""
    return {"status": "ok", "message": "Orders service funcionando"}













