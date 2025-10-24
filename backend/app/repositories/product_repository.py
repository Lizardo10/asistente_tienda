"""
Repositorio de productos siguiendo el patrón Repository
Siguiendo el principio de Single Responsibility (SOLID)
"""
from typing import Optional, List
from sqlmodel import Session, select, and_
from .base_repository import BaseRepository
from app.models_sqlmodel.product import Product, ProductImage


class ProductRepository(BaseRepository[Product]):
    """Repositorio para productos"""
    
    def __init__(self, session: Session):
        super().__init__(session, Product)
    
    async def get_active_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Obtiene productos activos"""
        statement = select(Product).where(Product.active == True).offset(skip).limit(limit)
        return self.session.exec(statement).all()
    
    async def get_by_price_range(self, min_price: float, max_price: float) -> List[Product]:
        """Obtiene productos por rango de precio"""
        statement = select(Product).where(
            and_(Product.price >= min_price, Product.price <= max_price, Product.active == True)
        )
        return self.session.exec(statement).all()
    
    async def search_products(self, query: str) -> List[Product]:
        """Busca productos por título o descripción"""
        statement = select(Product).where(
            and_(
                Product.active == True,
                or_(
                    Product.title.ilike(f"%{query}%"),
                    Product.description.ilike(f"%{query}%")
                )
            )
        )
        return self.session.exec(statement).all()
    
    async def get_featured_products(self, limit: int = 10) -> List[Product]:
        """Obtiene productos destacados"""
        # Por ahora retorna los productos más recientes
        statement = select(Product).where(Product.active == True).order_by(Product.created_at.desc()).limit(limit)
        return self.session.exec(statement).all()


class ProductImageRepository(BaseRepository[ProductImage]):
    """Repositorio para imágenes de productos"""
    
    def __init__(self, session: Session):
        super().__init__(session, ProductImage)
    
    async def get_by_product_id(self, product_id: int) -> List[ProductImage]:
        """Obtiene imágenes por producto"""
        statement = select(ProductImage).where(ProductImage.product_id == product_id)
        return self.session.exec(statement).all()
