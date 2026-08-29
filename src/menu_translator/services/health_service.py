from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

from menu_translator.extensions import db
from sqlalchemy import text


def is_live() -> bool:
    return True


def check_database_readiness() -> bool:
    """Pings the database to verify connectivity via the connection pool."""
    try:
        with db.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False