import asyncio

from app.ai.mock_provider import MockAIProvider


SCHEMA = {"schemas": [{"name": "public", "tables": [{"name": "customers", "columns": [{"name": "id"}, {"name": "name"}]}, {"name": "orders", "columns": [{"name": "customer_id"}, {"name": "total_amount"}, {"name": "order_date"}]}]}]}


def test_mock_provider_analyzes_customer_revenue() -> None:
    analysis = asyncio.run(MockAIProvider().analyze_query("Show the top 10 customers by revenue this year.", SCHEMA, "postgresql"))
    assert analysis.intent == "customer_revenue"
    assert analysis.metrics[0].name == "revenue"
    assert analysis.time_range is not None
    assert analysis.time_range.year is not None
    assert analysis.limit == 10


def test_mock_provider_marks_best_as_ambiguous() -> None:
    analysis = asyncio.run(MockAIProvider().analyze_query("Show me the best products.", SCHEMA, "postgresql"))
    assert analysis.is_ambiguous is True
    assert analysis.ambiguities


def test_mock_provider_generates_read_only_sql() -> None:
    provider = MockAIProvider()
    analysis = asyncio.run(provider.analyze_query("Show monthly revenue for 2026.", SCHEMA, "postgresql"))
    generated = asyncio.run(provider.generate_sql("Show monthly revenue for 2026.", analysis, SCHEMA, "postgresql"))
    assert generated.tables_used == ["orders"]
    assert generated.sql.startswith("SELECT")
