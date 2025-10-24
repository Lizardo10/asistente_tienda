# backend/app/routers/products_ultra_simple.py
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter(prefix="/products", tags=["products"])

# Datos de ejemplo para productos
SAMPLE_PRODUCTS = [
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

@router.get("")
def list_products():
    """Lista todos los productos activos"""
    return SAMPLE_PRODUCTS

@router.get("/all")
def list_all_products():
    """Lista todos los productos (activos e inactivos)"""
    return SAMPLE_PRODUCTS

@router.get("/{product_id}")
def get_product(product_id: int):
    """Obtiene un producto por ID"""
    for product in SAMPLE_PRODUCTS:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Producto no encontrado")

@router.get("/health/check")
def health_check():
    """Endpoint de salud para productos"""
    return {"status": "ok", "message": "Products service is running", "products_count": len(SAMPLE_PRODUCTS)}
