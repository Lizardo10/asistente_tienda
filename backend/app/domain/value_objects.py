"""
Value Objects - Capa de Domain
Objetos inmutables que representan valores del dominio
Siguiendo principios SOLID
"""
from dataclasses import dataclass
from typing import Optional
import re
from decimal import Decimal


@dataclass(frozen=True)
class Email:
    """Value Object para Email"""
    value: str
    
    def __post_init__(self):
        if not self._is_valid():
            raise ValueError(f"Email inválido: {self.value}")
    
    def _is_valid(self) -> bool:
        """Validar formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, self.value) is not None
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Money:
    """Value Object para dinero"""
    amount: Decimal
    currency: str = "GTQ"
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("El monto no puede ser negativo")
    
    def add(self, other: 'Money') -> 'Money':
        """Sumar dinero"""
        if self.currency != other.currency:
            raise ValueError("No se pueden sumar monedas diferentes")
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        """Restar dinero"""
        if self.currency != other.currency:
            raise ValueError("No se pueden restar monedas diferentes")
        return Money(self.amount - other.amount, self.currency)
    
    def multiply(self, factor: Decimal) -> 'Money':
        """Multiplicar dinero"""
        return Money(self.amount * factor, self.currency)
    
    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"


@dataclass(frozen=True)
class ProductSKU:
    """Value Object para SKU de producto"""
    value: str
    
    def __post_init__(self):
        if not self._is_valid():
            raise ValueError(f"SKU inválido: {self.value}")
    
    def _is_valid(self) -> bool:
        """Validar formato de SKU"""
        # SKU debe ser alfanumérico, 6-20 caracteres
        return bool(re.match(r'^[A-Z0-9]{6,20}$', self.value))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Quantity:
    """Value Object para cantidad"""
    value: int
    
    def __post_init__(self):
        if self.value < 0:
            raise ValueError("La cantidad no puede ser negativa")
    
    def add(self, other: 'Quantity') -> 'Quantity':
        """Sumar cantidades"""
        return Quantity(self.value + other.value)
    
    def subtract(self, other: 'Quantity') -> 'Quantity':
        """Restar cantidades"""
        result = self.value - other.value
        if result < 0:
            raise ValueError("El resultado no puede ser negativo")
        return Quantity(result)
    
    def is_sufficient_for(self, required: 'Quantity') -> bool:
        """Verificar si la cantidad es suficiente"""
        return self.value >= required.value
    
    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class UserRole:
    """Value Object para rol de usuario"""
    value: str
    
    VALID_ROLES = ["admin", "user", "customer", "moderator"]
    
    def __post_init__(self):
        if self.value not in self.VALID_ROLES:
            raise ValueError(f"Rol inválido: {self.value}")
    
    def is_admin(self) -> bool:
        """Verificar si es rol de admin"""
        return self.value == "admin"
    
    def has_permission(self, permission: str) -> bool:
        """Verificar permisos basados en rol"""
        admin_permissions = ["manage_products", "manage_users", "view_reports", "manage_orders"]
        user_permissions = ["make_purchase", "view_products", "chat"]
        
        if self.value == "admin":
            return permission in admin_permissions
        elif self.value in ["user", "customer"]:
            return permission in user_permissions
        
        return False
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class OrderStatus:
    """Value Object para estado de orden"""
    value: str
    
    VALID_STATUSES = ["pending", "processing", "shipped", "delivered", "cancelled"]
    
    def __post_init__(self):
        if self.value not in self.VALID_STATUSES:
            raise ValueError(f"Estado de orden inválido: {self.value}")
    
    def can_transition_to(self, new_status: 'OrderStatus') -> bool:
        """Verificar si puede cambiar a un nuevo estado"""
        transitions = {
            "pending": ["processing", "cancelled"],
            "processing": ["shipped", "cancelled"],
            "shipped": ["delivered"],
            "delivered": [],
            "cancelled": []
        }
        
        return new_status.value in transitions.get(self.value, [])
    
    def is_final(self) -> bool:
        """Verificar si es un estado final"""
        return self.value in ["delivered", "cancelled"]
    
    def __str__(self) -> str:
        return self.value



