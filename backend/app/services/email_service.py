# backend/app/services/email_service.py
"""
Servicio de correos electrónicos completo
Incluye confirmación, recuperación de contraseña y filtrado de spam
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List, Dict, Any
import os
import re
import logging
from datetime import datetime, timedelta
import secrets
import hashlib

from ..core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Servicio de correos electrónicos"""
    
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.email_user = settings.email_user
        self.email_password = settings.email_password
        self.from_email = settings.from_email or self.email_user
        self.app_name = settings.app_name
        
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
        """Enviar email"""
        try:
            # Validar email
            if not self.is_valid_email(to_email):
                logger.error(f"Email inválido: {to_email}")
                return False
            
            # Verificar spam
            if self.is_spam_email(to_email, subject, html_content):
                logger.warning(f"Email detectado como spam: {to_email}")
                return False
            
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Agregar contenido
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Enviar email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            logger.info(f"Email enviado exitosamente a {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email a {to_email}: {str(e)}")
            return False
    
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
                    <p>Este enlace expirará en 24 horas.</p>
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
        
        Este enlace expirará en 24 horas.
        
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
    
    def send_mfa_code_email(self, to_email: str, code: str) -> bool:
        """Enviar código MFA por email"""
        subject = f"Código de verificación - {self.app_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Código de verificación</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .code {{ background: #fff; border: 2px solid #4ecdc4; padding: 20px; text-align: center; font-size: 24px; font-weight: bold; color: #4ecdc4; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Código de verificación</h1>
                </div>
                <div class="content">
                    <h2>Tu código de verificación</h2>
                    <p>Hola,</p>
                    <p>Aquí está tu código de verificación para completar el proceso de autenticación:</p>
                    <div class="code">{code}</div>
                    <p>Este código expirará en 10 minutos.</p>
                    <p>Si no solicitaste este código, ignora este email.</p>
                </div>
                <div class="footer">
                    <p>Este email fue enviado automáticamente, por favor no respondas.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Código de verificación - {self.app_name}
        
        Tu código de verificación es: {code}
        
        Este código expirará en 10 minutos.
        
        Si no solicitaste este código, ignora este email.
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

# Instancia global del servicio de email
email_service = EmailService()
