from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class ProductORM(Base):
    """ORM model for Product"""
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class OrderORM(Base):
    """ORM model for Order"""
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(50), nullable=False, default='pending')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with items
    items = relationship('OrderItemORM', back_populates='order', cascade='all, delete-orphan')


class OrderItemORM(Base):
    """ORM model for OrderItem"""
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_order = Column(Float, nullable=False)

    # Relationships
    order = relationship('OrderORM', back_populates='items')
    product = relationship('ProductORM')
