"""module for testing application and database health"""
from sqlalchemy.exc import SQLAlchemyError

from menu_translator.extensions import db
from sqlalchemy import text


def is_live() -> bool:
    """Checks if Flask is running"""
    return True


def check_database_readiness() -> bool:
    """Pings the database to verify connectivity via the connection pool."""
    try:
        with db.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False