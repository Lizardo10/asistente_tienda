"""
Router para gestión de saldo de usuarios
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db import get_db
from app.models import User
from app.security import get_current_user, get_current_admin

router = APIRouter(prefix="/balance", tags=["Balance"])


@router.post("/add")
async def add_balance(
    amount: float,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Agregar saldo a un usuario (solo admin)
    """
    try:
        if amount <= 0:
            raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0")
        
        # Por simplicidad, agregamos saldo al primer usuario
        user = db.query(User).first()
        if not user:
            raise HTTPException(status_code=404, detail="No hay usuarios en el sistema")
        
        user.balance += amount
        db.commit()
        
        return {
            "status": "success",
            "message": f"Saldo agregado exitosamente",
            "user_email": user.email,
            "amount_added": amount,
            "new_balance": user.balance
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error agregando saldo: {str(e)}")


@router.post("/add-to-user/{user_id}")
async def add_balance_to_user(
    user_id: int,
    amount: float,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Agregar saldo a un usuario específico (solo admin)
    """
    try:
        if amount <= 0:
            raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        user.balance += amount
        db.commit()
        
        return {
            "status": "success",
            "message": f"Saldo agregado exitosamente",
            "user_email": user.email,
            "amount_added": amount,
            "new_balance": user.balance
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error agregando saldo: {str(e)}")


@router.get("/my-balance")
async def get_my_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener saldo del usuario actual
    """
    try:
        return {
            "user_email": current_user.email,
            "balance": current_user.balance
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo saldo: {str(e)}")


@router.post("/set-balance/{user_id}")
async def set_user_balance(
    user_id: int,
    balance: float,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Establecer saldo específico para un usuario (solo admin)
    """
    try:
        if balance < 0:
            raise HTTPException(status_code=400, detail="El saldo no puede ser negativo")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        old_balance = user.balance
        user.balance = balance
        db.commit()
        
        return {
            "status": "success",
            "message": f"Saldo actualizado exitosamente",
            "user_email": user.email,
            "old_balance": old_balance,
            "new_balance": user.balance
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando saldo: {str(e)}")









