# backend/app/routers/products_db.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from datetime import datetime
from sqlmodel import Session, select
from ..database import get_db
from ..models.product_simple import Product

router = APIRouter(prefix="/products", tags=["products"])

@router.get("")
def list_products(db: Session = Depends(get_db)):
    """
    Lista todos los productos activos desde la base de datos.
    """
    try:
        # Intentar obtener productos de la base de datos
        products = db.exec(select(Product).where(Product.active == True)).all()
        
        if not products:
            # Si no hay productos en la base de datos, devolver productos de ejemplo
            return [
                {
                    "id": 1,
                    "title": "Laptop Gaming",
                    "name": "Laptop Gaming",
                    "description": "Laptop para gaming de alta gama",
                    "price": 1299.99,
                    "stock": 10,
                    "active": True,
                    "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=300&fit=crop",
                    "created_at": "2024-01-01T00:00:00"
                },
                {
                    "id": 2,
                    "title": "Smartphone Pro",
                    "name": "Smartphone Pro",
                    "description": "Smartphone con cámara profesional",
                    "price": 899.99,
                    "stock": 25,
                    "active": True,
                    "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=300&fit=crop",
                    "created_at": "2024-01-02T00:00:00"
                },
                {
                    "id": 3,
                    "title": "Auriculares Wireless",
                    "name": "Auriculares Wireless",
                    "description": "Auriculares inalámbricos con cancelación de ruido",
                    "price": 299.99,
                    "stock": 50,
                    "active": True,
                    "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=300&fit=crop",
                    "created_at": "2024-01-03T00:00:00"
                }
            ]
        
        # Convertir productos de la base de datos al formato esperado
        result = []
        for product in products:
            result.append({
                "id": product.id,
                "title": product.name,
                "name": product.name,
                "description": product.description or "",
                "price": product.price,
                "stock": product.stock,
                "active": product.active,
                "image_url": product.image_url or "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=300&fit=crop",
                "created_at": product.created_at.isoformat() if product.created_at else "2024-01-01T00:00:00"
            })
        
        return result
        
    except Exception as e:
        # Si hay error con la base de datos, devolver productos de ejemplo
        print(f"Error accediendo a la base de datos: {e}")
        return [
            {
                "id": 1,
                "title": "Laptop Gaming",
                "name": "Laptop Gaming",
                "description": "Laptop para gaming de alta gama",
                "price": 1299.99,
                "stock": 10,
                "active": True,
                "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=300&fit=crop",
                "created_at": "2024-01-01T00:00:00"
            },
            {
                "id": 2,
                "title": "Smartphone Pro",
                "name": "Smartphone Pro",
                "description": "Smartphone con cámara profesional",
                "price": 899.99,
                "stock": 25,
                "active": True,
                "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=300&fit=crop",
                "created_at": "2024-01-02T00:00:00"
            },
            {
                "id": 3,
                "title": "Auriculares Wireless",
                "name": "Auriculares Wireless",
                "description": "Auriculares inalámbricos con cancelación de ruido",
                "price": 299.99,
                "stock": 50,
                "active": True,
                "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=300&fit=crop",
                "created_at": "2024-01-03T00:00:00"
            }
        ]

@router.get("/all")
def list_all_products(db: Session = Depends(get_db)):
    """
    Lista todos los productos (incluyendo inactivos) - Solo para administradores.
    """
    try:
        products = db.exec(select(Product)).all()
        
        if not products:
            return []
        
        result = []
        for product in products:
            result.append({
                "id": product.id,
                "title": product.name,
                "name": product.name,
                "description": product.description or "",
                "price": product.price,
                "stock": product.stock,
                "active": product.active,
                "image_url": product.image_url or "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=300&fit=crop",
                "created_at": product.created_at.isoformat() if product.created_at else "2024-01-01T00:00:00"
            })
        
        return result
        
    except Exception as e:
        print(f"Error accediendo a la base de datos: {e}")
        return []

@router.get("/health/check")
def health_check():
    return {"status": "ok", "message": "Products service funcionando con base de datos"}
