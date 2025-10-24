"""
Módulo de base de datos - Abstracción de la capa de datos
Siguiendo el principio de Dependency Inversion (SOLID)
"""
from .connection import get_db, engine, create_db_and_tables
from .base import Base

__all__ = ["get_db", "engine", "Base", "create_db_and_tables"]
