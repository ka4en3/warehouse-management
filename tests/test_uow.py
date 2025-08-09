import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain.models import Product
from infrastructure.orm import Base
from infrastructure.repositories import SqlAlchemyProductRepository
from infrastructure.unit_of_work import SqlAlchemyUnitOfWork


class TestSqlAlchemyUnitOfWork:
    """Test SQLAlchemy Unit of Work implementation"""

    @pytest.fixture
    def engine(self):
        """Create in-memory SQLite engine"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        return engine

    @pytest.fixture
    def session_factory(self, engine):
        """Create session factory"""
        return sessionmaker(bind=engine)

    def test_commit_success(self, session_factory):
        """Test successful commit"""
        session = session_factory()

        with SqlAlchemyUnitOfWork(session):
            repo = SqlAlchemyProductRepository(session)
            product = Product(id=None, name="Test Product", quantity=10, price=99.99)
            repo.add(product)
            # Commit happens automatically on context exit

        # Verify product was saved
        new_session = session_factory()
        saved_products = new_session.query(Base.metadata.tables['products']).all()
        assert len(saved_products) == 1
        new_session.close()

    def test_rollback_on_exception(self, session_factory):
        """Test rollback when exception occurs"""
        session = session_factory()

        try:
            with SqlAlchemyUnitOfWork(session):
                repo = SqlAlchemyProductRepository(session)
                product = Product(id=None, name="Test Product", quantity=10, price=99.99)
                repo.add(product)
                raise Exception("Something went wrong")
        except Exception:
            pass

        # Verify product was NOT saved
        new_session = session_factory()
        saved_products = new_session.query(Base.metadata.tables['products']).all()
        assert len(saved_products) == 0
        new_session.close()

    def test_manual_commit(self, session_factory):
        """Test manual commit"""
        session = session_factory()
        uow = SqlAlchemyUnitOfWork(session)

        repo = SqlAlchemyProductRepository(session)
        product = Product(id=None, name="Test Product", quantity=10, price=99.99)
        repo.add(product)

        uow.commit()
        session.close()

        # Verify product was saved
        new_session = session_factory()
        saved_products = new_session.query(Base.metadata.tables['products']).all()
        assert len(saved_products) == 1
        new_session.close()

    def test_manual_rollback(self, session_factory):
        """Test manual rollback"""
        session = session_factory()
        uow = SqlAlchemyUnitOfWork(session)

        repo = SqlAlchemyProductRepository(session)
        product = Product(id=None, name="Test Product", quantity=10, price=99.99)
        repo.add(product)

        uow.rollback()
        session.close()

        # Verify product was NOT saved
        new_session = session_factory()
        saved_products = new_session.query(Base.metadata.tables['products']).all()
        assert len(saved_products) == 0
        new_session.close()

    def test_multiple_operations_in_transaction(self, session_factory):
        """Test multiple operations in single transaction"""
        session = session_factory()

        with SqlAlchemyUnitOfWork(session):
            repo = SqlAlchemyProductRepository(session)

            # Add multiple products
            product1 = Product(id=None, name="Product 1", quantity=10, price=50.00)
            product2 = Product(id=None, name="Product 2", quantity=20, price=75.00)

            repo.add(product1)
            repo.add(product2)
            # Both should be committed together

        # Verify both products were saved
        new_session = session_factory()
        saved_products = new_session.query(Base.metadata.tables['products']).all()
        assert len(saved_products) == 2
        new_session.close()
