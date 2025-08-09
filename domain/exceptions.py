class DomainException(Exception):
    """Base exception for domain errors"""
    pass


class ProductNotFoundError(DomainException):
    """Raised when product is not found"""

    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(f"Product with id {product_id} not found")


class OrderNotFoundError(DomainException):
    """Raised when order is not found"""

    def __init__(self, order_id: int):
        self.order_id = order_id
        super().__init__(f"Order with id {order_id} not found")


class InsufficientStockError(DomainException):
    """Raised when there is not enough product in stock"""

    def __init__(self, product_name: str, requested: int, available: int):
        self.product_name = product_name
        self.requested = requested
        self.available = available
        super().__init__(
            f"Insufficient stock for product '{product_name}': "
            f"requested {requested}, available {available}"
        )


class InvalidPriceError(DomainException):
    """Raised when price is invalid"""

    def __init__(self, price: float):
        self.price = price
        super().__init__(f"Invalid price: {price}. Price must be positive")


class InvalidQuantityError(DomainException):
    """Raised when quantity is invalid"""

    def __init__(self, quantity: int):
        self.quantity = quantity
        super().__init__(f"Invalid quantity: {quantity}. Quantity must be positive")
