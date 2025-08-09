import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain.models import Product, Order
from infrastructure.orm import Base
from infrastructure.repositories import SqlAlchemyProductRepository, SqlAlchemyOrderRepository


class TestSqlAlchemyRepositories:
    """Test SQLAlchemy repository implementations"""

    @pytest.fixture
    def session(self):
        """Create in-memory SQLite session for testing"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        session_factory = sessionmaker(bind=engine)
        session = session_factory()
        yield session
        session.close()

    @pytest.fixture
    def product_repo(self, session):
        """Create product repository"""
        return SqlAlchemyProductRepository(session)

    @pytest.fixture
    def order_repo(self, session):
        """Create order repository"""
        return SqlAlchemyOrderRepository(session)

    # Product Repository Tests
    def test_add_product(self, product_repo, session):
        """Test adding a product"""
        product = Product(id=None, name="Test Product", quantity=10, price=99.99)

        saved_product = product_repo.add(product)
        session.commit()

        assert saved_product.id is not None
        assert saved_product.name == "Test Product"

    def test_get_product_by_id(self, product_repo, session):
        """Test getting product by ID"""
        product = Product(id=None, name="Test Product", quantity=10, price=99.99)
        saved_product = product_repo.add(product)
        session.commit()

        retrieved = product_repo.get(saved_product.id)

        assert retrieved is not None
        assert retrieved.id == saved_product.id
        assert retrieved.name == "Test Product"

    def test_get_product_by_id_not_found(self, product_repo):
        """Test getting non-existent product returns None"""
        result = product_repo.get(999)
        assert result is None

    def test_get_product_by_name(self, product_repo, session):
        """Test getting product by name"""
        product = Product(id=None, name="Unique Product", quantity=10, price=99.99)
        product_repo.add(product)
        session.commit()

        retrieved = product_repo.get_by_name("Unique Product")

        assert retrieved is not None
        assert retrieved.name == "Unique Product"

    def test_list_products(self, product_repo, session):
        """Test listing all products"""
        product1 = Product(id=None, name="Product 1", quantity=10, price=50.00)
        product2 = Product(id=None, name="Product 2", quantity=0, price=75.00)

        product_repo.add(product1)
        product_repo.add(product2)
        session.commit()

        products = product_repo.list()

        assert len(products) == 2
        assert any(p.name == "Product 1" for p in products)
        assert any(p.name == "Product 2" for p in products)

    def test_update_product(self, product_repo, session):
        """Test updating a product"""
        product = Product(id=None, name="Original", quantity=10, price=99.99)
        saved_product = product_repo.add(product)
        session.commit()

        saved_product.name = "Updated"
        saved_product.quantity = 20
        saved_product.price = 89.99

        product_repo.update(saved_product)
        session.commit()

        retrieved = product_repo.get(saved_product.id)
        assert retrieved.name == "Updated"
        assert retrieved.quantity == 20
        assert retrieved.price == 89.99

    def test_delete_product(self, product_repo, session):
        """Test deleting a product"""
        product = Product(id=None, name="To Delete", quantity=10, price=99.99)
        saved_product = product_repo.add(product)
        session.commit()

        result = product_repo.delete(saved_product.id)
        session.commit()

        assert result is True
        assert product_repo.get(saved_product.id) is None

    def test_list_in_stock(self, product_repo, session):
        """Test listing products in stock"""
        product1 = Product(id=None, name="In Stock", quantity=10, price=50.00)
        product2 = Product(id=None, name="Out of Stock", quantity=0, price=75.00)

        product_repo.add(product1)
        product_repo.add(product2)
        session.commit()

        in_stock = product_repo.list_in_stock()

        assert len(in_stock) == 1
        assert in_stock[0].name == "In Stock"

    # Order Repository Tests
    def test_add_order(self, order_repo, product_repo, session):
        """Test adding an order"""
        # Create products first
        product1 = Product(id=None, name="Product 1", quantity=10, price=50.00)
        product2 = Product(id=None, name="Product 2", quantity=20, price=30.00)

        saved_p1 = product_repo.add(product1)
        saved_p2 = product_repo.add(product2)
        session.commit()

        # Create order
        order = Order(id=None)
        order.add_item(saved_p1, 2)
        order.add_item(saved_p2, 3)

        saved_order = order_repo.add(order)
        session.commit()

        assert saved_order.id is not None
        assert len(saved_order.items) == 2

    def test_get_order_by_id(self, order_repo, product_repo, session):
        """Test getting order by ID"""
        # Create product and order
        product = Product(id=None, name="Product", quantity=10, price=50.00)
        saved_product = product_repo.add(product)
        session.commit()

        order = Order(id=None)
        order.add_item(saved_product, 2)
        saved_order = order_repo.add(order)
        session.commit()

        retrieved = order_repo.get(saved_order.id)

        assert retrieved is not None
        assert retrieved.id == saved_order.id
        assert len(retrieved.items) == 1
        assert retrieved.items[0].quantity == 2

    def test_list_orders(self, order_repo, product_repo, session):
        """Test listing all orders"""
        # Create product
        product = Product(id=None, name="Product", quantity=10, price=50.00)
        saved_product = product_repo.add(product)
        session.commit()

        # Create orders
        order1 = Order(id=None)
        order1.add_item(saved_product, 1)

        order2 = Order(id=None)
        order2.add_item(saved_product, 2)

        order_repo.add(order1)
        order_repo.add(order2)
        session.commit()

        orders = order_repo.list()

        assert len(orders) == 2

    def test_update_order(self, order_repo, product_repo, session):
        """Test updating an order"""
        # Create product and order
        product = Product(id=None, name="Product", quantity=10, price=50.00)
        saved_product = product_repo.add(product)
        session.commit()

        order = Order(id=None, status="pending")
        order.add_item(saved_product, 2)
        saved_order = order_repo.add(order)
        session.commit()

        # Update status
        saved_order.status = "confirmed"
        order_repo.update(saved_order)
        session.commit()

        retrieved = order_repo.get(saved_order.id)
        assert retrieved.status == "confirmed"

    def test_list_by_status(self, order_repo, product_repo, session):
        """Test listing orders by status"""
        # Create product
        product = Product(id=None, name="Product", quantity=10, price=50.00)
        saved_product = product_repo.add(product)
        session.commit()

        # Create orders with different statuses
        pending_order = Order(id=None, status="pending")
        pending_order.add_item(saved_product, 1)

        confirmed_order = Order(id=None, status="confirmed")
        confirmed_order.add_item(saved_product, 2)

        order_repo.add(pending_order)
        order_repo.add(confirmed_order)
        session.commit()

        pending_orders = order_repo.list_by_status("pending")
        confirmed_orders = order_repo.list_by_status("confirmed")

        assert len(pending_orders) == 1
        assert len(confirmed_orders) == 1
        assert pending_orders[0].status == "pending"
        assert confirmed_orders[0].status == "confirmed"
