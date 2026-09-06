import logging
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.database import DatabaseConnection
from app.services.credentials import credential_service

logger = logging.getLogger(__name__)


class ExternalDatabaseError(Exception):
    pass


class ExternalDatabaseManager:
    def _url(self, connection: DatabaseConnection) -> URL:
        return URL.create(
            "postgresql+psycopg",
            username=connection.username,
            password=credential_service.decrypt(connection.encrypted_password),
            host=connection.host,
            port=connection.port,
            database=connection.database_name,
            query={"sslmode": connection.ssl_mode},
        )

    def _engine(self, connection: DatabaseConnection):
        return create_engine(self._url(connection), pool_pre_ping=True, pool_recycle=300, connect_args={"connect_timeout": 5})

    def test_connection(self, connection: DatabaseConnection) -> bool:
        try:
            with self._engine(connection).connect() as db_connection:
                db_connection.execute(text("SELECT 1"))
            return True
        except (SQLAlchemyError, ValueError) as exc:
            logger.warning("External database connection failed", extra={"database_id": str(connection.id), "error_type": type(exc).__name__})
            return False

    @contextmanager
    def session(self, connection: DatabaseConnection) -> Iterator[Session]:
        engine = self._engine(connection)
        try:
            with Session(engine) as session:
                yield session
        except (SQLAlchemyError, ValueError) as exc:
            logger.warning("External database operation failed", extra={"database_id": str(connection.id), "error_type": type(exc).__name__})
            raise ExternalDatabaseError("Unable to communicate with the database.") from exc
        finally:
            engine.dispose()


external_database_manager = ExternalDatabaseManager()
