from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from domain.models import Order, Product, OrderItem
from domain.repositories import ProductRepository, OrderRepository
from .orm import ProductORM, OrderORM, OrderItemORM


class SqlAlchemyProductRepository(ProductRepository):
    """SQLAlchemy implementation of ProductRepository"""

    def __init__(self, session: Session):
        self.session = session

    def add(self, product: Product) -> Product:
        """Add a new product"""
        product_orm = ProductORM(
            name=product.name,
            quantity=product.quantity,
            price=product.price,
        )
        self.session.add(product_orm)
        self.session.flush()  # Get the ID without committing

        product.id = product_orm.id
        return product

    def get(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        product_orm = self.session.query(ProductORM).filter_by(id=product_id).first()
        if not product_orm:
            return None

        return self._to_domain(product_orm)

    def get_by_name(self, name: str) -> Optional[Product]:
        """Get product by name"""
        product_orm = self.session.query(ProductORM).filter_by(name=name).first()
        if not product_orm:
            return None

        return self._to_domain(product_orm)

    def list(self) -> List[Product]:
        """List all products"""
        products_orm = self.session.query(ProductORM).all()
        return [self._to_domain(p) for p in products_orm]

    def update(self, product: Product) -> Product:
        """Update existing product"""
        product_orm = self.session.query(ProductORM).filter_by(id=product.id).first()
        if not product_orm:
            raise ValueError(f"Product with id {product.id} not found")

        product_orm.name = product.name
        product_orm.quantity = product.quantity
        product_orm.price = product.price

        self.session.flush()
        return product

    def delete(self, product_id: int) -> bool:
        """Delete product by ID"""
        product_orm = self.session.query(ProductORM).filter_by(id=product_id).first()
        if not product_orm:
            return False

        self.session.delete(product_orm)
        self.session.flush()
        return True

    def list_in_stock(self) -> List[Product]:
        """List all products that are in stock"""
        products_orm = self.session.query(ProductORM).filter(ProductORM.quantity > 0).all()
        return [self._to_domain(p) for p in products_orm]

    def _to_domain(self, product_orm: ProductORM) -> Product:
        """Convert ORM model to domain model"""
        return Product(
            id=product_orm.id,
            name=product_orm.name,
            quantity=product_orm.quantity,
            price=product_orm.price
        )


class SqlAlchemyOrderRepository(OrderRepository):
    """SQLAlchemy implementation of OrderRepository"""

    def __init__(self, session: Session):
        self.session = session

    def add(self, order: Order) -> Order:
        """Add a new order"""
        order_orm = OrderORM(
            status=order.status,
            created_at=order.created_at
        )

        # Add order items
        for item in order.items:
            item_orm = OrderItemORM(
                product_id=item.product.id,
                quantity=item.quantity,
                price_at_order=item.price_at_order
            )
            order_orm.items.append(item_orm)

        self.session.add(order_orm)
        self.session.flush()

        order.id = order_orm.id
        return order

    def get(self, order_id: int) -> Optional[Order]:
        """Get order by ID with all items"""
        order_orm = (
            self.session.query(OrderORM)
            .options(joinedload(OrderORM.items).joinedload(OrderItemORM.product))
            .filter_by(id=order_id)
            .first()
        )

        if not order_orm:
            return None

        return self._to_domain(order_orm)

    def list(self) -> List[Order]:
        """List all orders"""
        orders_orm = (
            self.session.query(OrderORM)
            .options(joinedload(OrderORM.items).joinedload(OrderItemORM.product))
            .all()
        )
        return [self._to_domain(o) for o in orders_orm]

    def update(self, order: Order) -> Order:
        """Update existing order"""
        order_orm = self.session.query(OrderORM).filter_by(id=order.id).first()
        if not order_orm:
            raise ValueError(f"Order with id {order.id} not found")

        order_orm.status = order.status

        # items updates are not implemented yet

        self.session.flush()
        return order

    def list_by_status(self, status: str) -> List[Order]:
        """List orders by status"""
        orders_orm = (
            self.session.query(OrderORM)
            .options(joinedload(OrderORM.items).joinedload(OrderItemORM.product))
            .filter_by(status=status)
            .all()
        )
        return [self._to_domain(o) for o in orders_orm]

    def delete(self, order_id: int) -> bool:
        """Delete order by ID"""
        order_orm = self.session.query(OrderORM).filter_by(id=order_id).first()
        if not order_orm:
            return False

        self.session.delete(order_orm)
        self.session.flush()
        return True

    def _to_domain(self, order_orm: OrderORM) -> Order:
        """Convert ORM model to domain model"""
        order = Order(
            id=order_orm.id,
            created_at=order_orm.created_at,
            status=order_orm.status
        )

        # Convert items
        order.items = []
        for item_orm in order_orm.items:
            product = Product(
                id=item_orm.product.id,
                name=item_orm.product.name,
                quantity=item_orm.product.quantity,
                price=item_orm.product.price
            )
            order_item = OrderItem(
                product=product,
                quantity=item_orm.quantity,
                price_at_order=item_orm.price_at_order
            )
            order.items.append(order_item)

        return order
