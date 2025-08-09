from abc import ABC, abstractmethod
from typing import List, Optional

from .models import Product, Order


class ProductRepository(ABC):
    """Abstract repository for Product entity"""

    @abstractmethod
    def add(self, product: Product) -> Product:
        """Add a new product and return it with assigned ID"""
        pass

    @abstractmethod
    def get(self, product_id: int) -> Optional[Product]:
        """Get product by ID, return None if not found"""
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Product]:
        """Get product by name, return None if not found"""
        pass

    @abstractmethod
    def list(self) -> List[Product]:
        """List all products"""
        pass

    @abstractmethod
    def update(self, product: Product) -> Product:
        """Update existing product"""
        pass

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """Delete product by ID, return True if deleted"""
        pass

    @abstractmethod
    def list_in_stock(self) -> List[Product]:
        """List all products that are in stock"""
        pass


class OrderRepository(ABC):
    """Abstract repository for Order entity"""

    @abstractmethod
    def add(self, order: Order) -> Order:
        """Add a new order and return it with assigned ID"""
        pass

    @abstractmethod
    def get(self, order_id: int) -> Optional[Order]:
        """Get order by ID, return None if not found"""
        pass

    @abstractmethod
    def list(self) -> List[Order]:
        """List all orders"""
        pass

    @abstractmethod
    def update(self, order: Order) -> Order:
        """Update existing order"""
        pass

    @abstractmethod
    def list_by_status(self, status: str) -> List[Order]:
        """List orders by status"""
        pass

    @abstractmethod
    def delete(self, order_id: int) -> bool:
        """Delete order by ID, return True if deleted"""
        pass