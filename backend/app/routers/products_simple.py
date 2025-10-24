# backend/app/routers/products_simple.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..database import get_db
from ..models.product_simple import Product, ProductRead
from sqlmodel import Session, select

router = APIRouter(prefix="/products", tags=["products"])

@router.get("", response_model=List[ProductRead])
def list_products(db: Session = Depends(get_db)):
    """Lista todos los productos activos"""
    try:
        statement = select(Product).where(Product.active == True)
        products = db.exec(statement).all()
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener productos: {str(e)}")

@router.get("/all", response_model=List[ProductRead])
def list_all_products(db: Session = Depends(get_db)):
    """Lista todos los productos (activos e inactivos)"""
    try:
        statement = select(Product)
        products = db.exec(statement).all()
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener productos: {str(e)}")

@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Obtiene un producto por ID"""
    try:
        statement = select(Product).where(Product.id == product_id)
        product = db.exec(statement).first()
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener producto: {str(e)}")

@router.get("/health/check")
def health_check():
    """Endpoint de salud para productos"""
    return {"status": "ok", "message": "Products service is running"}
