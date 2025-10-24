"""
Base para todos los modelos usando SQLModel
Siguiendo el principio de Open/Closed (SOLID)
"""
from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional

# Base para todos los modelos
Base = SQLModel


class BaseModel(SQLModel):
    """Modelo base con campos comunes"""
    
    class Config:
        arbitrary_types_allowed = True


class TimestampMixin(SQLModel):
    """Mixin para agregar timestamps a los modelos"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
