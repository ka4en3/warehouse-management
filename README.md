# Warehouse Management System

A warehouse management system implemented using Domain-Driven Design (DDD) and Clean Architecture principles.

## Description

This is an educational project demonstrating the application of DDD and Clean Architecture in Python. The system allows you to:
- Manage warehouse products (create, update, delete)
- Create and process orders
- Track product quantities in stock
- Handle business rules and constraints

## Architecture

The project is divided into two main layers:

### Domain Layer (`domain/`)
Contains business logic independent of infrastructure:
- **models.py** - business entities (Product, Order, OrderItem)
- **repositories.py** - repository interfaces
- **services.py** - business services
- **exceptions.py** - domain exceptions
- **unit_of_work.py** - Unit of Work interface

### Infrastructure Layer (`infrastructure/`)
Contains technical implementation:
- **orm.py** - SQLAlchemy models
- **repositories.py** - repository implementations
- **unit_of_work.py** - Unit of Work implementation
- **database.py** - database configuration

## Installation

### Requirements
- Python 3.10+
- UV (package manager)

### Installing UV (Windows)

```powershell
# Using PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or download the installer from https://github.com/astral-sh/uv/releases
```

### Installing Dependencies

```bash
# Clone the repository
git clone https://github.com/ka4en3/warehouse-management.git
cd warehouse

# Create virtual environment and install dependencies
uv venv
# Activate environment (Windows)
.venv\Scripts\activate
# Install dependencies
uv pip install -r requirements.txt
uv pip install -r dev_requirements.txt

# Or using pyproject.toml
uv pip install -e .
uv pip install -e ".[dev]"
```

## Usage

### Running the Example

```bash
python main.py
```

This will run demonstration scenarios:
1. Product management (creation, updating, restocking)
2. Order management (creation, cancellation)
3. Error handling

### Code Examples

#### Creating a Product
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from domain.services import WarehouseService
from infrastructure.repositories import SqlAlchemyProductRepository, SqlAlchemyOrderRepository
from infrastructure.unit_of_work import SqlAlchemyUnitOfWork

# Setup
engine = create_engine("sqlite:///warehouse.db")
Session = sessionmaker(bind=engine)
session = Session()

# Create service
product_repo = SqlAlchemyProductRepository(session)
order_repo = SqlAlchemyOrderRepository(session)
service = WarehouseService(product_repo, order_repo)

# Using with Unit of Work
with SqlAlchemyUnitOfWork(session):
    product = service.create_product(
        name="Laptop",
        quantity=10,
        price=999.99
    )
    print(f"Created: {product}")
```

#### Creating an Order
```python
with SqlAlchemyUnitOfWork(session):
    # Create order with multiple products
    order = service.create_order([
        (1, 2),  # product_id=1, quantity=2
        (2, 5),  # product_id=2, quantity=5
    ])
    print(f"Order total: ${order.total_price}")
```

## Testing

### Running All Tests

```bash
# Simple run
pytest

# With coverage report
pytest --cov=domain --cov=infrastructure --cov-report=html

# Verbose output
pytest -v
```

### Running Specific Tests

```bash
# Only model tests
pytest tests/test_models.py

# Specific test
pytest tests/test_services.py::TestWarehouseService::test_create_product_success
```

### Checking Coverage

After running tests with `--cov-report=html`, open `htmlcov/index.html` in your browser.

## Code Quality

### Running pylint

```bash
# Check entire project
pylint domain infrastructure

# Check specific module
pylint domain/services.py

# Ignore certain warnings (configured in .pylintrc)
pylint --disable=missing-docstring domain/
```

## Project Structure

```
warehouse/
├── domain/                 # Business logic
│   ├── __init__.py
│   ├── models.py          # Business entities
│   ├── repositories.py    # Repository interfaces
│   ├── services.py        # Business services
│   ├── unit_of_work.py    # UoW interface
│   └── exceptions.py      # Business exceptions
├── infrastructure/        # Technical implementation
│   ├── __init__.py
│   ├── database.py       # Database configuration
│   ├── orm.py           # SQLAlchemy models
│   ├── repositories.py  # Repository implementations
│   └── unit_of_work.py  # UoW implementation
├── tests/               # Tests
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_services.py
│   ├── test_repositories.py
│   └── test_unit_of_work.py
├── main.py              # Entry point
├── pyproject.toml       # Project configuration
├── requirements.txt     # Dependencies
├── dev_requirements.txt # Dev dependencies
├── .pylintrc           # Pylint configuration
├── .gitignore         # Git ignore
└── README.md          # Documentation
```

## Business Rules

1. **Products**:
   - Price must be positive
   - Quantity cannot be negative
   - Name cannot be empty
   - Cannot delete a product if it exists in orders

2. **Orders**:
   - Cannot order more product than available in stock
   - Product quantity decreases when order is created
   - Product quantity is restored when order is cancelled
   - Can only cancel orders with status "pending" or "confirmed"
   - Cannot confirm an empty order

## Error Handling

The system uses specialized exceptions:
- `ProductNotFoundError` - product not found
- `OrderNotFoundError` - order not found
- `InsufficientStockError` - insufficient product in stock
- `InvalidPriceError` - invalid price
- `InvalidQuantityError` - invalid quantity

## Future Improvements

Possible enhancements:
- [ ] Add authentication and authorization
- [ ] Implement REST API
- [ ] Add operation logging
- [ ] Implement event sourcing
- [ ] Add caching
- [ ] Implement more complex business rules
- [ ] Add support for multiple warehouses

## License

MIT