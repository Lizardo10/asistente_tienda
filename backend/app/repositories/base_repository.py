"""
Repositorio base siguiendo el patrón Repository
Siguiendo el principio de Open/Closed (SOLID)
"""
from typing import TypeVar, Generic, List, Optional, Dict, Any
from sqlmodel import SQLModel, Session, select
from abc import ABC, abstractmethod

T = TypeVar('T', bound=SQLModel)


class BaseRepository(ABC, Generic[T]):
    """Repositorio base abstracto"""
    
    def __init__(self, session: Session, model_class: type[T]):
        self.session = session
        self.model_class = model_class
    
    async def create(self, obj_in: Dict[str, Any]) -> T:
        """Crea un nuevo objeto"""
        db_obj = self.model_class(**obj_in)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj
    
    async def get(self, id: int) -> Optional[T]:
        """Obtiene un objeto por ID"""
        return self.session.get(self.model_class, id)
    
    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Obtiene múltiples objetos con paginación"""
        statement = select(self.model_class).offset(skip).limit(limit)
        return self.session.exec(statement).all()
    
    async def update(self, id: int, obj_in: Dict[str, Any]) -> Optional[T]:
        """Actualiza un objeto"""
        db_obj = await self.get(id)
        if db_obj:
            for key, value in obj_in.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            self.session.add(db_obj)
            self.session.commit()
            self.session.refresh(db_obj)
        return db_obj
    
    async def delete(self, id: int) -> bool:
        """Elimina un objeto"""
        db_obj = await self.get(id)
        if db_obj:
            self.session.delete(db_obj)
            self.session.commit()
            return True
        return False
    
    async def count(self) -> int:
        """Cuenta el número total de objetos"""
        statement = select(self.model_class)
        return len(self.session.exec(statement).all())
    
    async def exists(self, id: int) -> bool:
        """Verifica si un objeto existe"""
        db_obj = await self.get(id)
        return db_obj is not None
