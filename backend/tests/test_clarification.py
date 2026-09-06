import pytest

from app.ai.models import Ambiguity, QueryAnalysis
from app.models.database import Clarification
from app.services.clarification import ClarificationError, clarification_answer_processor, clarification_question_generator


SCHEMA = {"schemas": [{"name": "public", "tables": [{"name": "customers", "columns": [{"name": "id"}, {"name": "name"}]}, {"name": "orders", "columns": [{"name": "customer_id"}, {"name": "total_amount"}, {"name": "order_date"}]}]}]}


def test_metric_question_uses_entity_and_schema_supported_options() -> None:
    analysis = QueryAnalysis(intent="customers_ranking", entities=["customers"], is_ambiguous=True, ambiguities=[Ambiguity(field="metric", reason="best is ambiguous")])
    prompt = clarification_question_generator.generate(analysis, SCHEMA, 1)
    assert prompt is not None
    assert prompt.question == 'How should "best customers" be measured?'
    assert [option.value for option in prompt.options] == ["revenue", "order_count", "average_order_value"]


def test_answer_updates_metric() -> None:
    clarification = Clarification(field="metric", question="How?", options=[{"label": "Highest Revenue", "value": "revenue"}])
    analysis = QueryAnalysis(intent="customers_ranking", entities=["customers"], is_ambiguous=True, ambiguities=[Ambiguity(field="metric", reason="best")])
    clarification_answer_processor.process(clarification, "Highest Revenue", analysis)
    assert analysis.metrics[0].name == "revenue"
    assert not analysis.ambiguities


def test_invalid_answer_is_rejected() -> None:
    clarification = Clarification(field="metric", question="How?", options=[{"label": "Highest Revenue", "value": "revenue"}])
    with pytest.raises(ClarificationError):
        clarification_answer_processor.process(clarification, "Something else", QueryAnalysis(intent="customers_ranking"))


def test_question_generator_stops_after_three_rounds() -> None:
    analysis = QueryAnalysis(intent="customers_ranking", entities=["customers"], is_ambiguous=True, ambiguities=[Ambiguity(field="metric", reason="best")])
    assert clarification_question_generator.generate(analysis, SCHEMA, 4) is None
