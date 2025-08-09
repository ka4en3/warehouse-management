import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain.services import WarehouseService
from infrastructure.orm import Base
from infrastructure.repositories import SqlAlchemyProductRepository, SqlAlchemyOrderRepository
from infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from infrastructure.database import DATABASE_URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(DATABASE_URL, echo=False)
SessionFactory = sessionmaker(bind=engine)

# Create tables
Base.metadata.create_all(engine)


def demo_product_management():
    """Demonstrate product management"""
    logger.info("=== Product Management Demo ===")

    session = SessionFactory()
    product_repo = SqlAlchemyProductRepository(session)
    order_repo = SqlAlchemyOrderRepository(session)
    warehouse_service = WarehouseService(product_repo, order_repo)

    with SqlAlchemyUnitOfWork(session):
        # Create products
        laptop = warehouse_service.create_product("Laptop", 10, 999.99)
        logger.info(f"Created product: {laptop}")

        mouse = warehouse_service.create_product("Mouse", 50, 29.99)
        logger.info(f"Created product: {mouse}")

        keyboard = warehouse_service.create_product("Keyboard", 30, 79.99)
        logger.info(f"Created product: {keyboard}")

        # List all products
        products = warehouse_service.list_products()
        logger.info(f"Total products: {len(products)}")

        # Update product price
        laptop = warehouse_service.update_product_price(laptop.id, 899.99)
        logger.info(f"Updated laptop price to: {laptop.price}")

        # Restock product
        mouse = warehouse_service.restock_product(mouse.id, 20)
        logger.info(f"Restocked mouse, new quantity: {mouse.quantity}")


def demo_order_management():
    """Demonstrate order management"""
    logger.info("\n=== Order Management Demo ===")

    session = SessionFactory()
    product_repo = SqlAlchemyProductRepository(session)
    order_repo = SqlAlchemyOrderRepository(session)
    warehouse_service = WarehouseService(product_repo, order_repo)

    with SqlAlchemyUnitOfWork(session):
        # Get products
        products = warehouse_service.list_products()
        if len(products) < 2:
            logger.error("Not enough products for order demo")
            return

        # Create an order
        order = warehouse_service.create_order([
            (products[0].id, 2),  # 2 laptops
            (products[1].id, 5),  # 5 mice
        ])
        logger.info(f"Created order {order.id} with {order.total_items} items")
        logger.info(f"Order total: ${order.total_price:.2f}")

        # Check updated stock
        laptop = warehouse_service.get_product(products[0].id)
        logger.info(f"Laptop stock after order: {laptop.quantity}")

        # List orders
        orders = warehouse_service.list_orders()
        logger.info(f"Total orders: {len(orders)}")

        # Cancel an order (restores stock)
        cancelled_order = warehouse_service.cancel_order(order.id)
        logger.info(f"Cancelled order {cancelled_order.id}")

        # Check restored stock
        laptop = warehouse_service.get_product(products[0].id)
        logger.info(f"Laptop stock after cancellation: {laptop.quantity}")


def demo_error_handling():
    """Demonstrate error handling"""
    logger.info("\n=== Error Handling Demo ===")

    session = SessionFactory()
    product_repo = SqlAlchemyProductRepository(session)
    order_repo = SqlAlchemyOrderRepository(session)
    warehouse_service = WarehouseService(product_repo, order_repo)

    try:
        with SqlAlchemyUnitOfWork(session):
            # Try to create product with invalid price
            warehouse_service.create_product("Invalid Product", 10, -50)
    except Exception as e:
        logger.error(f"Expected error: {e}")

    try:
        with SqlAlchemyUnitOfWork(session):
            # Try to order more than available
            products = warehouse_service.list_products()
            if products:
                warehouse_service.create_order([
                    (products[0].id, 1000)  # More than available
                ])
    except Exception as e:
        logger.error(f"Expected error: {e}")


def main():
    """Run all demos"""
    try:
        demo_product_management()
        demo_order_management()
        demo_error_handling()
        logger.info("\n=== All demos completed successfully! ===")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
