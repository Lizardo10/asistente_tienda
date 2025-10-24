"""
Entidades de dominio - Capa de Domain
Entidades puras sin dependencias de frameworks
Siguiendo principios de Clean Architecture
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


@dataclass
class ProductEntity:
    """Entidad de dominio para Producto"""
    id: Optional[int]
    title: str
    description: str
    price: Decimal
    image_url: str
    active: bool
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def is_available(self) -> bool:
        """Verificar si el producto está disponible"""
        return self.active and self.price > 0
    
    def calculate_discount(self, percentage: Decimal) -> Decimal:
        """Calcular precio con descuento"""
        discount_amount = self.price * (percentage / 100)
        return self.price - discount_amount
    
    def validate(self) -> List[str]:
        """Validar entidad"""
        errors = []
        
        if not self.title or len(self.title.strip()) == 0:
            errors.append("El título es requerido")
        
        if self.price < 0:
            errors.append("El precio no puede ser negativo")
        
        if len(self.description) > 1000:
            errors.append("La descripción es demasiado larga")
        
        return errors


@dataclass
class UserEntity:
    """Entidad de dominio para Usuario"""
    id: Optional[int]
    email: str
    full_name: str
    is_admin: bool
    role: str
    balance: Decimal
    active: bool
    email_verified: bool
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def can_make_purchase(self, amount: Decimal) -> bool:
        """Verificar si puede realizar una compra"""
        return self.active and self.email_verified and self.balance >= amount
    
    def is_authorized_admin(self) -> bool:
        """Verificar si es administrador autorizado"""
        return self.is_admin and self.active
    
    def validate(self) -> List[str]:
        """Validar entidad"""
        errors = []
        
        if not self.email or '@' not in self.email:
            errors.append("Email inválido")
        
        if not self.full_name or len(self.full_name.strip()) == 0:
            errors.append("El nombre completo es requerido")
        
        if self.balance < 0:
            errors.append("El balance no puede ser negativo")
        
        return errors


@dataclass
class OrderEntity:
    """Entidad de dominio para Orden"""
    id: Optional[int]
    user_id: int
    status: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    items: List['OrderItemEntity'] = field(default_factory=list)
    
    def calculate_total(self) -> Decimal:
        """Calcular total de la orden"""
        return sum(item.calculate_subtotal() for item in self.items)
    
    def can_be_cancelled(self) -> bool:
        """Verificar si la orden puede ser cancelada"""
        return self.status in ["pending", "processing"]
    
    def is_completed(self) -> bool:
        """Verificar si la orden está completada"""
        return self.status == "delivered"
    
    def validate(self) -> List[str]:
        """Validar entidad"""
        errors = []
        
        if not self.items:
            errors.append("La orden debe tener al menos un item")
        
        if self.user_id <= 0:
            errors.append("Usuario inválido")
        
        return errors


@dataclass
class OrderItemEntity:
    """Entidad de dominio para Item de Orden"""
    id: Optional[int]
    order_id: Optional[int]
    product_id: int
    quantity: int
    price: Decimal
    
    def calculate_subtotal(self) -> Decimal:
        """Calcular subtotal del item"""
        return self.price * self.quantity
    
    def validate(self) -> List[str]:
        """Validar entidad"""
        errors = []
        
        if self.quantity <= 0:
            errors.append("La cantidad debe ser mayor a 0")
        
        if self.price < 0:
            errors.append("El precio no puede ser negativo")
        
        return errors


@dataclass
class ChatMessageEntity:
    """Entidad de dominio para Mensaje de Chat"""
    id: Optional[int]
    chat_id: int
    user_id: Optional[int]
    sender: str  # "user" o "bot"
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    has_image: bool = False
    image_url: Optional[str] = None
    
    def is_from_user(self) -> bool:
        """Verificar si el mensaje es del usuario"""
        return self.sender == "user"
    
    def validate(self) -> List[str]:
        """Validar entidad"""
        errors = []
        
        if not self.content or len(self.content.strip()) == 0:
            errors.append("El mensaje no puede estar vacío")
        
        if len(self.content) > 5000:
            errors.append("El mensaje es demasiado largo")
        
        if self.sender not in ["user", "bot"]:
            errors.append("Sender inválido")
        
        return errors


@dataclass
class StockLevelEntity:
    """Entidad de dominio para Nivel de Stock"""
    id: Optional[int]
    product_id: int
    current_stock: int
    min_stock_level: int
    max_stock_level: int
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def needs_restock(self) -> bool:
        """Verificar si necesita reabastecimiento"""
        return self.current_stock <= self.min_stock_level
    
    def is_out_of_stock(self) -> bool:
        """Verificar si está agotado"""
        return self.current_stock == 0
    
    def is_overstocked(self) -> bool:
        """Verificar si hay sobre-stock"""
        return self.current_stock > self.max_stock_level
    
    def can_fulfill_order(self, quantity: int) -> bool:
        """Verificar si puede cumplir una orden"""
        return self.current_stock >= quantity
    
    def validate(self) -> List[str]:
        """Validar entidad"""
        errors = []
        
        if self.current_stock < 0:
            errors.append("El stock no puede ser negativo")
        
        if self.min_stock_level < 0:
            errors.append("El nivel mínimo no puede ser negativo")
        
        if self.max_stock_level <= self.min_stock_level:
            errors.append("El nivel máximo debe ser mayor al mínimo")
        
        return errors



