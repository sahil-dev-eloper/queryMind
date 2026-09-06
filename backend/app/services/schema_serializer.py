from sqlalchemy.orm import Session, selectinload

from app.models.database import DatabaseConnection, DatabaseRelationship, DatabaseSchema, DatabaseTable


def serialize_schema(db: Session, connection: DatabaseConnection) -> dict:
    schemas = db.query(DatabaseSchema).options(selectinload(DatabaseSchema.tables).selectinload(DatabaseTable.columns), selectinload(DatabaseSchema.tables).selectinload(DatabaseTable.source_relationships).options(selectinload(DatabaseRelationship.target_table), selectinload(DatabaseRelationship.source_column), selectinload(DatabaseRelationship.target_column))).filter(DatabaseSchema.database_connection_id == connection.id).all()
    serialized_schemas = []
    for schema in schemas:
        tables = []
        for table in schema.tables:
            foreign_keys = {}
            for relationship in table.source_relationships:
                foreign_keys[relationship.source_column.column_name] = f"{relationship.target_table.table_name}.{relationship.target_column.column_name}"
            tables.append({"name": table.table_name, "type": table.table_type, "description": table.description, "columns": [{"name": column.column_name, "type": column.data_type, "nullable": column.nullable, "primary_key": column.is_primary_key, "default_value": column.default_value, "foreign_key": foreign_keys.get(column.column_name)} for column in table.columns]})
        serialized_schemas.append({"name": schema.schema_name, "tables": tables})
    return {"database_id": connection.id, "database": connection.database_name, "dialect": "postgresql", "schemas": serialized_schemas}
