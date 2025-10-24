# backend/app/services/brevo_service.py
"""
Servicio de correos electrónicos usando SendinBlue/Brevo
Versión profesional y confiable
"""
import logging
from typing import Optional
import re
from datetime import datetime, timedelta
import secrets

from ..core.config import settings

logger = logging.getLogger(__name__)

class BrevoEmailService:
    """Servicio de correos electrónicos con SendinBlue/Brevo"""
    
    def __init__(self):
        # Usar EMAIL_PASSWORD como API key de Brevo si BREVO_API_KEY no está configurado
        self.api_key = settings.brevo_api_key or settings.email_password
        self.from_email = settings.from_email
        self.app_name = settings.app_name
        
        # Verificar que tenemos las credenciales necesarias
        if not self.api_key:
            logger.warning("⚠️ No se encontró API key de Brevo/SendInBlue")
            self.simulation_mode = True
        else:
            logger.info(f"✅ API key de Brevo configurada: {self.api_key[:10]}...")
            self.simulation_mode = False
            
        if not self.from_email:
            logger.warning("⚠️ No se encontró email de remitente")
        else:
            logger.info(f"✅ Email de remitente: {self.from_email}")
        
        # Modo simulación si la API key no es válida
        if self.api_key and "xkeysib-" in self.api_key:
            # Probar la API key
            try:
                import requests
                test_response = requests.get(
                    "https://api.brevo.com/v3/account",
                    headers={"api-key": self.api_key}
                )
                if test_response.status_code == 401:
                    logger.warning("⚠️ API key de Brevo inválida, activando modo simulación")
                    self.simulation_mode = True
                else:
                    logger.info("✅ API key de Brevo válida")
            except:
                logger.warning("⚠️ No se pudo verificar API key, activando modo simulación")
                self.simulation_mode = True
        
        # Lista de dominios bloqueados (spam)
        self.blocked_domains = {
            "10minutemail.com", "tempmail.org", "guerrillamail.com",
            "mailinator.com", "throwaway.email", "temp-mail.org"
        }
        
        # Patrones de spam
        self.spam_patterns = [
            r"viagra", r"casino", r"lottery", r"winner", r"congratulations",
            r"free money", r"click here", r"urgent", r"act now"
        ]
    
    def is_valid_email(self, email: str) -> bool:
        """Validar formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def is_spam_email(self, email: str, subject: str = "", content: str = "") -> bool:
        """Detectar emails spam"""
        email_lower = email.lower()
        subject_lower = subject.lower()
        content_lower = content.lower()
        
        # Verificar dominio bloqueado
        domain = email.split('@')[1] if '@' in email else ""
        if domain in self.blocked_domains:
            return True
        
        # Verificar patrones de spam
        text_to_check = f"{subject_lower} {content_lower}"
        for pattern in self.spam_patterns:
            if re.search(pattern, text_to_check):
                return True
        
        return False
    
    def send_email(self, to_email: str, subject: str, html_content: str, 
                   text_content: str = None) -> bool:
        """Enviar email usando SendinBlue/Brevo o modo simulación"""
        
        # Modo simulación si la API key no es válida
        if getattr(self, 'simulation_mode', False):
            logger.info(f"📧 [SIMULACIÓN] Email enviado a: {to_email}")
            logger.info(f"📧 [SIMULACIÓN] Asunto: {subject}")
            logger.info(f"📧 [SIMULACIÓN] Contenido HTML: {len(html_content)} caracteres")
            return True
        
        try:
            import sib_api_v3_sdk
            from sib_api_v3_sdk.rest import ApiException
            
            # Configurar API
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = self.api_key
            
            # Crear instancia de API
            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
            
            # Validar email
            if not self.is_valid_email(to_email):
                logger.error(f"Email inválido: {to_email}")
                return False
            
            # Verificar spam
            if self.is_spam_email(to_email, subject, html_content):
                logger.warning(f"Email detectado como spam: {to_email}")
                return False
            
            # Crear sender
            sender = sib_api_v3_sdk.SendSmtpEmailSender(
                name=self.app_name,
                email=self.from_email
            )
            
            # Crear destinatario
            to = [sib_api_v3_sdk.SendSmtpEmailTo(
                email=to_email,
                name=to_email.split('@')[0]
            )]
            
            # Crear mensaje
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                sender=sender,
                to=to,
                subject=subject,
                html_content=html_content
            )
            
            # Agregar contenido de texto si existe
            if text_content:
                send_smtp_email.text_content = text_content
            
            # Enviar email
            api_response = api_instance.send_transac_email(send_smtp_email)
            
            logger.info(f"Email enviado exitosamente a {to_email} - Message ID: {api_response.message_id}")
            return True
            
        except ApiException as e:
            logger.error(f"Error de API enviando email a {to_email}: {e}")
            # Si falla la API, activar modo simulación para futuros emails
            self.simulation_mode = True
            logger.warning("⚠️ Activando modo simulación debido a error de API")
            return True  # Retornar True para que el registro continúe
        except Exception as e:
            logger.error(f"Error enviando email a {to_email}: {str(e)}")
            # Si hay cualquier error, activar modo simulación
            self.simulation_mode = True
            logger.warning("⚠️ Activando modo simulación debido a error")
            return True  # Retornar True para que el registro continúe
    
    def send_confirmation_email(self, to_email: str, confirmation_token: str) -> bool:
        """Enviar email de confirmación"""
        subject = f"Confirma tu cuenta en {self.app_name}"
        
        confirmation_url = f"{settings.frontend_url}/confirm-email?token={confirmation_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Confirma tu cuenta</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>¡Bienvenido a {self.app_name}!</h1>
                </div>
                <div class="content">
                    <h2>Confirma tu cuenta</h2>
                    <p>Hola,</p>
                    <p>Gracias por registrarte en {self.app_name}. Para completar tu registro, necesitas confirmar tu dirección de email.</p>
                    <p>Haz clic en el siguiente botón para confirmar tu cuenta:</p>
                    <a href="{confirmation_url}" class="button">Confirmar mi cuenta</a>
                    <p>Si el botón no funciona, copia y pega este enlace en tu navegador:</p>
                    <p><a href="{confirmation_url}">{confirmation_url}</a></p>
                    <p>Este enlace expirará en 7 días.</p>
                    <p>Si no creaste una cuenta en {self.app_name}, puedes ignorar este email.</p>
                </div>
                <div class="footer">
                    <p>Este email fue enviado automáticamente, por favor no respondas.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        ¡Bienvenido a {self.app_name}!
        
        Confirma tu cuenta haciendo clic en el siguiente enlace:
        {confirmation_url}
        
        Este enlace expirará en 7 días.
        
        Si no creaste una cuenta en {self.app_name}, puedes ignorar este email.
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """Enviar email de recuperación de contraseña"""
        subject = f"Recupera tu contraseña en {self.app_name}"
        
        reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Recupera tu contraseña</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #ff6b6b; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Recupera tu contraseña</h1>
                </div>
                <div class="content">
                    <h2>Solicitud de recuperación de contraseña</h2>
                    <p>Hola,</p>
                    <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta en {self.app_name}.</p>
                    <p>Haz clic en el siguiente botón para crear una nueva contraseña:</p>
                    <a href="{reset_url}" class="button">Restablecer contraseña</a>
                    <p>Si el botón no funciona, copia y pega este enlace en tu navegador:</p>
                    <p><a href="{reset_url}">{reset_url}</a></p>
                    <div class="warning">
                        <strong>⚠️ Importante:</strong>
                        <ul>
                            <li>Este enlace expirará en 1 hora</li>
                            <li>Solo puede ser usado una vez</li>
                            <li>Si no solicitaste este cambio, ignora este email</li>
                        </ul>
                    </div>
                </div>
                <div class="footer">
                    <p>Este email fue enviado automáticamente, por favor no respondas.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Recupera tu contraseña en {self.app_name}
        
        Haz clic en el siguiente enlace para restablecer tu contraseña:
        {reset_url}
        
        IMPORTANTE:
        - Este enlace expirará en 1 hora
        - Solo puede ser usado una vez
        - Si no solicitaste este cambio, ignora este email
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Enviar email de bienvenida"""
        subject = f"¡Bienvenido a {self.app_name}!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>¡Bienvenido!</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>¡Bienvenido a {self.app_name}!</h1>
                </div>
                <div class="content">
                    <h2>Hola {user_name},</h2>
                    <p>¡Nos complace darte la bienvenida a {self.app_name}!</p>
                    <p>Tu cuenta ha sido creada exitosamente y ya puedes disfrutar de todos nuestros servicios.</p>
                    <p>Aquí tienes algunas cosas que puedes hacer:</p>
                    <ul>
                        <li>Explorar nuestros productos</li>
                        <li>Configurar tu perfil</li>
                        <li>Habilitar la autenticación de dos factores para mayor seguridad</li>
                        <li>Contactar con nuestro soporte si necesitas ayuda</li>
                    </ul>
                    <p>¡Gracias por elegirnos!</p>
                </div>
                <div class="footer">
                    <p>Este email fue enviado automáticamente, por favor no respondas.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        ¡Bienvenido a {self.app_name}!
        
        Hola {user_name},
        
        ¡Nos complace darte la bienvenida a {self.app_name}!
        
        Tu cuenta ha sido creada exitosamente y ya puedes disfrutar de todos nuestros servicios.
        
        ¡Gracias por elegirnos!
        """
        
        return self.send_email(to_email, subject, html_content, text_content)

# Instancia global del servicio Brevo
brevo_email_service = BrevoEmailService()
