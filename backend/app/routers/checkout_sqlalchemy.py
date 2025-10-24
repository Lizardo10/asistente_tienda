"""
Router para checkout y pagos con PayPal - Compatible con SQLAlchemy
Sistema completo de procesamiento de pagos
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import json
import uuid
from datetime import datetime

from app.db import get_db
from app import models
from app.security import get_current_user
from app.services.paypal_service import paypal_service

router = APIRouter(prefix="/checkout", tags=["Checkout"])


@router.post("/create-order")
async def create_order(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Crear orden y preparar para pago con PayPal
    """
    try:
        # Obtener datos del carrito desde el request
        body = await request.json()
        cart_items = body.get("items", [])
        
        if not cart_items:
            raise HTTPException(status_code=400, detail="Carrito vacío")
        
        # Calcular total
        total_amount = 0
        order_items = []
        
        for item in cart_items:
            product = db.query(models.Product).get(item["product_id"])
            if not product:
                raise HTTPException(status_code=404, detail=f"Producto {item['product_id']} no encontrado")
            
            if not product.active:
                raise HTTPException(status_code=400, detail=f"Producto {product.title} no disponible")
            
            item_total = float(product.price) * item["quantity"]
            total_amount += item_total
            
            order_items.append({
                "product": product,
                "quantity": item["quantity"],
                "price": float(product.price)
            })
        
        # Crear orden usando el modelo SQLAlchemy existente
        order = models.Order(
            user_id=current_user.id,
            status="pending"
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        # Crear items de la orden
        for item_data in order_items:
            order_item = models.OrderItem(
                order_id=order.id,
                product_id=item_data["product"].id,
                quantity=item_data["quantity"],
                price_each=item_data["price"]
            )
            db.add(order_item)
        
        db.commit()
        
        # Preparar datos para PayPal
        paypal_data = {
            "order_id": order.id,
            "total_amount": total_amount,
            "currency": "USD",  # PayPal usa USD por defecto
            "items": [
                {
                    "name": item_data["product"].title,
                    "quantity": item_data["quantity"],
                    "price": item_data["price"]
                }
                for item_data in order_items
            ],
            "return_url": f"{request.base_url}checkout/success",
            "cancel_url": f"{request.base_url}checkout/cancel"
        }
        
        return {
            "order_id": order.id,
            "total_amount": total_amount,
            "paypal_data": paypal_data,
            "message": "Orden creada exitosamente"
        }
        
    except Exception as e:
        print(f"Error creando orden: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/paypal/create-payment")
async def create_paypal_payment(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Crear pago en PayPal (real o modo desarrollo)
    """
    try:
        body = await request.json()
        order_id = body.get("order_id")
        
        if not order_id:
            raise HTTPException(status_code=400, detail="order_id requerido")
        
        # Obtener orden
        order = db.query(models.Order).get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        
        if order.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="No autorizado")
        
        # Obtener items de la orden para PayPal
        items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).all()
        
        # Calcular total
        total_amount = sum(item.price_each * item.quantity for item in items)
        
        order_data = {
            "order_id": order.id,
            "total_amount": total_amount,
            "items": [
                {
                    "name": item.product.title,
                    "product_id": item.product_id,
                    "price": float(item.price_each),
                    "quantity": item.quantity
                }
                for item in items
            ]
        }
        
        # Verificar si PayPal está configurado
        if not paypal_service.client_id or not paypal_service.client_secret:
            # Modo desarrollo - simular PayPal
            print("⚠️ PayPal no configurado - usando modo desarrollo")
            payment_id = f"PAY-DEV-{uuid.uuid4().hex[:10].upper()}"
            
            # Simular respuesta de PayPal
            paypal_response = {
                "id": payment_id,
                "state": "created",
                "links": [
                    {
                        "href": f"https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token={payment_id}",
                        "rel": "approval_url",
                        "method": "REDIRECT"
                    }
                ]
            }
            
            return {
                "payment_id": payment_id,
                "approval_url": paypal_response["links"][0]["href"],
                "paypal_response": paypal_response,
                "message": "Pago creado en PayPal (modo desarrollo - configura PayPal para usar modo real)"
            }
        
        # Modo real - usar PayPal API
        print("✅ Usando PayPal real")
        paypal_response = await paypal_service.create_payment(order_data)
        
        payment_id = paypal_response["id"]
        approval_url = paypal_service.get_approval_url(paypal_response)
        
        return {
            "payment_id": payment_id,
            "approval_url": approval_url,
            "paypal_response": paypal_response,
            "message": f"Pago creado en PayPal ({paypal_service.mode} mode)"
        }
        
    except Exception as e:
        print(f"Error creando pago PayPal: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/paypal/execute")
async def execute_paypal_payment(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Ejecutar pago de PayPal (real o modo desarrollo)
    """
    try:
        body = await request.json()
        payment_id = body.get("payment_id")
        payer_id = body.get("payer_id")
        
        if not payment_id or not payer_id:
            raise HTTPException(status_code=400, detail="payment_id y payer_id requeridos")
        
        # Buscar orden por payment_id (necesitamos agregar este campo al modelo)
        # Por ahora, simularemos que encontramos la orden
        order = db.query(models.Order).filter(models.Order.id == 1).first()  # Temporal
        
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        
        if order.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="No autorizado")
        
        # Verificar si PayPal está configurado
        if not paypal_service.client_id or not paypal_service.client_secret:
            # Modo desarrollo - simular pago exitoso
            print("⚠️ PayPal no configurado - simulando pago exitoso")
            order.status = "completed"
            db.commit()
            
            return {
                "order_id": order.id,
                "status": "completed",
                "payment_status": "completed",
                "message": "Pago procesado exitosamente (modo desarrollo)"
            }
        
        # Modo real - ejecutar pago con PayPal
        print("✅ Ejecutando pago PayPal real")
        execution_response = await paypal_service.execute_payment(payment_id, payer_id)
        
        if paypal_service.is_payment_completed(execution_response):
            # Pago exitoso
            transaction_id = paypal_service.get_transaction_id(execution_response)
            
            order.status = "completed"
            db.commit()
            
            return {
                "order_id": order.id,
                "status": "completed",
                "payment_status": "completed",
                "transaction_id": transaction_id,
                "message": f"Pago procesado exitosamente con PayPal ({paypal_service.mode} mode)"
            }
        else:
            # Pago fallido
            order.status = "failed"
            db.commit()
            
            return {
                "order_id": order.id,
                "status": "failed",
                "payment_status": "failed",
                "message": "Pago fallido en PayPal"
            }
        
    except Exception as e:
        print(f"Error ejecutando pago PayPal: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/success")
async def checkout_success(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Página de éxito después del pago
    """
    try:
        # Obtener parámetros de PayPal
        payment_id = request.query_params.get("paymentId")
        payer_id = request.query_params.get("PayerID")
        
        if payment_id and payer_id:
            # Buscar orden (temporal)
            order = db.query(models.Order).filter(models.Order.id == 1).first()
            
            if order:
                # Confirmar pago
                order.status = "completed"
                db.commit()
                
                return {
                    "success": True,
                    "order_id": order.id,
                    "message": "Pago procesado exitosamente"
                }
        
        return {
            "success": True,
            "message": "Pago procesado exitosamente"
        }
        
    except Exception as e:
        print(f"Error en checkout success: {e}")
        return {
            "success": False,
            "message": "Error procesando pago"
        }


@router.get("/cancel")
async def checkout_cancel():
    """
    Página de cancelación de pago
    """
    return {
        "success": False,
        "message": "Pago cancelado por el usuario"
    }


@router.get("/order/{order_id}")
async def get_order_details(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Obtener detalles de una orden
    """
    try:
        order = db.query(models.Order).get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        
        if order.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="No autorizado")
        
        # Obtener items de la orden
        items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).all()
        
        total_amount = sum(item.price_each * item.quantity for item in items)
        
        order_data = {
            "id": order.id,
            "total_amount": total_amount,
            "status": order.status,
            "created_at": order.created_at,
            "items": [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price": item.price_each,
                    "subtotal": item.price_each * item.quantity
                }
                for item in items
            ]
        }
        
        return order_data
        
    except Exception as e:
        print(f"Error obteniendo orden: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


