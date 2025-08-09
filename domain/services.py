from dataclasses import replace
from typing import List, Optional

from .models import Product, Order
from .repositories import ProductRepository, OrderRepository
from .exceptions import (
    ProductNotFoundError,
    OrderNotFoundError,
    InsufficientStockError
)


class WarehouseService:
    """Service for warehouse business logic"""

    def __init__(self, product_repo: ProductRepository, order_repo: OrderRepository):
        self.product_repo = product_repo
        self.order_repo = order_repo

    # Product management
    def create_product(self, name: str, quantity: int, price: float) -> Product:
        """Create a new product"""
        # Check if product with same name exists
        existing = self.product_repo.get_by_name(name)
        if existing:
            raise ValueError(f"Product with name '{name}' already exists")

        product = Product(id=None, name=name, quantity=quantity, price=price)
        return self.product_repo.add(product)

    def get_product(self, product_id: int) -> Product:
        """Get product by ID"""
        product = self.product_repo.get(product_id)
        if not product:
            raise ProductNotFoundError(product_id)
        return product

    def list_products(self) -> List[Product]:
        """List all products"""
        return self.product_repo.list()

    def list_available_products(self) -> List[Product]:
        """List products that are in stock"""
        return self.product_repo.list_in_stock()

    def update_product_price(self, product_id: int, new_price: float) -> Product:
        """Update product price"""
        old_product = self.get_product(product_id)
        new_product = replace(old_product, price=new_price)  # Creates new instance, triggers __post_init__
        return self.product_repo.update(new_product)

    def restock_product(self, product_id: int, quantity: int) -> Product:
        """Add more items to product stock"""
        product = self.get_product(product_id)
        product.increase_quantity(quantity)
        return self.product_repo.update(product)

    def delete_product(self, product_id: int) -> bool:
        """Delete a product (only if not in any orders)"""
        # Check if product exists
        product = self.get_product(product_id)

        # Check if product is in any orders
        all_orders = self.order_repo.list()
        for order in all_orders:
            for item in order.items:
                if item.product.id == product_id:
                    raise ValueError(
                        f"Cannot delete product {product_id}: "
                        f"it is referenced in order {order.id}"
                    )

        return self.product_repo.delete(product_id)

    # Order management
    def create_order(self, product_quantities: List[tuple[int, int]]) -> Order:
        """
        Create a new order with products
        Args:
            product_quantities: List of (product_id, quantity) tuples
        """
        order = Order(id=None)

        # Process each product
        for product_id, quantity in product_quantities:
            product = self.get_product(product_id)

            # Check stock availability
            if product.quantity < quantity:
                raise InsufficientStockError(
                    product.name,
                    quantity,
                    product.quantity
                )

            # Add to order
            order.add_item(product, quantity)

            # Reduce stock
            product.reduce_quantity(quantity)
            self.product_repo.update(product)

        # Save order
        return self.order_repo.add(order)

    def get_order(self, order_id: int) -> Order:
        """Get order by ID"""
        order = self.order_repo.get(order_id)
        if not order:
            raise OrderNotFoundError(order_id)
        return order

    def list_orders(self, status: Optional[str] = None) -> List[Order]:
        """List orders, optionally filtered by status"""
        if status:
            return self.order_repo.list_by_status(status)
        return self.order_repo.list()

    def cancel_order(self, order_id: int) -> Order:
        """Cancel an order and restore product quantities"""
        order = self.get_order(order_id)

        # Can only cancel pending or confirmed orders
        if order.status not in ["pending", "confirmed"]:
            raise ValueError(
                f"Cannot cancel order with status '{order.status}'"
            )

        # Restore product quantities
        for item in order.items:
            product = self.get_product(item.product.id)
            product.increase_quantity(item.quantity)
            self.product_repo.update(product)

        # Update order status
        order.cancel()
        return self.order_repo.update(order)

    def complete_order(self, order_id: int) -> Order:
        """Mark order as completed"""
        order = self.get_order(order_id)

        if order.status != "confirmed":
            raise ValueError(
                f"Can only complete confirmed orders, "
                f"current status: '{order.status}'"
            )

        order.status = "completed"
        return self.order_repo.update(order)