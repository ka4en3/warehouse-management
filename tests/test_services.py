from unittest.mock import Mock
import pytest

from domain.models import Product, Order, OrderItem
from domain.services import WarehouseService
from domain.exceptions import (
    ProductNotFoundError,
    OrderNotFoundError,
    InsufficientStockError
)


class TestWarehouseService:
    """Test WarehouseService"""

    @pytest.fixture
    def mock_product_repo(self):
        """Create mock product repository"""
        return Mock()

    @pytest.fixture
    def mock_order_repo(self):
        """Create mock order repository"""
        return Mock()

    @pytest.fixture
    def service(self, mock_product_repo, mock_order_repo):
        """Create warehouse service with mocked dependencies"""
        return WarehouseService(mock_product_repo, mock_order_repo)

    # Product management tests
    def test_create_product_success(self, service, mock_product_repo):
        """Test creating a new product successfully"""
        mock_product_repo.get_by_name.return_value = None
        mock_product_repo.add.return_value = Product(
            id=1, name="New Product", quantity=10, price=99.99
        )

        result = service.create_product("New Product", 10, 99.99)

        assert result.id == 1
        assert result.name == "New Product"
        mock_product_repo.get_by_name.assert_called_once_with("New Product")
        mock_product_repo.add.assert_called_once()

    def test_create_product_duplicate_name(self, service, mock_product_repo):
        """Test creating product with duplicate name raises error"""
        existing_product = Product(id=1, name="Existing", quantity=5, price=50.00)
        mock_product_repo.get_by_name.return_value = existing_product

        with pytest.raises(ValueError, match="already exists"):
            service.create_product("Existing", 10, 99.99)

    def test_get_product_success(self, service, mock_product_repo):
        """Test getting product by ID"""
        expected_product = Product(id=1, name="Product", quantity=10, price=99.99)
        mock_product_repo.get.return_value = expected_product

        result = service.get_product(1)

        assert result == expected_product
        mock_product_repo.get.assert_called_once_with(1)

    def test_get_product_not_found(self, service, mock_product_repo):
        """Test getting non-existent product raises error"""
        mock_product_repo.get.return_value = None

        with pytest.raises(ProductNotFoundError):
            service.get_product(999)

    def test_list_products(self, service, mock_product_repo):
        """Test listing all products"""
        products = [
            Product(id=1, name="Product 1", quantity=10, price=50.00),
            Product(id=2, name="Product 2", quantity=20, price=75.00)
        ]
        mock_product_repo.list.return_value = products

        result = service.list_products()

        assert result == products
        mock_product_repo.list.assert_called_once()

    def test_list_available_products(self, service, mock_product_repo):
        """Test listing products in stock"""
        products = [
            Product(id=1, name="Product 1", quantity=10, price=50.00)
        ]
        mock_product_repo.list_in_stock.return_value = products

        result = service.list_available_products()

        assert result == products
        mock_product_repo.list_in_stock.assert_called_once()

    def test_update_product_price(self, service, mock_product_repo):
        """Test updating product price"""
        product = Product(id=1, name="Product", quantity=10, price=99.99)
        mock_product_repo.get.return_value = product

        def update_product_with_price(new_product: Product) -> Product:
            return new_product

        mock_product_repo.update.side_effect = update_product_with_price

        result = service.update_product_price(1, 89.99)

        assert result.price == 89.99
        mock_product_repo.update.assert_called_once()

    def test_restock_product(self, service, mock_product_repo):
        """Test restocking product"""
        product = Product(id=1, name="Product", quantity=10, price=99.99)
        mock_product_repo.get.return_value = product
        mock_product_repo.update.return_value = product

        result = service.restock_product(1, 20)

        assert result.quantity == 30
        mock_product_repo.update.assert_called_once()

    def test_delete_product_success(self, service, mock_product_repo, mock_order_repo):
        """Test deleting product successfully"""
        product = Product(id=1, name="Product", quantity=10, price=99.99)
        mock_product_repo.get.return_value = product
        mock_order_repo.list.return_value = []  # No orders
        mock_product_repo.delete.return_value = True

        result = service.delete_product(1)

        assert result is True
        mock_product_repo.delete.assert_called_once_with(1)

    def test_delete_product_in_order(self, service, mock_product_repo, mock_order_repo):
        """Test deleting product that's in an order raises error"""
        product = Product(id=1, name="Product", quantity=10, price=99.99)
        order_item = OrderItem(product=product, quantity=2, price_at_order=99.99)
        order = Order(id=1)
        order.items = [order_item]

        mock_product_repo.get.return_value = product
        mock_order_repo.list.return_value = [order]

        with pytest.raises(ValueError, match="Cannot delete product"):
            service.delete_product(1)

    # Order management tests
    def test_create_order_success(self, service, mock_product_repo, mock_order_repo):
        """Test creating order successfully"""
        product1 = Product(id=1, name="Product 1", quantity=10, price=50.00)
        product2 = Product(id=2, name="Product 2", quantity=20, price=30.00)

        mock_product_repo.get.side_effect = [product1, product2]

        def add_order_with_id(order):
            order.id = 1
            return order

        mock_order_repo.add.side_effect = add_order_with_id

        result = service.create_order([(1, 2), (2, 3)])

        assert result.id == 1
        assert len(result.items) == 2
        assert product1.quantity == 8  # 10 - 2
        assert product2.quantity == 17  # 20 - 3
        assert mock_product_repo.update.call_count == 2

    def test_create_order_insufficient_stock(self, service, mock_product_repo):
        """Test creating order with insufficient stock raises error"""
        product = Product(id=1, name="Product", quantity=5, price=50.00)
        mock_product_repo.get.return_value = product

        with pytest.raises(InsufficientStockError):
            service.create_order([(1, 10)])  # Request 10, only 5 available

    def test_get_order_success(self, service, mock_order_repo):
        """Test getting order by ID"""
        expected_order = Order(id=1)
        mock_order_repo.get.return_value = expected_order

        result = service.get_order(1)

        assert result == expected_order
        mock_order_repo.get.assert_called_once_with(1)

    def test_get_order_not_found(self, service, mock_order_repo):
        """Test getting non-existent order raises error"""
        mock_order_repo.get.return_value = None

        with pytest.raises(OrderNotFoundError):
            service.get_order(999)

    def test_list_orders_all(self, service, mock_order_repo):
        """Test listing all orders"""
        orders = [Order(id=1), Order(id=2)]
        mock_order_repo.list.return_value = orders

        result = service.list_orders()

        assert result == orders
        mock_order_repo.list.assert_called_once()

    def test_list_orders_by_status(self, service, mock_order_repo):
        """Test listing orders by status"""
        orders = [Order(id=1, status="pending")]
        mock_order_repo.list_by_status.return_value = orders

        result = service.list_orders(status="pending")

        assert result == orders
        mock_order_repo.list_by_status.assert_called_once_with("pending")

    def test_cancel_order_success(self, service, mock_product_repo, mock_order_repo):
        """Test canceling order successfully"""
        product = Product(id=1, name="Product", quantity=8, price=50.00)
        order_item = OrderItem(product=product, quantity=2, price_at_order=50.00)
        order = Order(id=1, status="pending")
        order.items = [order_item]

        mock_order_repo.get.return_value = order
        mock_product_repo.get.return_value = product
        mock_order_repo.update.return_value = order

        result = service.cancel_order(1)

        assert result.status == "cancelled"
        assert product.quantity == 10  # 8 + 2 restored
        mock_product_repo.update.assert_called_once()

    def test_cancel_order_invalid_status(self, service, mock_order_repo):
        """Test canceling order with invalid status raises error"""
        order = Order(id=1, status="completed")
        mock_order_repo.get.return_value = order

        with pytest.raises(ValueError, match="Cannot cancel order"):
            service.cancel_order(1)

    def test_complete_order_success(self, service, mock_order_repo):
        """Test completing order successfully"""
        order = Order(id=1, status="confirmed")
        mock_order_repo.get.return_value = order
        mock_order_repo.update.return_value = order

        result = service.complete_order(1)

        assert result.status == "completed"
        mock_order_repo.update.assert_called_once()

    def test_complete_order_invalid_status(self, service, mock_order_repo):
        """Test completing order with invalid status raises error"""
        order = Order(id=1, status="pending")
        mock_order_repo.get.return_value = order

        with pytest.raises(ValueError, match="Can only complete confirmed orders"):
            service.complete_order(1)
