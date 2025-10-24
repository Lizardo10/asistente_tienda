"""
Servicio de notificaciones moderno
Siguiendo el principio de Single Responsibility (SOLID)
"""
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
from datetime import datetime


class NotificationType(Enum):
    """Tipos de notificaciones"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBSOCKET = "websocket"


class NotificationPriority(Enum):
    """Prioridades de notificación"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Notification:
    """Modelo de notificación"""
    id: str
    type: NotificationType
    recipient: str
    subject: str
    content: str
    priority: NotificationPriority
    created_at: datetime
    sent_at: Optional[datetime] = None
    status: str = "pending"  # pending, sent, failed


class NotificationServiceInterface(ABC):
    """Interface para el servicio de notificaciones - Dependency Inversion Principle"""
    
    @abstractmethod
    async def send_notification(self, notification: Notification) -> bool:
        pass
    
    @abstractmethod
    async def send_bulk_notifications(self, notifications: List[Notification]) -> Dict[str, Any]:
        pass


class NotificationService(NotificationServiceInterface):
    """Implementación del servicio de notificaciones"""
    
    def __init__(self):
        self.notification_queue = asyncio.Queue()
        self.is_processing = False
    
    async def send_notification(self, notification: Notification) -> bool:
        """Envía una notificación individual"""
        try:
            if notification.type == NotificationType.EMAIL:
                return await self._send_email(notification)
            elif notification.type == NotificationType.SMS:
                return await self._send_sms(notification)
            elif notification.type == NotificationType.PUSH:
                return await self._send_push(notification)
            elif notification.type == NotificationType.WEBSOCKET:
                return await self._send_websocket(notification)
            else:
                print(f"Tipo de notificación no soportado: {notification.type}")
                return False
                
        except Exception as e:
            print(f"Error enviando notificación {notification.id}: {e}")
            return False
    
    async def send_bulk_notifications(self, notifications: List[Notification]) -> Dict[str, Any]:
        """Envía múltiples notificaciones"""
        results = {
            "total": len(notifications),
            "sent": 0,
            "failed": 0,
            "errors": []
        }
        
        for notification in notifications:
            try:
                success = await self.send_notification(notification)
                if success:
                    results["sent"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Failed to send notification {notification.id}")
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Error sending notification {notification.id}: {str(e)}")
        
        return results
    
    async def _send_email(self, notification: Notification) -> bool:
        """Envía notificación por email"""
        # TODO: Implementar integración con SendGrid o similar
        print(f"📧 Enviando email a {notification.recipient}: {notification.subject}")
        await asyncio.sleep(0.1)  # Simular envío
        return True
    
    async def _send_sms(self, notification: Notification) -> bool:
        """Envía notificación por SMS"""
        # TODO: Implementar integración con Twilio
        print(f"📱 Enviando SMS a {notification.recipient}: {notification.content}")
        await asyncio.sleep(0.1)  # Simular envío
        return True
    
    async def _send_push(self, notification: Notification) -> bool:
        """Envía notificación push"""
        # TODO: Implementar integración con Firebase Cloud Messaging
        print(f"🔔 Enviando push notification a {notification.recipient}: {notification.content}")
        await asyncio.sleep(0.1)  # Simular envío
        return True
    
    async def _send_websocket(self, notification: Notification) -> bool:
        """Envía notificación por WebSocket"""
        # TODO: Implementar envío por WebSocket
        print(f"🔌 Enviando WebSocket notification a {notification.recipient}: {notification.content}")
        await asyncio.sleep(0.1)  # Simular envío
        return True


# Instancia global del servicio de notificaciones
notification_service = NotificationService()
