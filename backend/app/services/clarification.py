from dataclasses import dataclass
from uuid import UUID

from app.ai.models import QueryAnalysis, TimeRange
from app.models.database import Clarification, Conversation

MAX_CLARIFICATION_ROUNDS = 3


@dataclass
class ClarificationOption:
    label: str
    value: str


@dataclass
class ClarificationPrompt:
    field: str
    question: str
    options: list[ClarificationOption]


class ClarificationError(Exception):
    pass


class ClarificationQuestionGenerator:
    def generate(self, analysis: QueryAnalysis, schema: dict, round_number: int) -> ClarificationPrompt | None:
        if round_number > MAX_CLARIFICATION_ROUNDS:
            return None
        fields = {ambiguity.field for ambiguity in analysis.ambiguities}
        if "metric" in fields:
            options = [ClarificationOption("Highest Revenue", "revenue")]
            table_names = {table["name"] for item in schema.get("schemas", []) for table in item.get("tables", [])}
            columns = {column["name"] for item in schema.get("schemas", []) for table in item.get("tables", []) for column in table.get("columns", [])}
            if "orders" in table_names and "total_amount" in columns:
                options.append(ClarificationOption("Most Orders", "order_count"))
            if "orders" in table_names and "total_amount" in columns:
                options.append(ClarificationOption("Highest Average Order Value", "average_order_value"))
            entity = analysis.entities[0] if analysis.entities else "this"
            return ClarificationPrompt("metric", f"How should \"best {entity}\" be measured?", options)
        if "time_range" in fields:
            return ClarificationPrompt("time_range", "What time period should I use?", [ClarificationOption("This Month", "this_month"), ClarificationOption("This Quarter", "this_quarter"), ClarificationOption("This Year", "this_year"), ClarificationOption("All Time", "all_time")])
        if "definition" in fields or "filter" in fields:
            return ClarificationPrompt("definition", "How should this term be defined using the available data?", [])
        return None


class ClarificationAnswerProcessor:
    def process(self, clarification: Clarification, answer: str, analysis: QueryAnalysis) -> QueryAnalysis:
        normalized = answer.strip().lower().replace(" ", "_")
        allowed = {str(option["value"]).lower(): str(option["value"]) for option in clarification.options}
        if normalized not in allowed:
            aliases = {"revenue": "revenue", "highest_revenue": "revenue", "most_orders": "order_count", "this_year": "this_year", "this_month": "this_month", "this_quarter": "this_quarter", "all_time": "all_time"}
            normalized = aliases.get(normalized, "")
        if normalized not in allowed and normalized not in {"revenue", "order_count", "average_order_value", "this_year", "this_month", "this_quarter", "all_time"}:
            raise ClarificationError("That answer does not match one of the available options.")
        if clarification.field == "metric":
            from app.ai.models import Metric
            analysis.metrics = [Metric(name=normalized, definition="sum of order total amount" if normalized == "revenue" else normalized.replace("_", " "))]
            analysis.ambiguities = [item for item in analysis.ambiguities if item.field != "metric"]
            analysis.sort = analysis.sort.model_copy(update={"field": normalized}) if analysis.sort else None
        elif clarification.field == "time_range":
            if normalized == "this_year":
                analysis.time_range = TimeRange(type="calendar_year", year=__import__("datetime").date.today().year)
            elif normalized == "all_time":
                analysis.time_range = TimeRange(type="all_time")
            else:
                analysis.time_range = TimeRange(type=normalized)
            analysis.ambiguities = [item for item in analysis.ambiguities if item.field != "time_range"]
        clarification.answer = answer
        clarification.status = "answered"
        return analysis


clarification_question_generator = ClarificationQuestionGenerator()
clarification_answer_processor = ClarificationAnswerProcessor()
