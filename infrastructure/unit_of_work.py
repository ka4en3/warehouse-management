from sqlalchemy.orm import Session

from domain.unit_of_work import UnitOfWork


class SqlAlchemyUnitOfWork(UnitOfWork):
    """SQLAlchemy implementation of Unit of Work pattern"""

    def __init__(self, session: Session):
        self.session = session

    def __enter__(self):
        """Enter context manager"""
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Exit context manager - rollback if exception occurred"""
        if exception_type is not None:
            self.rollback()
        else:
            # Auto-commit on successful exit
            self.commit()

        # Close session
        self.session.close()

    def commit(self):
        """Commit all changes"""
        self.session.commit()

    def rollback(self):
        """Rollback all changes"""
        self.session.rollback()
