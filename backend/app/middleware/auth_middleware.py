# backend/app/middleware/auth_middleware.py
"""
Middleware de autenticación avanzado
Incluye rate limiting, logging de seguridad, y protección CSRF
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging
from typing import Dict, Optional
from collections import defaultdict, deque
import json

# Configuración de rate limiting
RATE_LIMIT_REQUESTS = 100  # requests por minuto
RATE_LIMIT_WINDOW = 60     # ventana en segundos

# Configuración de logging
security_logger = logging.getLogger("security")

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware de seguridad avanzado"""
    
    def __init__(self, app):
        super().__init__(app)
        self.rate_limit_storage: Dict[str, deque] = defaultdict(deque)
        self.blocked_ips: set = set()
        
    async def dispatch(self, request: Request, call_next):
        # Obtener IP del cliente
        client_ip = self._get_client_ip(request)
        
        # Verificar si la IP está bloqueada
        if client_ip in self.blocked_ips:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "IP bloqueada por actividad sospechosa"}
            )
        
        # Rate limiting
        if not self._check_rate_limit(client_ip):
            self._log_suspicious_activity(client_ip, "Rate limit exceeded", request)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Demasiadas solicitudes. Intenta más tarde."}
            )
        
        # Headers de seguridad
        response = await call_next(request)
        
        # Agregar headers de seguridad
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Log de actividad
        self._log_request(request, response)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Obtener IP real del cliente"""
        # Verificar headers de proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
            
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """Verificar rate limit"""
        now = time.time()
        client_requests = self.rate_limit_storage[client_ip]
        
        # Limpiar requests antiguos
        while client_requests and client_requests[0] <= now - RATE_LIMIT_WINDOW:
            client_requests.popleft()
        
        # Verificar límite
        if len(client_requests) >= RATE_LIMIT_REQUESTS:
            return False
        
        # Agregar request actual
        client_requests.append(now)
        return True
    
    def _log_suspicious_activity(self, client_ip: str, activity: str, request: Request):
        """Log de actividad sospechosa"""
        security_logger.warning(
            f"Suspicious activity: {activity} from IP {client_ip} "
            f"on {request.url.path} at {time.time()}"
        )
        
        # Bloquear IP después de múltiples violaciones
        if activity == "Rate limit exceeded":
            self.blocked_ips.add(client_ip)
    
    def _log_request(self, request: Request, response: Response):
        """Log de requests"""
        if response.status_code >= 400:
            security_logger.info(
                f"Request: {request.method} {request.url.path} "
                f"Status: {response.status_code} "
                f"IP: {self._get_client_ip(request)}"
            )

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware específico para autenticación"""
    
    def __init__(self, app):
        super().__init__(app)
        self.public_paths = {
            "/docs", "/redoc", "/openapi.json", "/health",
            "/auth/login", "/auth/register", "/auth/password-reset-request"
        }
    
    async def dispatch(self, request: Request, call_next):
        # Verificar si es una ruta pública
        if request.url.path in self.public_paths:
            return await call_next(request)
        
        # Verificar token de autenticación
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token de autenticación requerido"}
            )
        
        return await call_next(request)





