"""
Servicio de Caché Inteligente con Redis
Optimiza consultas a la base de datos costosas
Sistema de recomendaciones con ML
"""
import json
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlmodel import Session, select

from app.services.simple_cache_service import cache_service
from app.models_sqlmodel.product import Product
from app.models_sqlmodel.user import User
from app.models_sqlmodel.order import Order, OrderItem


class IntelligentCacheService:
    """Servicio de caché inteligente con Redis"""
    
    def __init__(self):
        self.cache = cache_service
        self.default_ttl = 3600  # 1 hora
        self.products_ttl = 7200  # 2 horas para productos
        self.search_ttl = 1800  # 30 minutos para búsquedas
    
    # ==================== PRODUCTOS ====================
    
    async def get_all_products(self, db: Session, active_only: bool = True) -> List[Dict[str, Any]]:
        """Obtener todos los productos (con caché)"""
        cache_key = f"products:all:active={active_only}"
        
        # Intentar obtener de caché
        cached = await self.cache.get(cache_key)
        if cached:
            print(f"✅ CACHE HIT: Productos obtenidos de Redis")
            return json.loads(cached)
        
        # Si no está en caché, consultar DB
        print(f"❌ CACHE MISS: Consultando base de datos")
        query = select(Product)
        if active_only:
            query = query.where(Product.active == True)
        
        products = db.exec(query).all()
        
        # Convertir a diccionarios
        products_data = [
            {
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "price": float(p.price),
                "image_url": p.image_url,
                "active": p.active
            }
            for p in products
        ]
        
        # Guardar en caché
        await self.cache.set(cache_key, json.dumps(products_data), ttl=self.products_ttl)
        
        return products_data
    
    async def search_products(self, db: Session, query: str) -> List[Dict[str, Any]]:
        """Buscar productos (con caché inteligente)"""
        # Crear hash de la consulta para usar como key
        query_hash = hashlib.md5(query.lower().encode()).hexdigest()
        cache_key = f"search:products:{query_hash}"
        
        # Intentar obtener de caché
        cached = await self.cache.get(cache_key)
        if cached:
            print(f"✅ CACHE HIT: Búsqueda '{query}' obtenida de Redis")
            return json.loads(cached)
        
        # Si no está en caché, buscar en DB
        print(f"❌ CACHE MISS: Buscando '{query}' en base de datos")
        
        # Buscar en título y descripción
        products = db.exec(
            select(Product).where(
                (Product.title.ilike(f"%{query}%")) | 
                (Product.description.ilike(f"%{query}%"))
            ).where(Product.active == True)
        ).all()
        
        # Convertir a diccionarios
        results = [
            {
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "price": float(p.price),
                "image_url": p.image_url,
                "relevance": self._calculate_relevance(query, p)
            }
            for p in products
        ]
        
        # Ordenar por relevancia
        results.sort(key=lambda x: x["relevance"], reverse=True)
        
        # Guardar en caché
        await self.cache.set(cache_key, json.dumps(results), ttl=self.search_ttl)
        
        return results
    
    async def get_product_by_id(self, db: Session, product_id: int) -> Optional[Dict[str, Any]]:
        """Obtener producto por ID (con caché)"""
        cache_key = f"product:{product_id}"
        
        # Intentar obtener de caché
        cached = await self.cache.get(cache_key)
        if cached:
            print(f"✅ CACHE HIT: Producto {product_id} de Redis")
            return json.loads(cached)
        
        # Consultar DB
        print(f"❌ CACHE MISS: Consultando producto {product_id} en DB")
        product = db.get(Product, product_id)
        
        if not product:
            return None
        
        product_data = {
            "id": product.id,
            "title": product.title,
            "description": product.description,
            "price": float(product.price),
            "image_url": product.image_url,
            "active": product.active
        }
        
        # Guardar en caché
        await self.cache.set(cache_key, json.dumps(product_data), ttl=self.products_ttl)
        
        return product_data
    
    # ==================== RECOMENDACIONES ====================
    
    async def get_personalized_recommendations(self, db: Session, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtener recomendaciones personalizadas (con ML básico)"""
        cache_key = f"recommendations:user:{user_id or 'guest'}"
        
        # Intentar obtener de caché
        cached = await self.cache.get(cache_key)
        if cached:
            print(f"✅ CACHE HIT: Recomendaciones para usuario {user_id}")
            return json.loads(cached)
        
        # Generar recomendaciones
        print(f"❌ CACHE MISS: Generando recomendaciones para usuario {user_id}")
        
        recommendations = []
        
        if user_id:
            # Recomendaciones basadas en historial
            recommendations = await self._get_user_based_recommendations(db, user_id)
        else:
            # Recomendaciones generales (productos populares)
            recommendations = await self._get_popular_products(db)
        
        # Guardar en caché (15 minutos)
        await self.cache.set(cache_key, json.dumps(recommendations), ttl=900)
        
        return recommendations
    
    async def _get_user_based_recommendations(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """Recomendaciones PERSONALIZADAS basadas en compras anteriores"""
        try:
            # Obtener órdenes del usuario
            orders = db.exec(
                select(Order).where(Order.user_id == user_id)
            ).all()
            
            if not orders:
                # Si no tiene historial, productos populares
                return await self._get_popular_products(db)
            
            # Obtener productos comprados con detalles
            purchased_products = []
            purchased_categories = set()
            
            for order in orders:
                items = db.exec(
                    select(OrderItem).where(OrderItem.order_id == order.id)
                ).all()
                for item in items:
                    product = db.get(Product, item.product_id)
                    if product:
                        purchased_products.append({
                            'id': product.id,
                            'title': product.title,
                            'description': product.description,
                            'price': float(product.price),
                            'category': self._extract_category(product.title, product.description)
                        })
                        purchased_categories.add(self._extract_category(product.title, product.description))
            
            # Obtener todos los productos disponibles
            all_products = db.exec(select(Product).where(Product.active == True)).all()
            
            recommendations = []
            purchased_ids = {p['id'] for p in purchased_products}
            
            for product in all_products:
                if product.id not in purchased_ids:
                    product_category = self._extract_category(product.title, product.description)
                    
                    # Calcular score de recomendación
                    score = 0
                    reason = ""
                    
                    # 1. Misma categoría que productos comprados
                    if product_category in purchased_categories:
                        score += 3
                        reason = f"Te gustan los productos de {product_category}"
                    
                    # 2. Precio similar a productos comprados
                    avg_price = sum(p['price'] for p in purchased_products) / len(purchased_products)
                    price_diff = abs(float(product.price) - avg_price) / avg_price
                    if price_diff < 0.3:  # 30% diferencia
                        score += 2
                        if not reason:
                            reason = "Similar a tus compras anteriores"
                    
                    # 3. Palabras clave similares
                    purchased_keywords = set()
                    for p in purchased_products:
                        keywords = self._extract_keywords(p['title'], p['description'])
                        purchased_keywords.update(keywords)
                    
                    product_keywords = self._extract_keywords(product.title, product.description)
                    common_keywords = purchased_keywords.intersection(product_keywords)
                    if common_keywords:
                        score += len(common_keywords)
                        if not reason:
                            reason = f"Similar a tus productos de {', '.join(common_keywords)}"
                    
                    # 4. Productos complementarios
                    complementary_score = self._get_complementary_score(product, purchased_products)
                    score += complementary_score
                    if complementary_score > 0 and not reason:
                        reason = "Perfecto para complementar tus compras"
                    
                    if score > 0:
                        recommendations.append({
                            "id": product.id,
                            "title": product.title,
                            "description": product.description,
                            "price": float(product.price),
                            "image_url": product.image_url,
                            "reason": reason or "Basado en tus compras anteriores",
                            "score": score,
                            "personalized": True
                        })
            
            # Ordenar por score y tomar los mejores
            recommendations.sort(key=lambda x: x["score"], reverse=True)
            
            return recommendations[:6]  # Top 6 recomendaciones personalizadas
            
        except Exception as e:
            print(f"Error en recomendaciones de usuario: {e}")
            return await self._get_popular_products(db)
    
    def _extract_category(self, title: str, description: str) -> str:
        """Extraer categoría del producto"""
        text = f"{title} {description}".lower()
        
        categories = {
            'ropa': ['camisa', 'pantalon', 'jeans', 'vestido', 'falda', 'blusa', 'chaqueta', 'abrigo'],
            'calzado': ['zapatos', 'tenis', 'sandalias', 'botas', 'tacones'],
            'accesorios': ['bolso', 'cinturon', 'reloj', 'collar', 'aretes', 'pulsera'],
            'deportes': ['deportivo', 'gym', 'running', 'futbol', 'basquet'],
            'casual': ['casual', 'diario', 'comodo', 'basico'],
            'formal': ['formal', 'elegante', 'oficina', 'negocio']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'general'
    
    def _extract_keywords(self, title: str, description: str) -> set:
        """Extraer palabras clave importantes"""
        text = f"{title} {description}".lower()
        
        # Palabras importantes para ropa
        keywords = set()
        important_words = [
            'algodon', 'jeans', 'casual', 'formal', 'deportivo', 'elegante',
            'comodo', 'moderno', 'clasico', 'colorido', 'basico', 'premium',
            'verano', 'invierno', 'primavera', 'otonio'
        ]
        
        for word in important_words:
            if word in text:
                keywords.add(word)
        
        return keywords
    
    def _get_complementary_score(self, product: Product, purchased_products: List[Dict]) -> int:
        """Calcular score de productos complementarios"""
        product_text = f"{product.title} {product.description}".lower()
        score = 0
        
        # Si compró jeans, recomendar camisas
        if any('jeans' in p['title'].lower() for p in purchased_products):
            if any(word in product_text for word in ['camisa', 'blusa', 'top']):
                score += 2
        
        # Si compró camisa, recomendar pantalones
        if any(word in ' '.join(p['title'].lower() for p in purchased_products) for word in ['camisa', 'blusa']):
            if any(word in product_text for word in ['pantalon', 'jeans', 'falda']):
                score += 2
        
        # Si compró ropa formal, recomendar más formal
        if any(word in ' '.join(p['title'].lower() for p in purchased_products) for word in ['formal', 'elegante']):
            if any(word in product_text for word in ['formal', 'elegante', 'oficina']):
                score += 1
        
        return score
    
    async def _get_popular_products(self, db: Session) -> List[Dict[str, Any]]:
        """Productos más populares/nuevos"""
        products = db.exec(
            select(Product)
            .where(Product.active == True)
            .order_by(Product.created_at.desc())
            .limit(6)
        ).all()
        
        return [
            {
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "price": float(p.price),
                "image_url": p.image_url,
                "reason": "Producto destacado"
            }
            for p in products
        ]
    
    # ==================== ANÁLISIS IA CACHE ====================
    
    async def cache_ai_analysis(self, query: str, response: str, ttl: int = 1800):
        """Cachear análisis de IA para consultas repetidas"""
        query_hash = hashlib.md5(query.lower().encode()).hexdigest()
        cache_key = f"ai:analysis:{query_hash}"
        
        await self.cache.set(cache_key, response, ttl=ttl)
    
    async def get_cached_ai_analysis(self, query: str) -> Optional[str]:
        """Obtener análisis de IA cacheado"""
        query_hash = hashlib.md5(query.lower().encode()).hexdigest()
        cache_key = f"ai:analysis:{query_hash}"
        
        cached = await self.cache.get(cache_key)
        if cached:
            print(f"✅ CACHE HIT: Análisis IA para '{query}'")
            return cached
        
        return None
    
    # ==================== INVALIDACIÓN ====================
    
    async def invalidate_product_cache(self, product_id: Optional[int] = None):
        """Invalidar caché de productos"""
        if product_id:
            # Invalidar producto específico
            await self.cache.delete(f"product:{product_id}")
        else:
            # Invalidar todos los productos
            await self.cache.delete("products:all:active=True")
            await self.cache.delete("products:all:active=False")
    
    async def invalidate_search_cache(self):
        """Invalidar todas las búsquedas cacheadas"""
        # En producción, usar scan para encontrar todas las keys
        pass
    
    # ==================== UTILIDADES ====================
    
    def _calculate_relevance(self, query: str, product: Product) -> float:
        """Calcular relevancia de un producto para una búsqueda"""
        score = 0.0
        query_lower = query.lower()
        title_lower = product.title.lower()
        desc_lower = product.description.lower()
        
        # Coincidencia exacta en título
        if query_lower in title_lower:
            score += 1.0
        
        # Coincidencia en descripción
        if query_lower in desc_lower:
            score += 0.5
        
        # Coincidencias de palabras
        words = query_lower.split()
        for word in words:
            if len(word) > 3:
                if word in title_lower:
                    score += 0.3
                if word in desc_lower:
                    score += 0.1
        
        return score


# Instancia global
intelligent_cache = IntelligentCacheService()
