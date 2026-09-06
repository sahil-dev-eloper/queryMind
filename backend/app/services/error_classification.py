from enum import Enum

from sqlalchemy.exc import DBAPIError, OperationalError, ProgrammingError


class QueryErrorCategory(str, Enum):
    SYNTAX_ERROR = "SYNTAX_ERROR"
    UNKNOWN_TABLE = "UNKNOWN_TABLE"
    UNKNOWN_COLUMN = "UNKNOWN_COLUMN"
    INVALID_JOIN = "INVALID_JOIN"
    INVALID_AGGREGATION = "INVALID_AGGREGATION"
    PERMISSION_ERROR = "PERMISSION_ERROR"
    TIMEOUT = "TIMEOUT"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    SAFETY_VIOLATION = "SAFETY_VIOLATION"
    UNKNOWN_DATABASE_ERROR = "UNKNOWN_DATABASE_ERROR"


def classify_database_error(error: Exception) -> QueryErrorCategory:
    message = str(error).lower()
    if "timeout" in message or "canceling statement" in message:
        return QueryErrorCategory.TIMEOUT
    if "permission" in message or "denied" in message:
        return QueryErrorCategory.PERMISSION_ERROR
    if "does not exist" in message and "column" in message:
        return QueryErrorCategory.UNKNOWN_COLUMN
    if "does not exist" in message or "relation" in message:
        return QueryErrorCategory.UNKNOWN_TABLE
    if isinstance(error, (OperationalError, ConnectionError)):
        return QueryErrorCategory.CONNECTION_ERROR
    if isinstance(error, (ProgrammingError, DBAPIError)):
        return QueryErrorCategory.SYNTAX_ERROR
    return QueryErrorCategory.UNKNOWN_DATABASE_ERROR
