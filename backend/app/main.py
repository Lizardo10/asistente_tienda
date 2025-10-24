"""
Aplicación principal modernizada con Clean Architecture
Siguiendo los principios SOLID y manteniendo compatibilidad
"""
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import os
import traceback
from contextlib import asynccontextmanager

# Importar configuración centralizada
from app.core.config import settings

# Importar base de datos
from app.database import create_db_and_tables, get_db

# Importar servicios
from app.services.simple_cache_service import cache_service
from app.services.ai_service import ai_service
from app.services.huggingface_image_service import huggingface_image_service

# Importar routers existentes (mantener compatibilidad)
from app.routers import auth, auth_enhanced, auth_complete
# from app.routers import mfa_service  # Comentado temporalmente
from app.routers import products
from app.routers import orders, chat, modern_chat
from app.routers import accounting_basic as accounting  # Área contable básica
from app.routers import image_search  # Búsqueda por imagen
from app.routers import recommendations  # Sistema de recomendaciones
from app.routers import checkout
from app.routers.checkout_sqlalchemy_fixed import router as checkout_sqlalchemy_router  # Sistema de checkout y pagos
from app.routers import audio  # Procesamiento de audio con IA
from app.routers import chat_history  # Historial de conversaciones
from app.routers import simple_processing  # Procesamiento simple
from app.routers import admin_financial  # Panel de administración financiera
from app.routers import invoices  # Sistema de facturas
from app.routers import balance  # Gestión de saldo
from app.routers import admin_users  # Gestión de usuarios por administradores
from app.routers import admin_accounts  # Gestión de cuentas y saldos
from app.routers import realtime  # Actualizaciones en tiempo real
from app.routers import cart_management  # Gestión del carrito
from app.routers import cart_clear_improved  # Limpieza mejorada del carrito
from app.routers import huggingface_test  # Pruebas de Hugging Face
from app.routers.auth import get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    print("🚀 Iniciando aplicación...")
    
    # Crear tablas de base de datos
    create_db_and_tables()
    print("✅ Base de datos inicializada")
    
    # Conectar a Redis
    await cache_service.connect()
    print("✅ Cache Redis inicializado")
    
    # Verificar servicios de IA
    if hasattr(ai_service, 'client') and ai_service.client:
        print("✅ Servicio de IA inicializado")
    else:
        print("⚠️ Servicio de IA en modo simulado")
    print("✅ Servicios básicos inicializados")
    
    yield
    
    # Shutdown
    print("🔄 Cerrando aplicación...")
    await cache_service.disconnect()
    print("✅ Aplicación cerrada correctamente")


# Crear aplicación FastAPI
app = FastAPI(
    title="Asistente de Soporte — Tienda Online",
    version="2.0.0",
    description="Aplicación modernizada con Clean Architecture y principios SOLID",
    lifespan=lifespan
)


# -- Manejo global de excepciones --
@app.exception_handler(Exception)
async def all_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(status_code=500, content={"detail": str(exc)})


# -- CORS --
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -- Routers (Sistema completo con correos) --
# app.include_router(auth.router)  # Sistema básico (comentado)
# app.include_router(auth_enhanced.router)  # Sistema mejorado (comentado)
app.include_router(auth_complete.router)  # Sistema completo con email y MFA
# app.include_router(mfa_service.router)  # MFA (comentado temporalmente)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(chat.router)
app.include_router(modern_chat.router)
app.include_router(accounting.router)  # Área contable
app.include_router(image_search.router)  # Búsqueda por imagen
app.include_router(image_search.image_search_router)  # Búsqueda por imagen para frontend
app.include_router(recommendations.router)  # Sistema de recomendaciones
app.include_router(checkout.router)  # Sistema de checkout y pagos
app.include_router(checkout_sqlalchemy_router)  # Sistema de checkout SQLAlchemy
app.include_router(chat_history.router)  # Historial de conversaciones (admin)
app.include_router(chat_history.public_router)  # Historial de conversaciones (público)
app.include_router(audio.router)  # Procesamiento de audio con IA
app.include_router(simple_processing.router)  # Procesamiento simple
app.include_router(admin_financial.router)  # Panel de administración financiera
app.include_router(invoices.router)  # Sistema de facturas
app.include_router(balance.router)  # Gestión de saldo
app.include_router(admin_users.router)  # Gestión de usuarios por administradores
app.include_router(admin_accounts.router)  # Gestión de cuentas y saldos
app.include_router(realtime.router)  # Actualizaciones en tiempo real
app.include_router(cart_management.router)  # Gestión del carrito
app.include_router(cart_clear_improved.router)  # Limpieza mejorada del carrito
app.include_router(huggingface_test.router)  # Pruebas de Hugging Face


