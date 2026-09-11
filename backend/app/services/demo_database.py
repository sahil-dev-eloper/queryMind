import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.database import ConnectionStatus, DatabaseConnection
from app.services.credentials import credential_service
from app.services.external_database import external_database_manager
from app.services.schema_introspection import schema_introspection_service

logger = logging.getLogger(__name__)


def ensure_demo_database(db: Session) -> DatabaseConnection | None:
    """Ensures a shared demo database connection exists and is introspected."""
    try:
        connection = (
            db.query(DatabaseConnection)
            .filter(DatabaseConnection.user_id.is_(None))
            .first()
        )

        if connection is None:
            connection = DatabaseConnection(
                user_id=None,
                name=settings.demo_database_name,
                host=settings.demo_database_host,
                port=settings.demo_database_port,
                database_name=settings.demo_database_db,
                username=settings.demo_database_user,
                encrypted_password=credential_service.encrypt(settings.demo_database_password),
                ssl_mode=settings.demo_database_ssl_mode,
                connection_status=ConnectionStatus.UNTESTED.value,
            )
            db.add(connection)
            db.commit()
            db.refresh(connection)
            logger.info("Created shared demo database connection: %s", connection.id)

        # If not connected or schemas not yet introspected, try to connect and introspect
        if connection.connection_status != ConnectionStatus.CONNECTED.value or not connection.schemas:
            try:
                success = external_database_manager.test_connection(connection)
                if success:
                    connection.connection_status = ConnectionStatus.CONNECTED.value
                    connection.last_tested_at = datetime.now(timezone.utc)
                    db.commit()
                    schema_introspection_service.introspect(db, connection)
                    logger.info("Successfully introspected shared demo database schema.")
            except Exception:
                logger.warning("Could not connect/introspect shared demo database.", exc_info=True)

        return connection
    except Exception:
        logger.exception("Failed in ensure_demo_database")
        return None
