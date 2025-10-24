import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Define lo que necesitas sí o sí:
    DATABASE_URL: str = "sqlite:///./tienda.db"

    # Permite variables extra del .env (JWT_SECRET, etc) sin que falle
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",         # 👈 clave para que no truene con extras
    )
    
settings = Settings()
DATABASE_URL = settings.DATABASE_URL  # ← tomará el valor de .env si existe

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
