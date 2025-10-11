from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from ..db import get_db
from .. import models, schemas
from ..security import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/my", response_model=List[schemas.OrderOut])
def my_orders(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Historial del cliente autenticado.
    """
    return (
        db.query(models.Order)
        .filter(models.Order.user_id == user.id)
        .order_by(models.Order.created_at.desc())
        .all()
    )


@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Detalle de pedido. Solo visible para el dueño o un admin.
    """
    order = db.query(models.Order).get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if (order.user_id != user.id) and (not user.is_admin):
        raise HTTPException(status_code=403, detail="No autorizado")
    return order


@router.get("", response_model=List[schemas.OrderOutWithUser])
def list_orders(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Listado completo de pedidos con información del usuario (solo admin).
    """
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Solo administrador")
    return (
        db.query(models.Order)
        .options(joinedload(models.Order.user))
        .order_by(models.Order.created_at.desc())
        .all()
    )


@router.post("", response_model=schemas.OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    data: schemas.OrderCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Crea un pedido para el usuario autenticado.
    Los precios de los items se copian del producto al momento de la compra.
    """
    if not data.items:
        raise HTTPException(status_code=400, detail="El pedido debe tener items")

    order = models.Order(user_id=user.id, status="pending")
    db.add(order)
    db.flush()  # obtiene order.id

    for it in data.items:
        prod = db.query(models.Product).get(it.product_id)
        if not prod:
            raise HTTPException(
                status_code=404, detail=f"Producto {it.product_id} no existe"
            )
        db.add(
            models.OrderItem(
                order_id=order.id,
                product_id=prod.id,
                quantity=it.quantity,
                price_each=prod.price,  # precio actual
            )
        )

    db.commit()
    db.refresh(order)
    return order
