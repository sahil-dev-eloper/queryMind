import re

import sqlglot
from sqlglot import exp


class SQLValidationError(Exception):
    pass


class SQLValidator:
    forbidden = re.compile(r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE|COMMENT|VACUUM|MERGE|CALL|COPY|DO|EXECUTE|PREPARE|SET)\b", re.IGNORECASE)

    def validate(self, sql: str, schema: dict) -> None:
        if not sql.strip() or "--" in sql or "/*" in sql or self.forbidden.search(sql):
            raise SQLValidationError("Only read-only SELECT queries are allowed.")
        try:
            statements = sqlglot.parse(sql, read="postgres")
        except sqlglot.errors.ParseError as exc:
            raise SQLValidationError("The generated SQL is not valid PostgreSQL.") from exc
        if len(statements) != 1 or not isinstance(statements[0], (exp.Select, exp.Union)):
            raise SQLValidationError("Only one read-only query is allowed.")
        tables = {table["name"].lower() for schema_item in schema.get("schemas", []) for table in schema_item.get("tables", [])}
        columns = {table["name"].lower(): {column["name"].lower() for column in table.get("columns", [])} for schema_item in schema.get("schemas", []) for table in schema_item.get("tables", [])}
        aliases: dict[str, str] = {}
        projection_aliases = {alias.alias.lower() for alias in statements[0].find_all(exp.Alias)}
        for table in statements[0].find_all(exp.Table):
            name = table.name.lower()
            if name not in tables:
                raise SQLValidationError(f"Table '{table.name}' is not in the connected schema.")
            if table.alias:
                aliases[table.alias.lower()] = name
        for column in statements[0].find_all(exp.Column):
            table_name = (column.table or "").lower()
            if table_name:
                table_name = aliases.get(table_name, table_name)
                if table_name not in columns or column.name.lower() not in columns[table_name]:
                    raise SQLValidationError(f"Column '{column.sql(dialect='postgres')}' is not in the connected schema.")
            elif column.name.lower() not in projection_aliases and column.name.lower() != "*" and not any(column.name.lower() in table_columns for table_columns in columns.values()):
                raise SQLValidationError(f"Column '{column.name}' is not in the connected schema.")


sql_validator = SQLValidator()
