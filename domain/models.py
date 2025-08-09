from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from .exceptions import InvalidPriceError, InvalidQuantityError, InsufficientStockError


@dataclass
class Product:
    """Product entity representing a warehouse item"""
    id: Optional[int]
    name: str
    quantity: int
    price: float

    def __post_init__(self):
        self._validate()

    def _validate(self):
        """Validate product data"""
        if self.price <= 0:
            raise InvalidPriceError(self.price)
        if self.quantity < 0:
            raise InvalidQuantityError(self.quantity)
        if not self.name or not self.name.strip():
            raise ValueError("Product name cannot be empty")

    def reduce_quantity(self, amount: int):
        """Reduce product quantity when ordered"""
        if amount <= 0:
            raise InvalidQuantityError(amount)
        if amount > self.quantity:
            raise InsufficientStockError(self.name, amount, self.quantity)
        self.quantity -= amount

    def increase_quantity(self, amount: int):
        """Increase product quantity when restocked"""
        if amount <= 0:
            raise InvalidQuantityError(amount)
        self.quantity += amount

    @property
    def is_in_stock(self) -> bool:
        """Check if product is in stock"""
        return self.quantity > 0


@dataclass
class OrderItem:
    """Order item representing a product in an order"""
    product: Product
    quantity: int
    price_at_order: float

    def __post_init__(self):
        if self.quantity <= 0:
            raise InvalidQuantityError(self.quantity)
        if self.price_at_order <= 0:
            raise InvalidPriceError(self.price_at_order)

    @property
    def total_price(self) -> float:
        """Calculate total price for this order item"""
        return self.quantity * self.price_at_order


@dataclass
class Order:
    """Order entity representing a customer order"""
    id: Optional[int]
    items: List[OrderItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = field(default="pending")

    def add_item(self, product: Product, quantity: int):
        """Add a product to the order"""
        if quantity <= 0:
            raise InvalidQuantityError(quantity)

        # Check if product already in order
        for item in self.items:
            if item.product.id == product.id:
                # Update quantity instead of adding duplicate
                item.quantity += quantity
                return

        # Add new item
        order_item = OrderItem(
            product=product,
            quantity=quantity,
            price_at_order=product.price
        )
        self.items.append(order_item)

    def remove_item(self, product_id: int):
        """Remove a product from the order"""
        self.items = [item for item in self.items if item.product.id != product_id]

    @property
    def total_price(self) -> float:
        """Calculate total order price"""
        return sum(item.total_price for item in self.items)

    @property
    def total_items(self) -> int:
        """Get total number of items in order"""
        return sum(item.quantity for item in self.items)

    def confirm(self):
        """Confirm the order"""
        if not self.items:
            raise ValueError("Cannot confirm empty order")
        self.status = "confirmed"

    def complete(self):
        if self.status != "confirmed":
            raise ValueError(
                f"Can only complete confirmed orders, "
                f"current status: '{self.status}'"
            )
        self.status = "completed"

    def cancel(self):
        """Cancel the order"""
        if self.status == "completed":
            raise ValueError("Cannot cancel completed order")
        self.status = "cancelled"
