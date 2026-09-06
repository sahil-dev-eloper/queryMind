from uuid import UUID
import re

from sqlalchemy.orm import Session

from app.models.database import DatabaseSchema, DatabaseTable


class SchemaRetriever:
    def retrieve(self, db: Session, database_id: str, query: str) -> list[dict]:
        terms = {re.sub(r"[^a-z0-9_]", "", term.lower()).rstrip("s") for term in query.split() if len(term) > 2}
        connection_id = UUID(database_id) if isinstance(database_id, str) else database_id
        tables = db.query(DatabaseTable).join(DatabaseSchema, DatabaseTable.database_schema_id == DatabaseSchema.id).filter(DatabaseSchema.database_connection_id == connection_id).all()
        ranked = []
        for table in tables:
            table_term = re.sub(r"[^a-z0-9_]", "", table.table_name.lower()).rstrip("s")
            score = 3 if table_term in terms or any(term in table_term for term in terms) else 0
            matching_columns = [column.column_name for column in table.columns if re.sub(r"[^a-z0-9_]", "", column.column_name.lower()).rstrip("s") in terms or any(term in column.column_name.lower() for term in terms)]
            score += len(matching_columns) * 2
            if score:
                ranked.append((score, table, matching_columns))

        selected_tables = {table.id for _, table, _ in ranked}
        pending_tables = [table for _, table, _ in ranked]
        while pending_tables:
            table = pending_tables.pop(0)
            for relationship in [*table.source_relationships, *table.target_relationships]:
                neighbor = relationship.target_table if relationship.source_table_id == table.id else relationship.source_table
                if neighbor.id not in selected_tables:
                    ranked.append((1, neighbor, []))
                    selected_tables.add(neighbor.id)
                    pending_tables.append(neighbor)

        return [{"table": table.table_name, "score": score, "columns": columns} for score, table, columns in sorted(ranked, key=lambda item: item[0], reverse=True)]


schema_retriever = SchemaRetriever()
