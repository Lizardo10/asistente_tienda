"""
Router para checkout usando solo SQLAlchemy
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import json
import uuid
from datetime import datetime

from app.db import get_db
from app.models import User, Product, Order, OrderItem
from app.security import get_current_user
from app.services.paypal_service import paypal_service
from app.routers.invoices import generate_invoice_html, send_invoice_email
from app.routers.admin_accounts import process_paypal_payment
from app.routers.realtime import manager
from app.routers.cart_clear_improved import clear_cart_after_payment

router = APIRouter(prefix="/checkout-sqlalchemy", tags=["Checkout SQLAlchemy"])


@router.post("/create-order")
async def create_order_sqlalchemy(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crear orden usando solo SQLAlchemy
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
            product = db.query(Product).filter(Product.id == item["product_id"]).first()
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
        
        # Crear orden usando SQLAlchemy
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
        
        return {
            "order_id": order.id,
            "total_amount": total_amount,
            "status": order.status,
            "message": "Orden creada exitosamente"
        }
        
    except Exception as e:
        print(f"Error creando orden: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/paypal/create-payment")
async def create_paypal_payment_sqlalchemy(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crear pago en PayPal usando solo SQLAlchemy
    """
    try:
        body = await request.json()
        order_id = body.get("order_id")
        
        if not order_id:
            raise HTTPException(status_code=400, detail="order_id requerido")
        
        # Obtener orden usando SQLAlchemy
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        
        if order.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="No autorizado")
        
        # Obtener items de la orden usando SQLAlchemy
        items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        
        order_data = {
            "order_id": order.id,
            "total_amount": order.total_amount,
            "items": []
        }
        
        # Obtener información de productos para cada item
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
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
            "message": "Pago creado en PayPal"
        }
        
    except Exception as e:
        print(f"Error creando pago PayPal: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/paypal/execute")
