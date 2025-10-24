"""
Conexión a la base de datos usando SQLModel
Siguiendo el principio de Single Responsibility (SOLID)
"""
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.engine import Engine
from typing import Generator
from app.core.config import settings


# Crear motor de base de datos
engine: Engine = create_engine(
    settings.database_url,
    echo=False,  # Cambiar a True para debug
    pool_pre_ping=True,
    pool_recycle=300
)


def create_db_and_tables():
    """Crear tablas de la base de datos"""
    SQLModel.metadata.create_all(engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obtener sesión de base de datos
    Siguiendo el principio de Dependency Inversion (SOLID)
    """
    with Session(engine) as session:
        yield session
