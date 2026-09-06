from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class Metric(BaseModel):
    name: str
    definition: str
    expression_hint: str | None = None


class TimeRange(BaseModel):
    type: str
    year: int | None = None
    start: str | None = None
    end: str | None = None


class SortSpec(BaseModel):
    field: str
    direction: Literal["asc", "desc"] = "desc"


class Ambiguity(BaseModel):
    field: str
    reason: str


class QueryAnalysis(BaseModel):
    is_answerable: bool = True
    rejection_reason: str | None = None
    intent: str = "general_query"
    entities: list[str] = Field(default_factory=list)
    metrics: list[Metric] = Field(default_factory=list)
    dimensions: list[str] = Field(default_factory=list)
    filters: list[dict] = Field(default_factory=list)
    time_range: TimeRange | None = None
    sort: SortSpec | None = None
    limit: int | None = None
    is_ambiguous: bool = False
    ambiguities: list[Ambiguity] = Field(default_factory=list)

    @field_validator("entities", mode="before")
    @classmethod
    def _normalize_entities(cls, v: Any) -> list[str]:
        if not isinstance(v, list):
            return v
        return [item["name"] if isinstance(item, dict) and "name" in item else str(item) for item in v]

    @field_validator("dimensions", mode="before")
    @classmethod
    def _normalize_dimensions(cls, v: Any) -> list[str]:
        if not isinstance(v, list):
            return v
        return [item["name"] if isinstance(item, dict) and "name" in item else str(item) for item in v]

    @field_validator("filters", mode="before")
    @classmethod
    def _normalize_filters(cls, v: Any) -> list[dict]:
        if not isinstance(v, list):
            return []
        return [item for item in v if isinstance(item, dict)]

    @field_validator("metrics", mode="before")
    @classmethod
    def _normalize_metrics(cls, v: Any) -> list:
        if not isinstance(v, list):
            return []
        return [item for item in v if isinstance(item, dict)]


class SQLGenerationResult(BaseModel):
    sql: str
    explanation: str
    tables_used: list[str] = Field(default_factory=list)

    @field_validator("tables_used", mode="before")
    @classmethod
    def _normalize_tables(cls, v: Any) -> list[str]:
        if not isinstance(v, list):
            return v
        return [item["name"] if isinstance(item, dict) and "name" in item else str(item) for item in v]


class AIUsage(BaseModel):
    model: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: int | None = None
