"""
Sistema de facturas y envío por correo
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
import uuid

from app.db import get_db
from app.models import User, Order, OrderItem, Product
from app.security import get_current_user, get_current_admin

router = APIRouter(prefix="/invoices", tags=["Invoices"])


def generate_invoice_html(order: Order, user: User) -> str:
    """
    Generar HTML de la factura
    """
    invoice_number = f"INV-{order.id:06d}"
    invoice_date = order.created_at.strftime("%d/%m/%Y")
    
    # Calcular totales
    subtotal = sum(item.price_each * item.quantity for item in order.items)
    tax_rate = 0.12  # 12% IVA
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Factura {invoice_number}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .invoice-container {{
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 2px solid #007bff;
                padding-bottom: 20px;
            }}
            .company-info {{
                margin-bottom: 30px;
            }}
            .invoice-details {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 30px;
            }}
            .invoice-info, .customer-info {{
                flex: 1;
            }}
            .invoice-info h3, .customer-info h3 {{
                color: #007bff;
                margin-bottom: 10px;
            }}
            .items-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 30px;
            }}
            .items-table th, .items-table td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            .items-table th {{
                background-color: #007bff;
                color: white;
            }}
            .totals {{
                text-align: right;
                margin-top: 20px;
            }}
            .totals table {{
                margin-left: auto;
                width: 300px;
            }}
            .totals td {{
                padding: 8px;
                border-bottom: 1px solid #eee;
            }}
            .total-row {{
                font-weight: bold;
                font-size: 1.2em;
                background-color: #f8f9fa;
            }}
            .footer {{
                margin-top: 40px;
                text-align: center;
                color: #666;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="invoice-container">
            <div class="header">
                <h1>FACTURA</h1>
                <h2>{invoice_number}</h2>
            </div>
            
            <div class="company-info">
                <h3>Tienda Online</h3>
                <p>Dirección: 123 Calle Principal, Ciudad</p>
                <p>Teléfono: +502 1234-5678</p>
                <p>Email: info@tienda.com</p>
            </div>
            
            <div class="invoice-details">
                <div class="invoice-info">
                    <h3>Detalles de la Factura</h3>
                    <p><strong>Número:</strong> {invoice_number}</p>
                    <p><strong>Fecha:</strong> {invoice_date}</p>
                    <p><strong>Método de Pago:</strong> {order.payment_method or 'PayPal'}</p>
                    <p><strong>Estado:</strong> {order.status}</p>
                </div>
                
                <div class="customer-info">
                    <h3>Información del Cliente</h3>
                    <p><strong>Nombre:</strong> {user.full_name or user.email}</p>
                    <p><strong>Email:</strong> {user.email}</p>
                    <p><strong>ID Cliente:</strong> {user.id}</p>
                </div>
            </div>
            
            <table class="items-table">
                <thead>
                    <tr>
                        <th>Producto</th>
                        <th>Cantidad</th>
                        <th>Precio Unitario</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Agregar items
    for item in order.items:
        product = item.product if hasattr(item, 'product') else None
        product_name = product.title if product else f"Producto {item.product_id}"
        item_total = item.price_each * item.quantity
        
        html += f"""
                    <tr>
                        <td>{product_name}</td>
                        <td>{item.quantity}</td>
                        <td>Q{item.price_each:.2f}</td>
                        <td>Q{item_total:.2f}</td>
                    </tr>
        """
    
    html += f"""
                </tbody>
            </table>
            
            <div class="totals">
                <table>
                    <tr>
                        <td>Subtotal:</td>
                        <td>Q{subtotal:.2f}</td>
                    </tr>
                    <tr>
                        <td>IVA (12%):</td>
                        <td>Q{tax_amount:.2f}</td>
                    </tr>
                    <tr class="total-row">
                        <td>Total:</td>
                        <td>Q{total:.2f}</td>
                    </tr>
                </table>
            </div>
            
            <div class="footer">
                <p>Gracias por su compra. Esta es una factura generada automáticamente.</p>
                <p>Para consultas, contacte a: info@tienda.com</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


