from app.core.config import settings
from app.services.sql_validator import SQLValidationError, sql_validator


class SQLRepairError(Exception):
    pass


class SQLRepairService:
    def repair(self, sql: str, error: str, schema: dict) -> str:
        if settings.max_sql_repair_attempts < 1:
            raise SQLRepairError("SQL repair is disabled.")
        # Repair remains deliberately conservative: only normalize a common trailing statement issue.
        repaired = sql.strip().rstrip(";") + ";"
        try:
            sql_validator.validate(repaired, schema)
        except SQLValidationError as exc:
            raise SQLRepairError("The generated query could not be repaired safely.") from exc
        return repaired


sql_repair_service = SQLRepairService()
