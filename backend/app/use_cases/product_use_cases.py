"""
Casos de uso para productos siguiendo Clean Architecture
Siguiendo el principio de Single Responsibility (SOLID)
"""
from typing import Dict, Any, Optional, List
from app.models_sqlmodel.product import Product, ProductCreate, ProductUpdate
from app.repositories.product_repository import ProductRepository, ProductImageRepository


class ProductUseCases:
    """Casos de uso para productos"""
    
    def __init__(self, product_repository: ProductRepository, image_repository: ProductImageRepository):
        self.product_repository = product_repository
        self.image_repository = image_repository
    
    async def create_product(self, product_data: ProductCreate) -> Product:
        """Crea un nuevo producto"""
        return await self.product_repository.create(product_data.dict())
    
    async def get_product(self, product_id: int) -> Optional[Product]:
        """Obtiene un producto por ID"""
        return await self.product_repository.get(product_id)
    
    async def get_all_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Obtiene todos los productos"""
        return await self.product_repository.get_multi(skip, limit)
    
    async def get_active_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Obtiene productos activos"""
        return await self.product_repository.get_active_products(skip, limit)
    
    async def update_product(self, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        """Actualiza un producto"""
        update_data = product_data.dict(exclude_unset=True)
        return await self.product_repository.update(product_id, update_data)
    
    async def delete_product(self, product_id: int) -> bool:
        """Elimina un producto"""
        return await self.product_repository.delete(product_id)
    
    async def search_products(self, query: str) -> List[Product]:
        """Busca productos por título o descripción"""
        return await self.product_repository.search_products(query)
    
    async def get_products_by_price_range(self, min_price: float, max_price: float) -> List[Product]:
        """Obtiene productos por rango de precio"""
        return await self.product_repository.get_by_price_range(min_price, max_price)
    
    async def get_featured_products(self, limit: int = 10) -> List[Product]:
        """Obtiene productos destacados"""
        return await self.product_repository.get_featured_products(limit)
    
    async def toggle_product_status(self, product_id: int) -> Optional[Product]:
        """Activa/desactiva un producto"""
        product = await self.product_repository.get(product_id)
        if product:
            return await self.product_repository.update(product_id, {"active": not product.active})
        return None
    
    async def add_product_image(self, product_id: int, image_url: str) -> bool:
        """Agrega una imagen a un producto"""
        try:
            image_data = {
                "product_id": product_id,
                "url": image_url
            }
            await self.image_repository.create(image_data)
            return True
        except Exception:
            return False
    
    async def get_product_images(self, product_id: int) -> List:
        """Obtiene imágenes de un producto"""
        return await self.image_repository.get_by_product_id(product_id)
    
    async def remove_product_image(self, image_id: int) -> bool:
        """Elimina una imagen de producto"""
        return await self.image_repository.delete(image_id)
    
    async def get_products_analytics(self) -> Dict[str, Any]:
        """Obtiene analytics de productos"""
        total_products = await self.product_repository.count()
        active_products = len(await self.product_repository.get_active_products())
        
        return {
            "total_products": total_products,
            "active_products": active_products,
            "inactive_products": total_products - active_products,
            "active_percentage": (active_products / total_products * 100) if total_products > 0 else 0
        }
