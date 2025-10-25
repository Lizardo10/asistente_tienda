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
from app.routers import chat_enhanced  # Chat mejorado con OpenAI, audio e imágenes
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
    title="Asistente Tienda — Chat Inteligente",
    version="2.0.0",
    description="Sistema de chat inteligente con OpenAI, audio e imágenes",
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
app.include_router(chat_enhanced.router)  # Chat mejorado con OpenAI, audio e imágenes


# WebSocket endpoint modernizado
from fastapi import WebSocket, WebSocketDisconnect
from sqlmodel import Session
from app.models_sqlmodel.chat import Chat, ChatMessage
from app.use_cases.chat_use_cases import ChatUseCases
from app.repositories.chat_repository import ChatRepository
from app.services.rag_service import rag_service

@app.websocket("/ws/test")
async def websocket_test(websocket: WebSocket):
    """WebSocket de prueba simple"""
    print("🔌 WebSocket de prueba conectado")
    await websocket.accept()
    print("✅ WebSocket de prueba aceptado")
    
    try:
        await websocket.send_text("¡Hola! WebSocket funcionando")
        print("📤 Mensaje de prueba enviado")
        
        while True:
            data = await websocket.receive_text()
            print(f"📨 Mensaje recibido: '{data}'")
            await websocket.send_text(f"Echo: {data}")
            print(f"📤 Echo enviado: {data}")
            
    except WebSocketDisconnect:
        print("🔌 Cliente desconectado del WebSocket de prueba")
        return
    except Exception as e:
        print(f"❌ Error en WebSocket de prueba: {e}")
        return

@app.websocket("/ws/simple")
async def websocket_simple(websocket: WebSocket):
    """WebSocket completamente simple"""
    print("🔌 WebSocket SIMPLE conectado")
    await websocket.accept()
    print("✅ WebSocket SIMPLE aceptado")
    
    try:
        await websocket.send_text("¡Hola! WebSocket simple funcionando")
        print("📤 Mensaje simple enviado")
        
        while True:
            data = await websocket.receive_text()
            print(f"📨 Mensaje recibido: '{data}'")
            await websocket.send_text(f"Echo simple: {data}")
            print(f"📤 Echo simple enviado: {data}")
            
    except WebSocketDisconnect:
        print("🔌 Cliente desconectado del WebSocket SIMPLE")
        return
    except Exception as e:
        print(f"❌ Error en WebSocket SIMPLE: {e}")
        return

async def websocket_support_new(websocket: WebSocket):
    """WebSocket completamente nuevo para soporte en tiempo real con RAG"""
    print("🔌 WebSocket NUEVO conectado")
    await websocket.accept()
    print("✅ WebSocket NUEVO aceptado")
    
    try:
        # Enviar mensaje de bienvenida
        welcome_message = {
            "type": "chat_opened",
            "chat_id": 1,
            "features": {
                "ai_powered": True,
                "cache_optimized": True,
                "real_time": True,
                "intent_analysis": True
            },
            "message": "¡Hola! Soy tu asistente virtual de Asistente Tienda. ¿En qué puedo ayudarte hoy?"
        }
        await websocket.send_json(welcome_message)
        print("📤 Mensaje de bienvenida enviado")
        
        while True:
            data = await websocket.receive_text()
            print(f"📨 Mensaje recibido: '{data}'")
            
            try:
                # Procesar mensaje usando RAG
                print("🤖 Iniciando procesamiento RAG...")
                
                # Generar respuesta usando RAG
                print("🧠 Generando respuesta RAG...")
                rag_response = await rag_service.generate_response(data)
                print(f"✅ Respuesta RAG: {rag_response[:100]}...")
                
                # Obtener recomendaciones de productos
                print("🛍️ Obteniendo recomendaciones...")
                recommendations = await rag_service.get_recommendations(data)
                print(f"✅ Recomendaciones: {len(recommendations)} productos")
                
                # Crear respuesta estructurada
                response_data = {
                    "type": "bot",
                    "message": rag_response,
                    "recommendations": recommendations,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await websocket.send_json(response_data)
                print(f"📤 Respuesta enviada con {len(recommendations)} recomendaciones")
                
            except Exception as e:
                print(f"❌ Error procesando mensaje: {e}")
                error_response = {
                    "type": "error",
                    "message": f"Lo siento, hubo un error procesando tu consulta: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                await websocket.send_json(error_response)
            
    except WebSocketDisconnect:
        print("🔌 Cliente desconectado del WebSocket NUEVO")
        return
    except Exception as e:
        print(f"❌ Error en WebSocket NUEVO: {e}")
        await websocket.close(code=1011, reason="Error interno del servidor")
        return

async def websocket_support(websocket: WebSocket):
    """WebSocket simplificado para soporte en tiempo real con RAG"""
    print("🔌 WebSocket conectado")
    await websocket.accept()
    print("✅ WebSocket aceptado")
    
    try:
        # Enviar mensaje de bienvenida
        welcome_message = {
            "type": "chat_opened",
            "chat_id": 1,
            "features": {
                "ai_powered": True,
                "cache_optimized": True,
                "real_time": True,
                "intent_analysis": True
            },
            "message": "¡Hola! Soy tu asistente virtual de Asistente Tienda. ¿En qué puedo ayudarte hoy?"
        }
        await websocket.send_json(welcome_message)
        print("📤 Mensaje de bienvenida enviado")
        
        while True:
            data = await websocket.receive_text()
            print(f"📨 Mensaje recibido: '{data}'")
            
            try:
                # Procesar mensaje usando RAG
                print("🤖 Iniciando procesamiento RAG...")
                
                # Generar respuesta usando RAG
                print("🧠 Generando respuesta RAG...")
                rag_response = await rag_service.generate_response(data)
                print(f"✅ Respuesta RAG: {rag_response[:100]}...")
                
                # Obtener recomendaciones de productos
                print("🛍️ Obteniendo recomendaciones...")
                recommendations = await rag_service.get_recommendations(data)
                print(f"✅ Recomendaciones: {len(recommendations)} productos")
                
                # Crear respuesta estructurada
                response_data = {
                    "type": "bot",
                    "message": rag_response,
                    "recommendations": recommendations,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await websocket.send_json(response_data)
                print(f"📤 Respuesta enviada con {len(recommendations)} recomendaciones")
                
            except Exception as e:
                print(f"❌ Error procesando mensaje: {e}")
                error_response = {
                    "type": "error",
                    "message": f"Lo siento, hubo un error procesando tu consulta: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                await websocket.send_json(error_response)
            
    except WebSocketDisconnect:
        print("🔌 Cliente desconectado del WebSocket")
        return
    except Exception as e:
        print(f"❌ Error en WebSocket: {e}")
        await websocket.close(code=1011, reason="Error interno del servidor")
        return


@app.get("/test-rag")
async def test_rag_endpoint(query: str = "camiseta"):
    """Endpoint de prueba para verificar el RAG"""
    try:
        print(f"Probando RAG con query: {query}")
        
        # Generar respuesta usando RAG
        rag_response = await rag_service.generate_response(query)
        print(f"Respuesta RAG: {rag_response}")
        
        # Obtener recomendaciones de productos
        recommendations = await rag_service.get_recommendations(query)
        print(f"Recomendaciones: {len(recommendations)}")
        
        return {
            "query": query,
            "response": rag_response,
            "recommendations": recommendations,
            "recommendations_count": len(recommendations)
        }
    except Exception as e:
        print(f"Error en test-rag: {e}")
        return {"error": str(e)}

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
        "name": "Asistente Tienda — Chat Inteligente",
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