# WebSocket endpoint modernizado
from fastapi import WebSocket, WebSocketDisconnect
from sqlmodel import Session
from app.models_sqlmodel.chat import Chat, ChatMessage
from app.use_cases.chat_use_cases import ChatUseCases
from app.repositories.chat_repository import ChatRepository

@app.websocket("/ws/support")
async def websocket_support(websocket: WebSocket, db: Session = Depends(get_db)):
    """WebSocket modernizado para soporte en tiempo real"""
    await websocket.accept()
    
    try:
        # Inicializar casos de uso
        chat_repository = ChatRepository(db)
        chat_use_cases = ChatUseCases(chat_repository)
        
        # Crear chat
        chat = await chat_use_cases.create_chat()
        
        # Enviar mensaje de bienvenida
        welcome_message = {
            "type": "chat_opened",
            "chat_id": chat.id,
            "features": {
                "ai_powered": True,
                "cache_optimized": True,
                "real_time": True,
                "intent_analysis": True
            },
            "message": "¡Hola! Soy tu asistente virtual mejorado. ¿En qué puedo ayudarte hoy?"
        }
        await websocket.send_json(welcome_message)

        while True:
            data = await websocket.receive_text()
            print(f"Mensaje recibido en WebSocket: '{data}'")
            
            try:
                # Procesar mensaje usando casos de uso
                print("Iniciando procesamiento del mensaje...")
                response = await chat_use_cases.send_message(chat.id, data)
                print("Mensaje procesado exitosamente")
                
                # Enviar respuesta optimizada
                response_data = {
                    "type": "bot",
                    "message": response["response"],
                    "context": response["context"],
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await websocket.send_json(response_data)
                print("Respuesta enviada al cliente")
                
            except Exception as e:
                print(f"Error procesando mensaje en WebSocket: {e}")
                error_response = {
                    "type": "error",
                    "message": f"Lo siento, hubo un error procesando tu consulta: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                await websocket.send_json(error_response)
            
    except WebSocketDisconnect:
        # Cerrar chat
        if 'chat' in locals():
            await chat_use_cases.close_chat(chat.id)
        print("Cliente desconectado del WebSocket")
        return
    except Exception as e:
        print(f"Error en WebSocket: {e}")
        await websocket.close(code=1011, reason="Error interno del servidor")
        return


# -- Archivos estáticos (media) --
os.makedirs(settings.media_dir, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")


# -- Analytics del chat (solo para administradores) --
@app.get("/chat/analytics")
async def get_chat_analytics(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obtiene analytics del chat (solo administradores)"""
    # Verificar que el usuario sea administrador
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Solo los administradores pueden acceder a los analytics")
    
    # Usar casos de uso para obtener analytics
    chat_repository = ChatRepository(db)
    chat_use_cases = ChatUseCases(chat_repository)
    analytics = await chat_use_cases.get_chat_analytics()
    
    return {
        "status": "success",
        "analytics": analytics,
        "timestamp": datetime.now().isoformat()
    }


# -- Healthcheck mejorado --
@app.get("/health")
async def health():
    """Healthcheck con información de servicios"""
    cache_status = "connected" if cache_service.connected else "disconnected"
    ai_status = "connected" if hasattr(ai_service, 'client') and ai_service.client else "simulated"
    
    return {
        "status": "ok",
        "version": "2.0.0",
        "services": {
            "cache": cache_status,
            "ai": ai_status,
            "database": "connected"
        },
        "timestamp": datetime.now().isoformat()
    }


# -- Endpoint de información del sistema --
@app.get("/system/info")
async def system_info():
    """Información del sistema"""
    return {
        "name": "Asistente de Soporte — Tienda Online",
        "version": "2.0.0",
        "architecture": "Clean Architecture + SOLID",
        "features": [
            "FastAPI 0.115.0",
            "SQLModel + PostgreSQL",
            "Redis Stack Caching",
            "OpenAI GPT-4 Integration",
            "WebSocket Real-time",
            "Clean Architecture",
            "SOLID Principles"
        ],
        "timestamp": datetime.now().isoformat()
    }