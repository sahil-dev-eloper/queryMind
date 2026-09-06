import logging
from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.models.database import DatabaseColumn, DatabaseConnection, DatabaseRelationship, DatabaseSchema, DatabaseTable
from app.services.external_database import ExternalDatabaseError, external_database_manager

logger = logging.getLogger(__name__)


class SchemaIntrospectionService:
    def introspect(self, db: Session, connection: DatabaseConnection) -> dict[str, int]:
        try:
            with external_database_manager.session(connection) as external_session:
                inspector = inspect(external_session.bind)
                schema_names = inspector.get_schema_names()
                snapshots = []
                for schema_name in schema_names:
                    if schema_name.startswith("pg_") or schema_name == "information_schema":
                        continue
                    for table_name in inspector.get_table_names(schema=schema_name):
                        snapshots.append((schema_name, table_name, inspector.get_columns(table_name, schema=schema_name), inspector.get_pk_constraint(table_name, schema=schema_name), inspector.get_foreign_keys(table_name, schema=schema_name)))

            db.query(DatabaseSchema).filter(DatabaseSchema.database_connection_id == connection.id).delete(synchronize_session=False)
            schema_map: dict[str, DatabaseSchema] = {}
            table_map: dict[tuple[str, str], DatabaseTable] = {}
            column_map: dict[tuple[str, str, str], DatabaseColumn] = {}
            for schema_name, table_name, columns, primary_key, foreign_keys in snapshots:
                schema = schema_map.setdefault(schema_name, DatabaseSchema(database_connection_id=connection.id, schema_name=schema_name))
                if schema not in db.new:
                    db.add(schema)
                table = DatabaseTable(schema=schema, table_name=table_name, table_type="table")
                db.add(table)
                table_map[(schema_name, table_name)] = table
                primary_keys = set(primary_key.get("constrained_columns") or [])
                for column in columns:
                    model_column = DatabaseColumn(table=table, column_name=column["name"], data_type=str(column["type"]), nullable=column["nullable"], is_primary_key=column["name"] in primary_keys, default_value=str(column["default"]) if column.get("default") is not None else None)
                    db.add(model_column)
                    column_map[(schema_name, table_name, column["name"])] = model_column
            db.flush()
            relationship_count = 0
            for schema_name, table_name, _, _, foreign_keys in snapshots:
                source_table = table_map[(schema_name, table_name)]
                for foreign_key in foreign_keys:
                    target_schema = foreign_key.get("referred_schema") or schema_name
                    target_table = table_map.get((target_schema, foreign_key["referred_table"]))
                    if target_table is None:
                        continue
                    for source_name, target_name in zip(foreign_key["constrained_columns"], foreign_key["referred_columns"]):
                        source_column = column_map.get((schema_name, table_name, source_name))
                        target_column = column_map.get((target_schema, foreign_key["referred_table"], target_name))
                        if source_column and target_column:
                            db.add(DatabaseRelationship(source_table=source_table, source_column=source_column, target_table=target_table, target_column=target_column, relationship_type="foreign_key"))
                            relationship_count += 1
            db.commit()
            return {"tables": len(table_map), "columns": len(column_map), "relationships": relationship_count}
        except (ExternalDatabaseError, SQLAlchemyError, KeyError) as exc:
            db.rollback()
            logger.exception("Schema introspection failed", extra={"database_id": str(connection.id), "error_type": type(exc).__name__})
            raise ExternalDatabaseError("Unable to introspect the database schema.") from exc


schema_introspection_service = SchemaIntrospectionService()