def send_invoice_email(user_email: str, invoice_html: str, invoice_number: str):
    """
    Enviar factura por correo con configuración mejorada
    """
    try:
        print(f"📧 Intentando enviar factura {invoice_number} a {user_email}")
        
        # Configuración del servidor SMTP
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        
        # Credenciales desde variables de entorno
        sender_email = os.getenv("EMAIL_USER")
        sender_password = os.getenv("EMAIL_PASSWORD")
        
        if not sender_email or not sender_password:
            print("❌ Credenciales de correo no configuradas")
            print("Configura EMAIL_USER y EMAIL_PASSWORD en .env")
            return False
        
        print(f"📧 Servidor SMTP: {smtp_server}:{smtp_port}")
        print(f"📧 Email remitente: {sender_email}")
        
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Factura {invoice_number} - Tienda Online"
        msg['From'] = sender_email
        msg['To'] = user_email
        
        # Crear versión HTML
        html_part = MIMEText(invoice_html, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Enviar email
        print("📧 Conectando al servidor SMTP...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        print("📧 Autenticando...")
        server.login(sender_email, sender_password)
        
        print("📧 Enviando correo...")
        text = msg.as_string()
        server.sendmail(sender_email, user_email, text)
        server.quit()
        
        print(f"✅ Factura {invoice_number} enviada exitosamente a {user_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Error de autenticación SMTP: {e}")
        print("Verifica EMAIL_USER y EMAIL_PASSWORD en .env")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ Error SMTP: {e}")
        return False
    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False


@router.post("/generate/{order_id}")
async def generate_invoice(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generar factura para una orden
    """
    try:
        # Buscar la orden
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        
        if order.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="No autorizado")
        
        if order.payment_status != "completed":
            raise HTTPException(status_code=400, detail="La orden debe estar completada")
        
        # Obtener información del usuario
        user = db.query(User).filter(User.id == order.user_id).first()
        
        # Generar HTML de la factura
        invoice_html = generate_invoice_html(order, user)
        
        # Generar número de factura
        invoice_number = f"INV-{order.id:06d}"
        
        return {
            "invoice_number": invoice_number,
            "order_id": order.id,
            "html": invoice_html,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando factura: {str(e)}")


@router.post("/send/{order_id}")
async def send_invoice_email_endpoint(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Enviar factura por correo
    """
    try:
        # Buscar la orden
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        
        if order.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="No autorizado")
        
        if order.payment_status != "completed":
            raise HTTPException(status_code=400, detail="La orden debe estar completada")
        
        # Obtener información del usuario
        user = db.query(User).filter(User.id == order.user_id).first()
        
        # Generar HTML de la factura
        invoice_html = generate_invoice_html(order, user)
        invoice_number = f"INV-{order.id:06d}"
        
        # Enviar por correo
        email_sent = send_invoice_email(user.email, invoice_html, invoice_number)
        
        if email_sent:
            return {
                "status": "success",
                "message": "Factura enviada por correo exitosamente",
                "invoice_number": invoice_number,
                "sent_to": user.email
            }
        else:
            raise HTTPException(status_code=500, detail="Error enviando factura por correo")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando factura: {str(e)}")


@router.post("/auto-send/{order_id}")
async def auto_send_invoice(
    order_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Enviar factura automáticamente (solo admin)
    """
    try:
        # Buscar la orden
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        
        if order.payment_status != "completed":
            raise HTTPException(status_code=400, detail="La orden debe estar completada")
        
        # Obtener información del usuario
        user = db.query(User).filter(User.id == order.user_id).first()
        
        # Generar HTML de la factura
        invoice_html = generate_invoice_html(order, user)
        invoice_number = f"INV-{order.id:06d}"
        
        # Enviar por correo
        email_sent = send_invoice_email(user.email, invoice_html, invoice_number)
        
        if email_sent:
            return {
                "status": "success",
                "message": "Factura enviada automáticamente",
                "invoice_number": invoice_number,
                "sent_to": user.email,
                "order_id": order.id
            }
        else:
            raise HTTPException(status_code=500, detail="Error enviando factura por correo")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando factura: {str(e)}")
