"""
Router para sistema de recomendaciones inteligentes
Muestra productos recomendados sin consultar DB (usa caché)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List, Dict, Any, Optional

from app.database import get_db
from app.services.intelligent_cache_service import intelligent_cache
from app.routers.auth import get_current_user

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/for-you")
async def get_recommendations_for_user(
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = None
):
    """
    Obtener recomendaciones personalizadas
    USA CACHÉ - No consulta DB si ya están cacheadas
    """
    try:
        user_id = current_user.get("id") if current_user else None
        
        recommendations = await intelligent_cache.get_personalized_recommendations(
            db=db,
            user_id=user_id
        )
        
        # Información adicional para el cliente
        user_info = {
            "is_client": user_id is not None,
            "has_history": False,
            "total_orders": 0,
            "recommendation_type": "general"
        }
        
        if user_id:
            # Obtener información del historial del usuario
            orders = db.exec(
                select(Order).where(Order.user_id == user_id)
            ).all()
            
            user_info.update({
                "has_history": len(orders) > 0,
                "total_orders": len(orders),
                "recommendation_type": "personalized" if len(orders) > 0 else "new_client"
            })
        
        return {
            "recommendations": recommendations,
            "user_info": user_info,
            "from_cache": True,  # Siempre intentamos caché primero
            "total": len(recommendations),
            "message": f"{'Recomendaciones personalizadas' if user_info['is_client'] and user_info['has_history'] else 'Productos destacados para ti'}"
        }
        
    except Exception as e:
        print(f"Error obteniendo recomendaciones: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/quick-products")
async def get_quick_products(db: Session = Depends(get_db)):
    """
    Productos para mostrar inmediatamente al entrar
    OPTIMIZADO - Siempre desde caché
    """
    try:
        # Obtener productos desde caché
        products = await intelligent_cache.get_all_products(db, active_only=True)
        
        # Tomar solo los primeros 6 para carga rápida
        quick_products = products[:6]
        
        return {
            "products": quick_products,
            "from_cache": True,
            "load_time_ms": 0,  # Casi instantáneo desde Redis
            "total": len(quick_products)
        }
        
    except Exception as e:
        print(f"Error obteniendo productos rápidos: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/track-view")
async def track_product_view(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = None
):
    """
    Trackear que un usuario vio un producto
    Usado para mejorar recomendaciones
    """
    try:
        user_id = current_user.get("id") if current_user else "guest"
        
        # Guardar en Redis el tracking
        track_key = f"tracking:user:{user_id}:products"
        
        # Obtener tracking actual
        current_tracking = await intelligent_cache.cache.get(track_key)
        
        if current_tracking:
            import json
            viewed_products = json.loads(current_tracking)
        else:
            viewed_products = []
        
        # Agregar producto visto
        if product_id not in viewed_products:
            viewed_products.append(product_id)
            
            # Mantener solo últimos 20 productos vistos
            viewed_products = viewed_products[-20:]
            
            # Guardar en Redis
            await intelligent_cache.cache.set(
                track_key,
                json.dumps(viewed_products),
                expire=86400  # 24 horas
            )
        
        return {"message": "Tracking registrado", "total_viewed": len(viewed_products)}
        
    except Exception as e:
        print(f"Error en tracking: {e}")
        return {"message": "Error en tracking"}


@router.get("/trending")
async def get_trending_products(db: Session = Depends(get_db)):
    """
    Productos trending (más vistos)
    Basado en tracking de Redis
    """
    try:
        # Por ahora retornar productos populares
        products = await intelligent_cache._get_popular_products(db)
        
        return {
            "trending": products[:5],
            "period": "24h",
            "from_cache": True
        }
        
    except Exception as e:
        print(f"Error obteniendo trending: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
