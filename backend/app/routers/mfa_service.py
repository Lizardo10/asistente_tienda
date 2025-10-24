# backend/app/routers/mfa_service.py
"""
Servicio de Autenticación Multi-Factor (MFA)
SMS, Email, TOTP (Google Authenticator)
"""
import pyotp
import qrcode
import io
import base64
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..database.connection import get_db
from ..models_sqlmodel.user import User
from ..security import get_current_user

router = APIRouter(prefix="/mfa", tags=["mfa"])

class MFAService:
    """Servicio de autenticación multi-factor"""
    
    @staticmethod
    def generate_totp_secret() -> str:
        """Generar secreto TOTP"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_totp_qr(secret: str, email: str) -> str:
        """Generar QR para Google Authenticator"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=email,
            issuer_name="Tu Tienda"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @staticmethod
    def verify_totp_code(secret: str, code: str) -> bool:
        """Verificar código TOTP"""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)
    
    @staticmethod
    def generate_sms_code() -> str:
        """Generar código SMS de 6 dígitos"""
        return f"{secrets.randbelow(1000000):06d}"
    
    @staticmethod
    def generate_email_code() -> str:
        """Generar código de email de 6 dígitos"""
        return f"{secrets.randbelow(1000000):06d}"

@router.post("/setup/totp")
async def setup_totp(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Configurar TOTP (Google Authenticator)"""
    
    # Generar secreto
    secret = MFAService.generate_totp_secret()
    
    # Generar QR
    qr_code = MFAService.generate_totp_qr(secret, current_user.email)
    
    # Guardar secreto temporalmente (en producción usarías Redis)
    current_user.mfa_secret = secret
    current_user.mfa_enabled = False  # No habilitar hasta verificar
    db.commit()
    
    return {
        "secret": secret,
        "qr_code": qr_code,
        "manual_entry_key": secret
    }

@router.post("/verify/totp")
async def verify_totp_setup(
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verificar configuración TOTP"""
    
    if not current_user.mfa_secret:
        raise HTTPException(status_code=400, detail="TOTP no configurado")
    
    if not MFAService.verify_totp_code(current_user.mfa_secret, code):
        raise HTTPException(status_code=400, detail="Código inválido")
    
    # Habilitar MFA
    current_user.mfa_enabled = True
    db.commit()
    
    return {"message": "TOTP configurado exitosamente"}

@router.post("/send/sms")
async def send_sms_code(
    phone: str,
    current_user: User = Depends(get_current_user)
):
    """Enviar código SMS (simulado)"""
    
    code = MFAService.generate_sms_code()
    
    # En producción, usarías un servicio como Twilio
    print(f"Código SMS para {phone}: {code}")
    
    return {"message": "Código SMS enviado"}

@router.post("/send/email")
async def send_email_code(
    current_user: User = Depends(get_current_user)
):
    """Enviar código por email"""
    
    code = MFAService.generate_email_code()
    
    # En producción, usarías un servicio de email
    print(f"Código email para {current_user.email}: {code}")
    
    return {"message": "Código enviado por email"}

@router.post("/verify/code")
async def verify_mfa_code(
    code: str,
    method: str,  # "totp", "sms", "email"
    current_user: User = Depends(get_current_user)
):
    """Verificar código MFA"""
    
    if method == "totp":
        if not current_user.mfa_secret:
            raise HTTPException(status_code=400, detail="TOTP no configurado")
        
        if not MFAService.verify_totp_code(current_user.mfa_secret, code):
            raise HTTPException(status_code=400, detail="Código TOTP inválido")
    
    elif method in ["sms", "email"]:
        # En producción, verificarías contra la base de datos
        # Por ahora, simulamos que cualquier código de 6 dígitos es válido
        if not code.isdigit() or len(code) != 6:
            raise HTTPException(status_code=400, detail="Código inválido")
    
    return {"message": "Código verificado exitosamente"}

@router.get("/status")
async def get_mfa_status(
    current_user: User = Depends(get_current_user)
):
    """Obtener estado de MFA"""
    return {
        "mfa_enabled": current_user.mfa_enabled,
        "totp_configured": bool(current_user.mfa_secret),
        "methods_available": ["totp", "sms", "email"]
    }
