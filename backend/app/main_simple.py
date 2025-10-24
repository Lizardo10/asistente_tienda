"""
Aplicación FastAPI con Clean Architecture + Nuevas Tecnologías
Manteniendo tu PostgreSQL y OpenAI intactos
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db import engine, Base
from app.services.simple_cache_service import cache_service

# Importar routers con Clean Architecture
from app.routers import products, auth, orders, chat
from app.routers import modern_chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    print("🚀 Iniciando aplicación...")
    
    # Crear tablas de base de datos
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos inicializada")
    
    # Conectar a cache
    await cache_service.connect()
    print("✅ Cache Redis inicializado")
    
    yield
    
    # Shutdown
    print("🔄 Cerrando aplicación...")
    await cache_service.disconnect()
    print("✅ Aplicación cerrada correctamente")

# Crear aplicación FastAPI
app = FastAPI(
    title="Tienda Online - Backend Simplificado",
    description="Backend modernizado con Clean Architecture",
    version="2.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(chat.router)
app.include_router(modern_chat.router)

# Endpoint de salud
@app.get("/health")
async def health_check():
    """Endpoint de salud"""
    return {
        "status": "ok",
        "message": "Backend modernizado funcionando correctamente",
        "version": "2.0.0"
    }

# WebSocket endpoint
@app.websocket("/ws/support")
async def websocket_endpoint(websocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Aquí puedes agregar la lógica del WebSocket si la necesitas
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")

# Endpoint raíz
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "¡Bienvenido a la Tienda Online!",
        "docs": "/docs",
        "health": "/health",
        "products": "/products"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
