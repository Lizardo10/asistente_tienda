"""
Script de inicialización modernizado para la base de datos
"""
import asyncio
from app.database import create_db_and_tables
from app.core.config import settings
from app.services.simple_cache_service import cache_service
# from app.services.ai_service import ai_service


async def init_database():
    """Inicializa la base de datos y servicios"""
    print("🚀 Inicializando base de datos moderna...")
    
    # Crear tablas
    create_db_and_tables()
    print("✅ Tablas creadas exitosamente")
    
    # Conectar a Redis
    await cache_service.connect()
    print("✅ Cache Redis conectado")
    
    # Verificar servicios de IA
    # if ai_service.client:
    #     print("✅ Servicio de IA inicializado")
    # else:
    #     print("⚠️ Servicio de IA en modo simulado")
    print("✅ Servicios básicos inicializados")
    
    print("🎉 Inicialización completada exitosamente!")


if __name__ == "__main__":
    asyncio.run(init_database())
