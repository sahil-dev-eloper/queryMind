import pytest

from app.services.sql_validator import SQLValidationError, SQLValidator

SCHEMA = {"schemas": [{"name": "public", "tables": [{"name": "customers", "columns": [{"name": "id"}, {"name": "name"}]}]}]}


def test_validator_allows_select() -> None:
    SQLValidator().validate("SELECT name FROM customers", SCHEMA)


@pytest.mark.parametrize("sql", ["DROP TABLE customers", "DELETE FROM customers", "UPDATE customers SET name = 'x'", "SELECT * FROM customers; DROP TABLE customers"])
def test_validator_rejects_unsafe_sql(sql: str) -> None:
    with pytest.raises(SQLValidationError):
        SQLValidator().validate(sql, SCHEMA)


def test_validator_rejects_unknown_column() -> None:
    with pytest.raises(SQLValidationError):
        SQLValidator().validate("SELECT revenue FROM customers", SCHEMA)
