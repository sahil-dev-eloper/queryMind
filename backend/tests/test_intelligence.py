from decimal import Decimal

import pytest

from app.services.error_classification import QueryErrorCategory, classify_database_error
from app.services.intent_modifier import intent_modifier
from app.services.result_analyzer import result_analyzer
from app.services.sql_validator import SQLValidationError, sql_validator
from app.ai.models import QueryAnalysis, TimeRange


def test_result_analyzer_recommends_line_chart() -> None:
    result = result_analyzer.analyze(["month", "revenue"], [["2026-01-01", Decimal("12")], ["2026-02-01", Decimal("15")]])
    assert result["visualization"] == {"type": "LINE", "x": "month", "y": "revenue"}
    assert result["numeric_columns"] == ["revenue"]


def test_result_analyzer_handles_empty_results() -> None:
    result = result_analyzer.analyze(["name", "revenue"], [])
    assert result["summary"] == "No results found."
    assert result["visualization"]["type"] == "TABLE"


def test_follow_up_changes_limit_and_time() -> None:
    analysis = QueryAnalysis(intent="customer_revenue", limit=10, time_range=TimeRange(type="calendar_year", year=2026))
    intent_modifier.apply(analysis, "Make that top 20")
    assert analysis.limit == 20
    intent_modifier.apply(analysis, "What about last year?")
    assert analysis.time_range.year == 2025


@pytest.mark.parametrize("sql", ["SELECT * FROM customers -- DROP TABLE customers", "SELECT * FROM customers; DROP TABLE customers"])
def test_validator_rejects_comments_and_multiple_statements(sql: str) -> None:
    with pytest.raises(SQLValidationError):
        sql_validator.validate(sql, {"schemas": [{"tables": [{"name": "customers", "columns": []}]}]})


def test_error_classifier_categories_timeout() -> None:
    assert classify_database_error(Exception("canceling statement due to statement timeout")) == QueryErrorCategory.TIMEOUT
