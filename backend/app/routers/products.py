# backend/app/routers/products.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4
import os
from ..database.connection import get_db
from .. import schemas
from ..models_sqlmodel.product import Product, ProductImage
from ..models_sqlmodel.user import User
from ..security import get_current_admin  # 👈 protege con JWT + rol admin
from app.services.intelligent_cache_service import intelligent_cache

router = APIRouter(prefix="/products", tags=["products"])

@router.get("", response_model=List[schemas.ProductOut])
async def list_products(db: Session = Depends(get_db)):
    """Listar productos (CON CACHÉ INTELIGENTE)"""
    # Usar caché inteligente en lugar de consulta directa
    products_data = await intelligent_cache.get_all_products(db, active_only=True)
    return products_data

@router.get("/all", response_model=List[schemas.ProductOut])
def list_all_products(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """
    Lista todos los productos (activos e inactivos) - Solo para administradores.
    Útil para el historial de compras donde pueden aparecer productos desactivados.
    """
    return db.query(Product).all()

@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).get(product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return p

@router.post("", response_model=schemas.ProductOut, status_code=201, dependencies=[Depends(get_current_admin)])
def create_product(data: schemas.ProductCreate, db: Session = Depends(get_db)):
    p = Product(
        title=data.title,
        description=data.description,
        price=data.price,
        image_url=data.image_url,
        active=True
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

@router.put("/{product_id}", response_model=schemas.ProductOut, dependencies=[Depends(get_current_admin)])
def update_product(product_id: int, data: schemas.ProductUpdate, db: Session = Depends(get_db)):
    p = db.query(Product).get(product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if data.title is not None: p.title = data.title
    if data.description is not None: p.description = data.description
    if data.price is not None: p.price = data.price
    if data.image_url is not None: p.image_url = data.image_url
    if data.active is not None: p.active = data.active
    db.commit()
    db.refresh(p)
    return p

@router.delete("/{product_id}", status_code=204, dependencies=[Depends(get_current_admin)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).get(product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(p)
    db.commit()
    return

# ---------- Imágenes ----------
def _media_base_url():
    return "/media"

@router.get("/{product_id}/images", response_model=List[schemas.ProductImageOut])
def list_images(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).get(product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return p.images

@router.post("/{product_id}/images", response_model=schemas.ProductImageOut, status_code=201, dependencies=[Depends(get_current_admin)])
async def upload_image(product_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    p = db.query(Product).get(product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    media_dir = os.getenv("MEDIA_DIR", "media")
    os.makedirs(media_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1].lower()
    name = f"{uuid4().hex}{ext or '.jpg'}"
    path = os.path.join(media_dir, name)

    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)

    url = f"{_media_base_url()}/{name}"
    img = ProductImage(product_id=p.id, url=url)
    db.add(img)
    db.commit()
    db.refresh(img)
    return img

@router.delete("/{product_id}/images/{image_id}", status_code=204, dependencies=[Depends(get_current_admin)])
def delete_image(product_id: int, image_id: int, db: Session = Depends(get_db)):
    img = db.query(ProductImage).get(image_id)
    if not img or img.product_id != product_id:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    media_dir = os.getenv("MEDIA_DIR", "media")
    filename = img.url.split("/media/")[-1] if "/media/" in img.url else None
    if filename:
        try:
            os.remove(os.path.join(media_dir, filename))
        except FileNotFoundError:
            pass
    db.delete(img)
    db.commit()
    return
