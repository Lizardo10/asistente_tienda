# backend/app/services/mfa_service.py
"""
Servicio de Multi-Factor Authentication (MFA)
Incluye TOTP, SMS y Email
"""
import pyotp
import qrcode
import io
import base64
import secrets
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MFAService:
    """Servicio de Multi-Factor Authentication"""
    
    @staticmethod
    def generate_totp_secret() -> str:
        """Generar secreto TOTP"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_totp_qr(secret: str, email: str, app_name: str = "Tu Tienda") -> str:
        """Generar QR code para TOTP"""
        try:
            # Crear URI para TOTP
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=email,
                issuer_name=app_name
            )
            
            # Generar QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            # Crear imagen
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir a base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Codificar en base64
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"Error generando QR code: {str(e)}")
            return ""
    
    @staticmethod
    def verify_totp_code(secret: str, code: str) -> bool:
        """Verificar código TOTP"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(code, valid_window=1)  # Permitir 1 ventana de tiempo
        except Exception as e:
            logger.error(f"Error verificando código TOTP: {str(e)}")
            return False
    
    @staticmethod
    def generate_totp_code(secret: str) -> str:
        """Generar código TOTP actual"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.now()
        except Exception as e:
            logger.error(f"Error generando código TOTP: {str(e)}")
            return ""
    
    @staticmethod
    def generate_sms_code() -> str:
        """Generar código SMS de 6 dígitos"""
        return f"{secrets.randbelow(900000) + 100000:06d}"
    
    @staticmethod
    def generate_email_code() -> str:
        """Generar código de email de 6 dígitos"""
        return f"{secrets.randbelow(900000) + 100000:06d}"
    
    @staticmethod
    def generate_backup_codes(count: int = 10) -> list[str]:
        """Generar códigos de respaldo"""
        codes = []
        for _ in range(count):
            code = secrets.token_urlsafe(8).upper()
            codes.append(code)
        return codes
    
    @staticmethod
    def verify_backup_code(backup_codes: list[str], code: str) -> bool:
        """Verificar código de respaldo"""
        try:
            return code.upper() in backup_codes
        except Exception as e:
            logger.error(f"Error verificando código de respaldo: {str(e)}")
            return False
    
    @staticmethod
    def remove_backup_code(backup_codes: list[str], code: str) -> list[str]:
        """Remover código de respaldo usado"""
        try:
            return [c for c in backup_codes if c != code.upper()]
        except Exception as e:
            logger.error(f"Error removiendo código de respaldo: {str(e)}")
            return backup_codes
    
    @staticmethod
    def get_totp_remaining_time() -> int:
        """Obtener tiempo restante para el próximo código TOTP"""
        try:
            # TOTP cambia cada 30 segundos
            return 30 - (datetime.now().second % 30)
        except Exception as e:
            logger.error(f"Error obteniendo tiempo restante: {str(e)}")
            return 30
    
    @staticmethod
    def validate_mfa_setup(secret: str, code: str) -> Dict[str, Any]:
        """Validar configuración MFA"""
        try:
            is_valid = MFAService.verify_totp_code(secret, code)
            
            return {
                "valid": is_valid,
                "message": "Código válido" if is_valid else "Código inválido",
                "remaining_time": MFAService.get_totp_remaining_time()
            }
            
        except Exception as e:
            logger.error(f"Error validando configuración MFA: {str(e)}")
            return {
                "valid": False,
                "message": "Error validando código",
                "remaining_time": 30
            }

# Instancia global del servicio MFA
mfa_service = MFAService()