async def execute_paypal_payment_sqlalchemy(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ejecutar pago de PayPal usando solo SQLAlchemy
    """
    try:
        body = await request.json()
        payment_id = body.get("payment_id")
        payer_id = body.get("payer_id")
        
        if not payment_id or not payer_id:
            raise HTTPException(status_code=400, detail="payment_id y payer_id requeridos")
        
        # Buscar orden por payment_id o order_id si es modo desarrollo
        if payment_id.startswith("PAY-DEV-"):
            # Extraer order_id del payment_id de desarrollo
            order_id = int(payment_id.replace("PAY-DEV-", ""))
            order = db.query(Order).filter(Order.id == order_id).first()
        else:
            order = db.query(Order).filter(Order.payment_id == payment_id).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        
        if order.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="No autorizado")
        
        # Verificar si es modo desarrollo
        if payment_id.startswith("PAY-DEV-"):
            # Procesar pago en modo desarrollo
            try:
                # Procesar pago real (agregar a cuenta receptora, actualizar stock)
                receiver = process_paypal_payment(db, order, order.total_amount)
                
                # Enviar factura por correo
                invoice_html = generate_invoice_html(order, current_user)
                invoice_number = f"INV-{order.id:06d}"
                email_sent = send_invoice_email(current_user.email, invoice_html, invoice_number)
                
                # Enviar notificaciones en tiempo real
                try:
                    import json
                    from datetime import datetime
                    
                    # Notificar al usuario - orden completada
                    user_message = {
                        "type": "order_completed",
                        "data": {
                            "order_id": order.id,
                            "total_amount": order.total_amount,
                            "status": order.status,
                            "items_count": len(order.items)
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await manager.send_personal_message(json.dumps(user_message), current_user.id)
                    
                    # Notificar al usuario - limpiar carrito
                    cart_clear_message = {
                        "type": "cart_cleared",
                        "data": {
                            "message": "Carrito limpiado después de compra exitosa",
                            "order_id": order.id
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await manager.send_personal_message(json.dumps(cart_clear_message), current_user.id)
                    
                    # Notificar a administradores
                    admin_message = {
                        "type": "new_order",
                        "data": {
                            "order_id": order.id,
                            "user_email": current_user.email,
                            "total_amount": order.total_amount,
                            "items_count": len(order.items)
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await manager.broadcast_to_admins(json.dumps(admin_message))
                    
                except Exception as e:
                    print(f"Error enviando notificaciones: {e}")
                
                # Limpiar carrito después del pago exitoso
                try:
                    await clear_cart_after_payment(order.id, current_user.email, db, current_user)
                    print(f"✅ Carrito limpiado para usuario {current_user.email}")
                except Exception as e:
                    print(f"❌ Error limpiando carrito: {e}")
                
                return {
                    "status": "success",
                    "message": "Pago procesado exitosamente",
                    "order_id": order.id,
                    "payment_method": "paypal",
                    "amount_paid": order.total_amount,
                    "receiver_balance": receiver.balance,
                    "invoice_sent": email_sent,
                    "invoice_number": invoice_number
                }
            except Exception as e:
                print(f"Error procesando pago: {e}")
                return {
                    "status": "error",
                    "message": f"Error procesando pago: {str(e)}",
                    "order_id": order.id
                }
        
        # Modo real - ejecutar con PayPal
        try:
            execution_response = await paypal_service.execute_payment(payment_id, payer_id)
            
            if paypal_service.is_payment_completed(execution_response):
                # Procesar pago real (agregar a cuenta receptora, actualizar stock)
                receiver = process_paypal_payment(db, order, order.total_amount)
                
                # Enviar factura por correo
                try:
                    invoice_html = generate_invoice_html(order, current_user)
                    invoice_number = f"INV-{order.id:06d}"
                    email_sent = send_invoice_email(current_user.email, invoice_html, invoice_number)
                    
                    # Enviar notificaciones en tiempo real
                    try:
                        import json
                        from datetime import datetime
                        
                        # Notificar al usuario - orden completada
                        user_message = {
                            "type": "order_completed",
                            "data": {
                                "order_id": order.id,
                                "total_amount": order.total_amount,
                                "status": order.status,
                                "items_count": len(order.items)
                            },
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        await manager.send_personal_message(json.dumps(user_message), current_user.id)
                        
                        # Notificar al usuario - limpiar carrito
                        cart_clear_message = {
                            "type": "cart_cleared",
                            "data": {
                                "message": "Carrito limpiado después de compra exitosa",
                                "order_id": order.id
                            },
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        await manager.send_personal_message(json.dumps(cart_clear_message), current_user.id)
                        
                        # Notificar a administradores
                        admin_message = {
                            "type": "new_order",
                            "data": {
                                "order_id": order.id,
                                "user_email": current_user.email,
                                "total_amount": order.total_amount,
                                "items_count": len(order.items)
                            },
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        await manager.broadcast_to_admins(json.dumps(admin_message))
                        
                    except Exception as e:
                        print(f"Error enviando notificaciones: {e}")
                    
                    # Limpiar carrito después del pago exitoso
                    try:
                        await clear_cart_after_payment(order.id, current_user.email, db, current_user)
                        print(f"✅ Carrito limpiado para usuario {current_user.email}")
                    except Exception as e:
                        print(f"❌ Error limpiando carrito: {e}")
                    
                    return {
                        "status": "success",
                        "message": "Pago procesado exitosamente",
                        "order_id": order.id,
                        "payment_method": "paypal",
                        "amount_paid": order.total_amount,
                        "receiver_balance": receiver.balance,
                        "invoice_sent": email_sent,
                        "invoice_number": invoice_number
                    }
                except Exception as e:
                    print(f"Error enviando factura: {e}")
                    return {
                        "status": "success",
                        "message": "Pago procesado exitosamente",
                        "order_id": order.id,
                        "payment_method": "paypal",
                        "amount_paid": order.total_amount,
                        "receiver_balance": receiver.balance,
                        "invoice_sent": False,
                        "invoice_error": str(e)
                    }
            else:
                order.payment_status = "failed"
                db.commit()
                
                return {
                    "status": "failed",
                    "message": "El pago no fue completado",
                    "order_id": order.id
                }
                
        except Exception as paypal_error:
            print(f"❌ Error ejecutando pago PayPal: {paypal_error}")
            order.payment_status = "failed"
            db.commit()
            
            raise HTTPException(status_code=500, detail=f"Error ejecutando pago: {str(paypal_error)}")
        
    except Exception as e:
        print(f"Error ejecutando pago: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# Endpoint de pago directo eliminado - solo PayPal
