import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.database import ConnectionStatus, DatabaseConnection
from app.models.user import User
from app.schemas.databases import ConnectionTestResponse, DatabaseConnectionInput, DatabaseConnectionResponse, IntrospectionResponse
from app.services.credentials import credential_service
from app.services.demo_database import ensure_demo_database
from app.services.external_database import external_database_manager, ExternalDatabaseError
from app.services.schema_introspection import schema_introspection_service
from app.services.schema_serializer import serialize_schema

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/databases", tags=["databases"])


def get_connection(database_id: UUID, db: Session, user: User) -> DatabaseConnection:
    connection = db.get(DatabaseConnection, database_id)
    if connection is None or (connection.user_id is not None and connection.user_id != user.id):
        raise HTTPException(status_code=404, detail="Database connection not found.")
    return connection


def public_response(connection: DatabaseConnection) -> DatabaseConnectionResponse:
    return DatabaseConnectionResponse.model_validate(connection)


def test_and_update(db: Session, connection: DatabaseConnection) -> bool:
    success = external_database_manager.test_connection(connection)
    connection.connection_status = ConnectionStatus.CONNECTED.value if success else ConnectionStatus.FAILED.value
    connection.last_tested_at = datetime.now(timezone.utc)
    db.commit()
    return success


@router.post("/test", response_model=ConnectionTestResponse)
def test_new_connection(payload: DatabaseConnectionInput, user: User = Depends(get_current_user)) -> ConnectionTestResponse:
    transient = DatabaseConnection(name=payload.name, host=payload.host, port=payload.port, database_name=payload.database_name, username=payload.username, encrypted_password=credential_service.encrypt(payload.password), ssl_mode=payload.ssl_mode)
    try:
        success = external_database_manager.test_connection(transient)
    except Exception:
        logger.exception("External database test failed")
        success = False
    return ConnectionTestResponse(success=success, message="Database connection successful." if success else "Unable to connect to the database.")


@router.post("", response_model=DatabaseConnectionResponse, status_code=status.HTTP_201_CREATED)
def create_database(payload: DatabaseConnectionInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> DatabaseConnectionResponse:
    connection = DatabaseConnection(user_id=user.id, name=payload.name, host=payload.host, port=payload.port, database_name=payload.database_name, username=payload.username, encrypted_password=credential_service.encrypt(payload.password), ssl_mode=payload.ssl_mode)
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return public_response(connection)


@router.get("", response_model=list[DatabaseConnectionResponse])
def list_databases(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[DatabaseConnectionResponse]:
    ensure_demo_database(db)
    connections = (
        db.query(DatabaseConnection)
        .filter((DatabaseConnection.user_id == user.id) | (DatabaseConnection.user_id.is_(None)))
        .order_by(DatabaseConnection.created_at.desc())
        .all()
    )
    return [public_response(connection) for connection in connections]


@router.get("/{database_id}", response_model=DatabaseConnectionResponse)
def get_database(database_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> DatabaseConnectionResponse:
    return public_response(get_connection(database_id, db, user))


@router.delete("/{database_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_database(database_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> None:
    connection = get_connection(database_id, db, user)
    if connection.user_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The shared demo database cannot be deleted.")
    db.delete(connection)
    db.commit()


@router.post("/{database_id}/test", response_model=ConnectionTestResponse)
def test_saved_connection(database_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ConnectionTestResponse:
    connection = get_connection(database_id, db, user)
    success = test_and_update(db, connection)
    return ConnectionTestResponse(success=success, message="Database connection successful." if success else "Unable to connect to the database.")


@router.post("/{database_id}/introspect", response_model=IntrospectionResponse)
def introspect_database(database_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> IntrospectionResponse:
    connection = get_connection(database_id, db, user)
    try:
        summary = schema_introspection_service.introspect(db, connection)
        connection.connection_status = ConnectionStatus.CONNECTED.value
        connection.last_tested_at = datetime.now(timezone.utc)
        db.commit()
        return IntrospectionResponse(success=True, **summary)
    except ExternalDatabaseError as exc:
        connection.connection_status = ConnectionStatus.FAILED.value
        db.commit()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{database_id}/schema")
def get_schema(database_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    return serialize_schema(db, get_connection(database_id, db, user))
