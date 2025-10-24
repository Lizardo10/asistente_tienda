# backend/app/services/simple_email_service.py
"""
Servicio de email simple para desarrollo
Envía emails usando SMTP básico o simula el envío
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os

logger = logging.getLogger(__name__)

class SimpleEmailService:
    """Servicio de email simple para desarrollo"""
    
    def __init__(self):
        # Configuración básica para desarrollo
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_user = os.getenv('EMAIL_USER', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL_SMTP', self.email_user)
        self.app_name = os.getenv('APP_NAME', 'Tienda Online')
        self.frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5174')
        
        # Modo de desarrollo: si no hay credenciales, simular envío
        self.simulation_mode = not (self.email_user and self.email_password)
        
        if self.simulation_mode:
            logger.info("📧 Modo simulación de emails activado (sin credenciales SMTP)")
        else:
            logger.info(f"📧 Servicio de email configurado: {self.from_email}")
    
    def send_confirmation_email(self, email: str, confirmation_token: str) -> bool:
        """Enviar email de confirmación de cuenta"""
        try:
            confirmation_url = f"{self.frontend_url}/confirm-email?token={confirmation_token}"
            
            subject = f"Confirma tu cuenta en {self.app_name}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Confirmación de cuenta</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 ¡Bienvenido a {self.app_name}!</h1>
                    </div>
                    <div class="content">
                        <h2>Confirma tu cuenta</h2>
                        <p>Hola,</p>
                        <p>Gracias por registrarte en {self.app_name}. Para completar tu registro, necesitas confirmar tu dirección de email.</p>
                        
                        <p><strong>Haz clic en el botón de abajo para confirmar tu cuenta:</strong></p>
                        
                        <a href="{confirmation_url}" class="button">✅ Confirmar mi cuenta</a>
                        
                        <p>O copia y pega este enlace en tu navegador:</p>
                        <p style="word-break: break-all; background: #eee; padding: 10px; border-radius: 5px;">{confirmation_url}</p>
                        
                        <p><strong>¿No te registraste?</strong><br>
                        Si no creaste una cuenta en {self.app_name}, puedes ignorar este email de forma segura.</p>
                        
                        <p>¡Esperamos verte pronto!</p>
                        <p>El equipo de {self.app_name}</p>
                    </div>
                    <div class="footer">
                        <p>Este email fue enviado automáticamente, por favor no respondas.</p>
                        <p>© 2024 {self.app_name}. Todos los derechos reservados.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            ¡Bienvenido a {self.app_name}!
            
            Confirma tu cuenta haciendo clic en el siguiente enlace:
            {confirmation_url}
            
            Si no te registraste en {self.app_name}, puedes ignorar este email.
            
            ¡Esperamos verte pronto!
            El equipo de {self.app_name}
            """
            
            if self.simulation_mode:
                # Modo simulación: solo logear
                logger.info(f"📧 [SIMULACIÓN] Email de confirmación enviado a: {email}")
                logger.info(f"📧 [SIMULACIÓN] Token: {confirmation_token}")
                logger.info(f"📧 [SIMULACIÓN] URL: {confirmation_url}")
                return True
            else:
                # Envío real por SMTP
                return self._send_smtp_email(email, subject, html_content, text_content)
                
        except Exception as e:
            logger.error(f"❌ Error enviando email de confirmación: {e}")
            return False
    
    def send_password_reset_email(self, email: str, reset_token: str) -> bool:
        """Enviar email de recuperación de contraseña"""
        try:
            reset_url = f"{self.frontend_url}/reset-password?token={reset_token}"
            
            subject = f"Recupera tu contraseña en {self.app_name}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Recuperación de contraseña</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔐 Recuperación de contraseña</h1>
                    </div>
                    <div class="content">
                        <h2>Recupera tu contraseña</h2>
                        <p>Hola,</p>
                        <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta en {self.app_name}.</p>
                        
                        <p><strong>Haz clic en el botón de abajo para crear una nueva contraseña:</strong></p>
                        
                        <a href="{reset_url}" class="button">🔑 Restablecer contraseña</a>
                        
                        <p>O copia y pega este enlace en tu navegador:</p>
                        <p style="word-break: break-all; background: #eee; padding: 10px; border-radius: 5px;">{reset_url}</p>
                        
                        <p><strong>¿No solicitaste este cambio?</strong><br>
                        Si no solicitaste restablecer tu contraseña, puedes ignorar este email de forma segura.</p>
                        
                        <p>Este enlace expirará en 1 hora por seguridad.</p>
                        
                        <p>El equipo de {self.app_name}</p>
                    </div>
                    <div class="footer">
                        <p>Este email fue enviado automáticamente, por favor no respondas.</p>
                        <p>© 2024 {self.app_name}. Todos los derechos reservados.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            if self.simulation_mode:
                logger.info(f"📧 [SIMULACIÓN] Email de recuperación enviado a: {email}")
                logger.info(f"📧 [SIMULACIÓN] Token: {reset_token}")
                return True
            else:
                return self._send_smtp_email(email, subject, html_content, "")
                
        except Exception as e:
            logger.error(f"❌ Error enviando email de recuperación: {e}")
            return False
    
    def _send_smtp_email(self, to_email: str, subject: str, html_content: str, text_content: str) -> bool:
        """Enviar email usando SMTP"""
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Agregar contenido
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            if html_content:
                html_part = MIMEText(html_content, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Enviar email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"✅ Email enviado exitosamente a: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error SMTP: {e}")
            return False

# Instancia global del servicio
simple_email_service = SimpleEmailService()

