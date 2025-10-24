"""
Router para checkout y pagos con PayPal
Sistema completo de procesamiento de pagos
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session
from typing import Dict, Any, Optional
import json
import uuid
from datetime import datetime

from app.database import get_db
from app.models_sqlmodel.order import Order, OrderItem
from app.models import User, Product
from app.models_sqlmodel.payment import PaymentTransaction
from app.security import get_current_user
from app.services.paypal_service import paypal_service

router = APIRouter(prefix="/checkout", tags=["Checkout"])


@router.post("/create-order")
async def create_order(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
            product = db.get(Product, item["product_id"])
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
        
        # Crear orden
        order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            status="pending",
            payment_method="paypal",
            payment_status="pending"
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        # Crear items de la orden
        for item_data in order_items:
            order_item = OrderItem(
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
    current_user: User = Depends(get_current_user)
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
        order = db.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        
        if order.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="No autorizado")
        
        # Obtener items de la orden para PayPal
        items = db.exec(
            db.query(OrderItem).where(OrderItem.order_id == order_id)
        ).all()
        
        order_data = {
            "order_id": order.id,
            "total_amount": order.total_amount,
            "items": []
        }
        
        # Obtener información de productos para cada item
        for item in items:
            print(f"Processing item: {item}")
            print(f"Item product_id: {item.product_id}")
            # Usar SQLAlchemy para obtener el producto
            product = db.query(Product).filter(Product.id == item.product_id).first()
            print(f"Product found: {product}")
            if product:
                order_data["items"].append({
                    "name": product.title,
                    "product_id": item.product_id,
                    "price": float(item.price_each),
                    "quantity": item.quantity
                })
        
        # Verificar si PayPal está configurado
        if not paypal_service.client_id or not paypal_service.client_secret:
            # Modo desarrollo - simular PayPal
            print("⚠️ PayPal no configurado - usando modo desarrollo")
            payment_id = f"PAY-DEV-{uuid.uuid4().hex[:10].upper()}"
            
            order.payment_id = payment_id
            order.payment_status = "created"
            db.commit()
            
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
        try:
            paypal_response = await paypal_service.create_payment(order_data)
            
            # Verificar que la respuesta tenga la estructura esperada
            if not paypal_response or "id" not in paypal_response:
                print(f"❌ Respuesta PayPal inválida: {paypal_response}")
                raise HTTPException(status_code=500, detail="Error en respuesta de PayPal")
            
            payment_id = paypal_response["id"]
            approval_url = paypal_service.get_approval_url(paypal_response)
            
        except Exception as paypal_error:
            print(f"❌ Error en PayPal API: {paypal_error}")
            raise HTTPException(status_code=500, detail=f"Error en PayPal: {str(paypal_error)}")
        
        # Actualizar orden con payment_id
        order.payment_id = payment_id
        order.payment_status = "created"
        db.commit()
        
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
    current_user: Optional[Dict[str, Any]] = None
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
        
        # Buscar orden por payment_id
        order = db.exec(
            db.query(Order).where(Order.payment_id == payment_id)
        ).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        
        if order.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="No autorizado")
        
        # Verificar si PayPal está configurado
        if not paypal_service.client_id or not paypal_service.client_secret:
            # Modo desarrollo - simular pago exitoso
            print("⚠️ PayPal no configurado - simulando pago exitoso")
            order.status = "completed"
            order.payment_status = "completed"
            order.payment_id = payment_id
            order.payer_id = payer_id
            order.completed_at = datetime.utcnow()
            
            # Crear transacción de pago simulada
            payment_transaction = PaymentTransaction(
                order_id=order.id,
                payment_method="paypal",
                payment_provider_id=payment_id,
                amount=order.total_amount,
                currency="USD",
                status="completed",
                transaction_id=f"DEV-{payment_id}",
                payer_id=payer_id,
                processed_at=datetime.utcnow()
            )
            db.add(payment_transaction)
            
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
            order.payment_status = "completed"
            order.payment_id = payment_id
            order.payer_id = payer_id
            order.completed_at = datetime.utcnow()
            
            # Crear transacción de pago
            payment_transaction = PaymentTransaction(
                order_id=order.id,
                payment_method="paypal",
                payment_provider_id=payment_id,
                amount=order.total_amount,
                currency="USD",
                status="completed",
                transaction_id=transaction_id,
                payer_id=payer_id,
                processed_at=datetime.utcnow()
            )
            db.add(payment_transaction)
            
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
            order.payment_status = "failed"
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
            # Buscar orden
            order = db.exec(
                db.query(Order).where(Order.payment_id == payment_id)
            ).first()
            
            if order:
                # Confirmar pago
                order.status = "completed"
                order.payment_status = "completed"
                order.payer_id = payer_id
                order.completed_at = datetime.utcnow()
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
    current_user: Optional[Dict[str, Any]] = None
):
    """
    Obtener detalles de una orden
    """
    try:
        
        order = db.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        
        if order.user_id != current_user.id and not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="No autorizado")
        
        # Obtener items de la orden
        items = db.exec(
            db.query(OrderItem).where(OrderItem.order_id == order_id)
        ).all()
        
        order_data = {
            "id": order.id,
            "total_amount": order.total_amount,
            "status": order.status,
            "payment_method": order.payment_method,
            "payment_status": order.payment_status,
            "created_at": order.created_at,
            "completed_at": order.completed_at,
            "items": [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price": item.price,
                    "subtotal": item.price * item.quantity
                }
                for item in items
            ]
        }
        
        return order_data
        
    except Exception as e:
        print(f"Error obteniendo orden: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
