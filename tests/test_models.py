from datetime import datetime
import pytest

from domain.models import Product, Order, OrderItem
from domain.exceptions import InvalidPriceError, InvalidQuantityError, InsufficientStockError


class TestProduct:
    """Test Product model"""

    def test_create_valid_product(self):
        """Test creating a valid product"""
        product = Product(id=1, name="Test Product", quantity=10, price=99.99)
        assert product.id == 1
        assert product.name == "Test Product"
        assert product.quantity == 10
        assert product.price == 99.99
        assert product.is_in_stock is True

    def test_create_product_with_zero_quantity(self):
        """Test creating a product with zero quantity is valid"""
        product = Product(id=1, name="Test Product", quantity=0, price=99.99)
        assert product.quantity == 0
        assert product.is_in_stock is False

    def test_create_product_with_invalid_price(self):
        """Test creating a product with invalid price raises error"""
        with pytest.raises(InvalidPriceError):
            Product(id=1, name="Test Product", quantity=10, price=0)

        with pytest.raises(InvalidPriceError):
            Product(id=1, name="Test Product", quantity=10, price=-10)

    def test_create_product_with_invalid_quantity(self):
        """Test creating a product with negative quantity raises error"""
        with pytest.raises(InvalidQuantityError):
            Product(id=1, name="Test Product", quantity=-5, price=99.99)

    def test_create_product_with_empty_name(self):
        """Test creating a product with empty name raises error"""
        with pytest.raises(ValueError, match="Product name cannot be empty"):
            Product(id=1, name="", quantity=10, price=99.99)

        with pytest.raises(ValueError, match="Product name cannot be empty"):
            Product(id=1, name="   ", quantity=10, price=99.99)

    def test_reduce_quantity(self):
        """Test reducing product quantity"""
        product = Product(id=1, name="Test Product", quantity=10, price=99.99)
        product.reduce_quantity(3)
        assert product.quantity == 7

        product.reduce_quantity(7)
        assert product.quantity == 0
        assert product.is_in_stock is False

    def test_reduce_quantity_insufficient_stock(self):
        """Test reducing quantity when insufficient stock"""
        product = Product(id=1, name="Test Product", quantity=5, price=99.99)
        with pytest.raises(InsufficientStockError) as exc_info:
            product.reduce_quantity(10)

        assert exc_info.value.requested == 10
        assert exc_info.value.available == 5

    def test_reduce_quantity_invalid_amount(self):
        """Test reducing quantity with invalid amount"""
        product = Product(id=1, name="Test Product", quantity=10, price=99.99)
        with pytest.raises(InvalidQuantityError):
            product.reduce_quantity(0)

        with pytest.raises(InvalidQuantityError):
            product.reduce_quantity(-5)

    def test_increase_quantity(self):
        """Test increasing product quantity"""
        product = Product(id=1, name="Test Product", quantity=10, price=99.99)
        product.increase_quantity(5)
        assert product.quantity == 15

    def test_increase_quantity_invalid_amount(self):
        """Test increasing quantity with invalid amount"""
        product = Product(id=1, name="Test Product", quantity=10, price=99.99)
        with pytest.raises(InvalidQuantityError):
            product.increase_quantity(0)

        with pytest.raises(InvalidQuantityError):
            product.increase_quantity(-5)


class TestOrderItem:
    """Test OrderItem model"""

    def test_create_valid_order_item(self):
        """Test creating a valid order item"""
        product = Product(id=1, name="Test Product", quantity=10, price=99.99)
        order_item = OrderItem(product=product, quantity=2, price_at_order=99.99)

        assert order_item.product == product
        assert order_item.quantity == 2
        assert order_item.price_at_order == 99.99
        assert order_item.total_price == 199.98

    def test_create_order_item_with_invalid_quantity(self):
        """Test creating order item with invalid quantity"""
        product = Product(id=1, name="Test Product", quantity=10, price=99.99)

        with pytest.raises(InvalidQuantityError):
            OrderItem(product=product, quantity=0, price_at_order=99.99)

        with pytest.raises(InvalidQuantityError):
            OrderItem(product=product, quantity=-5, price_at_order=99.99)

    def test_create_order_item_with_invalid_price(self):
        """Test creating order item with invalid price"""
        product = Product(id=1, name="Test Product", quantity=10, price=99.99)

        with pytest.raises(InvalidPriceError):
            OrderItem(product=product, quantity=2, price_at_order=0)

        with pytest.raises(InvalidPriceError):
            OrderItem(product=product, quantity=2, price_at_order=-10)


class TestOrder:
    """Test Order model"""

    def test_create_empty_order(self):
        """Test creating an empty order"""
        order = Order(id=1)
        assert order.id == 1
        assert order.items == []
        assert order.status == "pending"
        assert isinstance(order.created_at, datetime)
        assert order.total_price == 0
        assert order.total_items == 0

    def test_add_item_to_order(self):
        """Test adding items to order"""
        order = Order(id=1)
        product1 = Product(id=1, name="Product 1", quantity=10, price=50.00)
        product2 = Product(id=2, name="Product 2", quantity=20, price=30.00)

        order.add_item(product1, 2)
        assert len(order.items) == 1
        assert order.total_items == 2
        assert order.total_price == 100.00

        order.add_item(product2, 3)
        assert len(order.items) == 2
        assert order.total_items == 5
        assert order.total_price == 190.00

    def test_add_same_product_twice(self):
        """Test adding same product twice updates quantity"""
        order = Order(id=1)
        product = Product(id=1, name="Product", quantity=10, price=50.00)

        order.add_item(product, 2)
        order.add_item(product, 3)

        assert len(order.items) == 1
        assert order.items[0].quantity == 5
        assert order.total_items == 5

    def test_add_item_with_invalid_quantity(self):
        """Test adding item with invalid quantity"""
        order = Order(id=1)
        product = Product(id=1, name="Product", quantity=10, price=50.00)

        with pytest.raises(InvalidQuantityError):
            order.add_item(product, 0)

        with pytest.raises(InvalidQuantityError):
            order.add_item(product, -5)

    def test_remove_item_from_order(self):
        """Test removing item from order"""
        order = Order(id=1)
        product1 = Product(id=1, name="Product 1", quantity=10, price=50.00)
        product2 = Product(id=2, name="Product 2", quantity=20, price=30.00)

        order.add_item(product1, 2)
        order.add_item(product2, 3)

        order.remove_item(1)
        assert len(order.items) == 1
        assert order.items[0].product.id == 2

    def test_confirm_order(self):
        """Test confirming order"""
        order = Order(id=1)
        product = Product(id=1, name="Product", quantity=10, price=50.00)
        order.add_item(product, 2)

        order.confirm()
        assert order.status == "confirmed"

    def test_confirm_empty_order(self):
        """Test confirming empty order raises error"""
        order = Order(id=1)
        with pytest.raises(ValueError, match="Cannot confirm empty order"):
            order.confirm()

    def test_cancel_order(self):
        """Test canceling order"""
        order = Order(id=1)
        order.cancel()
        assert order.status == "cancelled"

    def test_cancel_completed_order(self):
        """Test canceling completed order raises error"""
        order = Order(id=1, status="completed")
        with pytest.raises(ValueError, match="Cannot cancel completed order"):
            order.cancel()
