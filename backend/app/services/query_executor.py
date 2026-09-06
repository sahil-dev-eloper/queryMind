import time
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.models.database import DatabaseConnection
from app.services.external_database import ExternalDatabaseError, external_database_manager
from app.services.sql_validator import SQLValidationError, sql_validator
from app.services.error_classification import QueryErrorCategory, classify_database_error


class QueryExecutionError(Exception):
    def __init__(self, message: str, category: QueryErrorCategory = QueryErrorCategory.UNKNOWN_DATABASE_ERROR) -> None:
        super().__init__(message)
        self.category = category


def json_value(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


class QueryExecutor:
    def execute(self, connection: DatabaseConnection, sql: str, schema: dict) -> dict:
        sql_validator.validate(sql, schema)
        started = time.perf_counter()
        try:
            with external_database_manager.session(connection) as session:
                timeout_ms = max(1, settings.query_timeout_seconds * 1000)
                session.execute(text(f"SET statement_timeout = {timeout_ms}"))
                result = session.execute(text(sql))
                columns = list(result.keys())
                rows = [list(map(json_value, row)) for row in result.fetchmany(settings.max_query_rows)]
            return {"columns": columns, "rows": rows, "row_count": len(rows), "execution_time_ms": int((time.perf_counter() - started) * 1000)}
        except SQLValidationError as exc:
            raise QueryExecutionError(str(exc), QueryErrorCategory.SAFETY_VIOLATION) from exc
        except ExternalDatabaseError as exc:
            raise QueryExecutionError(str(exc), QueryErrorCategory.CONNECTION_ERROR) from exc
        except SQLAlchemyError as exc:
            raise QueryExecutionError("The query could not be executed.", classify_database_error(exc)) from exc


query_executor = QueryExecutor()
