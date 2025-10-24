"""
Router para el área contable
Solo accesible para administradores
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.database import get_db
from app.services.accounting_service_basic import AccountingService
# Comentado temporalmente para evitar errores
# from app.models_sqlmodel.accounting import (
#     InventoryTransactionCreate, StockAdjustmentRequest, 
#     InventoryTransactionOut, StockLevelOut, FinancialReportOut
# )
from app.routers.auth import get_current_user
from app.models_sqlmodel.user import User

router = APIRouter(prefix="/admin/accounting", tags=["Accounting"])


def verify_admin(user: User = Depends(get_current_user)):
    """Verificar que el usuario sea administrador"""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden acceder a esta área"
        )
    return user


# ==================== DASHBOARD ====================

@router.get("/dashboard")
async def get_dashboard_stats(
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas para el dashboard contable"""
    accounting_service = AccountingService(db)
    return accounting_service.get_dashboard_stats()


# ==================== INVENTARIO ====================

@router.get("/inventory/stock-levels")
async def get_stock_levels(
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Obtener niveles de stock de todos los productos"""
    accounting_service = AccountingService(db)
    return accounting_service.get_stock_levels()


@router.get("/inventory/low-stock")
async def get_low_stock_products(
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Obtener productos con stock bajo"""
    accounting_service = AccountingService(db)
    return accounting_service.get_low_stock_products()


@router.post("/inventory/adjust-stock")
async def adjust_stock(
    adjustment: Dict[str, Any],
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Ajustar stock de un producto"""
    accounting_service = AccountingService(db)
    
    success = accounting_service.adjust_stock(
        product_id=adjustment["product_id"],
        new_quantity=adjustment["new_quantity"],
        reason=adjustment["reason"],
        admin_user_id=admin_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error ajustando el stock del producto"
        )
    
    return {"message": "Stock ajustado correctamente"}


# Funciones adicionales se implementarán gradualmente
